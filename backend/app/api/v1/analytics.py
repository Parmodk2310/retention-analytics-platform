from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/metrics")
async def get_metrics(
    date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """Get DAU/WAU/MAU and stickiness for a given date."""
    target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
    service = AnalyticsService(db)
    return service.get_dau_wau_mau(target_date)


@router.get("/funnel")
async def get_funnel(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """6-stage conversion funnel for the last N days."""
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    service = AnalyticsService(db)
    return {
        "period_days": days,
        "stages": service.get_funnel_analysis(start, end)
    }


@router.get("/cohorts/retention")
async def get_cohort_retention(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """Monthly cohort retention matrix."""
    service = AnalyticsService(db)
    rows = service.get_cohort_retention(months)
    
    # Pivot for frontend heatmap
    cohorts = {}
    for row in rows:
        cm = row.cohort_month.isoformat()
        if cm not in cohorts:
            cohorts[cm] = {"size": row.cohort_size, "retention": {}}
        cohorts[cm]["retention"][row.period_month] = row.retention_rate
    
    return {
        "months": months,
        "cohorts": cohorts
    }


@router.get("/revenue")
async def get_revenue_cohorts(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """Revenue per user by signup cohort."""
    end = datetime.utcnow()
    start = end - timedelta(days=30 * months)
    service = AnalyticsService(db)
    return service.get_revenue_per_user(start, end)