import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

# Feature engineering for inference
FEATURE_COLUMNS = [
    "days_since_last_login",
    "session_count_30d",
    "session_count_90d",
    "avg_sessions_per_week",
    "total_revenue",
    "avg_order_value",
    "avg_session_duration",
    "search_count_30d",
    "cart_abandon_rate",
    "is_mobile",
    "channel_encoded"
]

CHANNEL_MAP = {ch: i for i, ch in enumerate(["organic", "paid_social", "referral", "email", "affiliate"])}


class ChurnPredictor:
    """
    Production churn prediction service.
    Churn definition: No activity (session_start or purchase) in last 30 days.
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.getenv(
            "CHURN_MODEL_PATH", 
            "app/ml/artifacts/churn_xgb_v1.joblib"
        )
        self.model = None
        self._load_model()
    
    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"✅ Loaded churn model from {self.model_path}")
        else:
            print(f"⚠️ Model not found at {self.model_path}. Predictions will fail.")
    
    def _fetch_user_features(self, db: Session, user_ids: List[int] = None) -> pd.DataFrame:
        """Aggregate user features from events table."""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        user_filter = ""
        params = {"cutoff": cutoff_date}
        
        if user_ids:
            user_filter = "AND e.user_id = ANY(:user_ids)"
            params["user_ids"] = user_ids
        
        query = text(f"""
            SELECT
                u.user_id,
                u.acquisition_channel,
                u.device_type,
                u.signup_date,
                MAX(e.timestamp) as last_activity,
                COUNT(DISTINCT CASE WHEN e.timestamp >= NOW() - INTERVAL '30 days' 
                    THEN e.session_id END) as session_count_30d,
                COUNT(DISTINCT CASE WHEN e.timestamp >= NOW() - INTERVAL '90 days' 
                    THEN e.session_id END) as session_count_90d,
                COALESCE(SUM(CASE WHEN e.event_type = 'purchase' THEN e.revenue END), 0) as total_revenue,
                COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) as order_count,
                AVG(CASE WHEN e.event_type = 'session_start' THEN 
                    EXTRACT(EPOCH FROM (LEAD(e.timestamp) OVER (PARTITION BY e.session_id ORDER BY e.timestamp) - e.timestamp))
                END) as avg_session_duration,
                COUNT(CASE WHEN e.event_type = 'search' AND e.timestamp >= NOW() - INTERVAL '30 days' THEN 1 END) as search_count_30d,
                COUNT(CASE WHEN e.event_type = 'add_to_cart' AND e.timestamp >= NOW() - INTERVAL '30 days' THEN 1 END) as cart_add_count,
                COUNT(CASE WHEN e.event_type = 'checkout' AND e.timestamp >= NOW() - INTERVAL '30 days' THEN 1 END) as checkout_count
            FROM users u
            LEFT JOIN events e ON u.user_id = e.user_id AND e.timestamp >= :cutoff
            WHERE 1=1 {user_filter}
            GROUP BY u.user_id, u.acquisition_channel, u.device_type, u.signup_date
        """)
        
        result = db.execute(query, params).mappings().all()
        return pd.DataFrame([dict(r) for r in result])
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform raw aggregates into model features."""
        now = pd.Timestamp.now()
        df["last_activity"] = pd.to_datetime(df["last_activity"])
        df["signup_date"] = pd.to_datetime(df["signup_date"])
        
        features = pd.DataFrame()
        features["days_since_last_login"] = (now - df["last_activity"]).dt.days.fillna(999)
        features["session_count_30d"] = df["session_count_30d"].fillna(0)
        features["session_count_90d"] = df["session_count_90d"].fillna(0)
        features["avg_sessions_per_week"] = features["session_count_90d"] / 13
        features["total_revenue"] = df["total_revenue"].fillna(0)
        features["avg_order_value"] = features["total_revenue"] / df["order_count"].clip(lower=1)
        features["avg_session_duration"] = df["avg_session_duration"].fillna(0)
        features["search_count_30d"] = df["search_count_30d"].fillna(0)
        features["cart_abandon_rate"] = 1 - (df["checkout_count"].fillna(0) / df["cart_add_count"].clip(lower=1))
        features["is_mobile"] = (df["device_type"] != "web").astype(int)
        features["channel_encoded"] = df["acquisition_channel"].map(CHANNEL_MAP).fillna(0)
        
        return features[FEATURE_COLUMNS]
    
    def predict(self, db: Session, user_ids: List[int] = None) -> List[Dict]:
        """
        Predict churn probability for users.
        Returns sorted list by risk score (highest first).
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        raw_df = self._fetch_user_features(db, user_ids)
        if raw_df.empty:
            return []
        
        features = self._engineer_features(raw_df)
        probabilities = self.model.predict_proba(features)[:, 1]
        
        results = []
        for idx, row in raw_df.iterrows():
            prob = probabilities[idx]
            risk_level = "high" if prob > 0.7 else "medium" if prob > 0.4 else "low"
            
            results.append({
                "user_id": int(row["user_id"]),
                "churn_probability": round(float(prob), 4),
                "risk_level": risk_level,
                "days_since_last_login": int(features.iloc[idx]["days_since_last_login"]),
                "total_revenue": float(row["total_revenue"]),
                "last_activity": row["last_activity"].isoformat() if pd.notna(row["last_activity"]) else None,
                "key_features": {
                    "sessions_30d": int(features.iloc[idx]["session_count_30d"]),
                    "avg_session_duration": round(float(features.iloc[idx]["avg_session_duration"]), 1),
                    "cart_abandon_rate": round(float(features.iloc[idx]["cart_abandon_rate"]), 2)
                }
            })
        
        return sorted(results, key=lambda x: x["churn_probability"], reverse=True)
    
    def predict_single(self, db: Session, user_id: int) -> Dict:
        """Predict churn for a single user."""
        results = self.predict(db, [user_id])
        return results[0] if results else {"error": "User not found"}


# Singleton instance
_predictor_instance = None

def get_predictor() -> ChurnPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = ChurnPredictor()
    return _predictor_instance

def load_model(path: str = None):
    """Called at FastAPI startup."""
    global _predictor_instance
    _predictor_instance = ChurnPredictor(path)
    return _predictor_instance