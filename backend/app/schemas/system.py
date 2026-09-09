from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SystemFeatures(BaseModel):
    realtime: bool
    churn_ml: bool
    experimentation: bool


class SystemInfo(BaseModel):
    environment: str
    version: str
    features: SystemFeatures


class EventPipelineStatus(BaseModel):
    status: Literal["fresh", "stale", "unknown"]
    last_persisted_at: datetime | None = None
    latest_event_time: datetime | None = None
    last_stream_id: str | None = None
    freshness_seconds: float | None = Field(default=None, ge=0)
    pending: int = Field(ge=0)
    lag: int = Field(ge=0)
    backlog: int = Field(ge=0)
