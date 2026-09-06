import json

import joblib
import numpy as np
import pandas as pd

from app.ml.artifact_store import download_latest
from app.ml.features import FEATURES


def load_model():
    return joblib.load(download_latest("churn_model.joblib"))


def load_metadata() -> dict:
    path = download_latest("model_metadata.json")
    return json.loads(path.read_text(encoding="utf-8"))


def predict_scores(model, frame: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(frame[FEATURES])[:, 1]


def risk_band(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def reason_codes(row: pd.Series) -> list[str]:
    pairs = []
    if row.get("days_since_last_activity", 0) >= 20:
        pairs.append("Long inactivity gap")
    if row.get("sessions_30d", 0) <= 1:
        pairs.append("Very low recent session frequency")
    if row.get("carts_30d", 0) > 0 and row.get("checkouts_30d", 0) == 0:
        pairs.append("Recent cart abandonment")
    if row.get("purchases_90d", 0) == 0:
        pairs.append("No purchase in 90 days")
    if row.get("searches_30d", 0) == 0:
        pairs.append("No recent search activity")
    return pairs[:3] or ["Broad engagement decline"]
