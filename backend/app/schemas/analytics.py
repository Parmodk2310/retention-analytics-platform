from datetime import date

from pydantic import BaseModel


class OverviewMetrics(BaseModel):
    as_of_date: date
    dau: int
    wau: int
    mau: int
    stickiness: float
    revenue: float
    arpu: float
    purchasers: int
    new_users: int


class ActivityPoint(BaseModel):
    date: date
    active_users: int
    sessions: int
    revenue: float


class FunnelStage(BaseModel):
    stage: str
    users: int
    conversion_from_previous: float
    dropoff_from_previous: float


class CohortCell(BaseModel):
    cohort_month: date
    period_month: int
    retained_users: int
    cohort_size: int
    retention_rate: float
    acquisition_channel: str | None = None


class RevenuePoint(BaseModel):
    month: date
    revenue: float
    purchasers: int
    orders: int


class ChannelPerformance(BaseModel):
    acquisition_channel: str
    users: int
    purchasers: int
    revenue: float
