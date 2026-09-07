from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_account
from app.db.session import get_db
from app.schemas.analytics import (
    ActivityPoint,
    ChannelPerformance,
    CohortCell,
    FunnelStage,
    OverviewMetrics,
    RevenuePoint,
)
from app.services import analytics_service, cohort_service, funnel_service

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_account)],
)


@router.get("/overview", response_model=OverviewMetrics)
async def overview(
    days: int = Query(30, ge=1, le=365),
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await analytics_service.overview(db, days, channel)


@router.get("/activity", response_model=list[ActivityPoint])
async def activity(
    days: int = Query(30, ge=7, le=365),
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await analytics_service.activity(db, days, channel)


@router.get("/funnel", response_model=list[FunnelStage])
async def funnel(
    days: int = Query(30, ge=1, le=365),
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await funnel_service.get_funnel(db, days, channel)


@router.get("/retention", response_model=list[CohortCell])
async def retention(
    months: int = Query(12, ge=1, le=24),
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await cohort_service.get_retention(db, months, channel)


@router.get("/revenue", response_model=list[RevenuePoint])
async def revenue(
    months: int = Query(12, ge=1, le=24),
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await analytics_service.revenue(db, months, channel)


@router.get("/channels", response_model=list[ChannelPerformance])
async def channels(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await analytics_service.channels(db, days)
