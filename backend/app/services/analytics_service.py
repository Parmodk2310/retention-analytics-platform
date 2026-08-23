from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from pydantic import BaseModel

from app.db.models import User, Event


class CohortRetentionRow(BaseModel):
    cohort_month: str
    period_month: int
    cohort_size: int
    retained_users: int
    retention_rate: float


class FunnelStage(BaseModel):
    stage: str
    users: int
    drop_off: int
    conversion_rate: float


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dau_wau_mau(self, date: Optional[datetime] = None) -> Dict:
        """Calculate DAU, WAU, MAU and stickiness ratio."""
        if date is None:
            date = datetime.utcnow()
        
        dau_date = date.date()
        wau_start = (date - timedelta(days=7)).date()
        mau_start = (date - timedelta(days=30)).date()
        
        query = text("""
            SELECT
                COUNT(DISTINCT CASE WHEN DATE(timestamp) = :dau_date THEN user_id END) as dau,
                COUNT(DISTINCT CASE WHEN DATE(timestamp) >= :wau_start THEN user_id END) as wau,
                COUNT(DISTINCT CASE WHEN DATE(timestamp) >= :mau_start THEN user_id END) as mau
            FROM events
            WHERE timestamp >= :mau_start
        """)
        
        result = self.db.execute(query, {
            "dau_date": dau_date,
            "wau_start": wau_start,
            "mau_start": mau_start
        }).mappings().fetchone()
        
        dau = result["dau"] or 0
        mau = result["mau"] or 1  # Avoid div by zero
        
        return {
            "dau": dau,
            "wau": result["wau"] or 0,
            "mau": mau,
            "stickiness": round(dau / mau, 4),
            "date": dau_date.isoformat()
        }

    def get_funnel_analysis(self, start_date: datetime, end_date: datetime) -> List[FunnelStage]:
        """6-stage conversion funnel with drop-off rates."""
        query = text("""
            WITH user_funnel AS (
                SELECT
                    user_id,
                    MAX(CASE WHEN event_type = 'session_start' THEN 1 ELSE 0 END) as visited,
                    MAX(CASE WHEN event_type = 'signup' THEN 1 ELSE 0 END) as signed_up,
                    MAX(CASE WHEN event_type = 'search' THEN 1 ELSE 0 END) as searched,
                    MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as added_to_cart,
                    MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) as checked_out,
                    MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchased
                FROM events
                WHERE timestamp BETWEEN :start AND :end
                GROUP BY user_id
            )
            SELECT
                SUM(visited) as visited,
                SUM(signed_up) as signed_up,
                SUM(searched) as searched,
                SUM(added_to_cart) as added_to_cart,
                SUM(checked_out) as checked_out,
                SUM(purchased) as purchased
            FROM user_funnel
        """)
        
        result = self.db.execute(query, {"start": start_date, "end": end_date}).mappings().fetchone()
        
        stages = ["Visit", "Signup", "Search", "Add to Cart", "Checkout", "Purchase"]
        keys = ["visited", "signed_up", "searched", "added_to_cart", "checked_out", "purchased"]
        
        funnel = []
        prev_count = result[keys[0]] or 0
        
        for stage, key in zip(stages, keys):
            count = result[key] or 0
            drop_off = prev_count - count if len(funnel) > 0 else 0
            rate = round(count / prev_count, 4) if prev_count > 0 else 0.0
            
            funnel.append(FunnelStage(
                stage=stage,
                users=count,
                drop_off=drop_off,
                conversion_rate=rate
            ))
            prev_count = count
        
        return funnel

    def get_cohort_retention(self, months: int = 12) -> List[CohortRetentionRow]:
        """Monthly cohort retention curves (Month 0–12)."""
        query = text("""
            WITH user_cohorts AS (
                SELECT 
                    user_id,
                    DATE_TRUNC('month', signup_date)::date AS cohort_month,
                    acquisition_channel
                FROM users
            ),
            user_activity AS (
                SELECT DISTINCT
                    user_id,
                    DATE_TRUNC('month', timestamp)::date AS activity_month
                FROM events
                WHERE event_type IN ('session_start', 'purchase')
            ),
            cohort_sizes AS (
                SELECT cohort_month, COUNT(*) AS cohort_size
                FROM user_cohorts
                GROUP BY cohort_month
            ),
            retention AS (
                SELECT 
                    uc.cohort_month,
                    EXTRACT(YEAR FROM ua.activity_month)::int * 12 + 
                    EXTRACT(MONTH FROM ua.activity_month)::int -
                    (EXTRACT(YEAR FROM uc.cohort_month)::int * 12 + 
                     EXTRACT(MONTH FROM uc.cohort_month)::int) AS period_month,
                    COUNT(DISTINCT uc.user_id) AS retained_users
                FROM user_cohorts uc
                JOIN user_activity ua ON uc.user_id = ua.user_id
                WHERE ua.activity_month >= uc.cohort_month
                  AND uc.cohort_month >= DATE_TRUNC('month', NOW() - INTERVAL ':months months')
                GROUP BY uc.cohort_month, period_month
            )
            SELECT 
                r.cohort_month,
                r.period_month,
                cs.cohort_size,
                r.retained_users,
                ROUND(r.retained_users::numeric / NULLIF(cs.cohort_size, 0), 4) AS retention_rate
            FROM retention r
            JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
            ORDER BY r.cohort_month, r.period_month
        """)
        
        rows = self.db.execute(query, {"months": months}).mappings().all()
        return [CohortRetentionRow(**dict(r)) for r in rows]

    def get_revenue_per_user(self, start_date: datetime, end_date: datetime) -> Dict:
        """Revenue cohort analysis."""
        query = text("""
            SELECT
                DATE_TRUNC('month', u.signup_date)::date as cohort_month,
                COUNT(DISTINCT u.user_id) as users,
                SUM(e.revenue) as total_revenue,
                ROUND(SUM(e.revenue) / NULLIF(COUNT(DISTINCT u.user_id), 0), 2) as arpu
            FROM users u
            LEFT JOIN events e ON u.user_id = e.user_id 
                AND e.event_type = 'purchase'
                AND e.timestamp BETWEEN :start AND :end
            WHERE u.signup_date BETWEEN :start AND :end
            GROUP BY cohort_month
            ORDER BY cohort_month
        """)
        
        results = self.db.execute(query, {"start": start_date, "end": end_date}).mappings().all()
        return {
            "cohorts": [dict(r) for r in results],
            "overall_arpu": round(sum(r["total_revenue"] or 0 for r in results) / 
                                  max(sum(r["users"] for r in results), 1), 2)
        }