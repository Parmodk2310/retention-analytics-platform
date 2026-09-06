from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class ChurnScoreResponse(BaseModel):
    user_id: UUID
    external_id: str
    snapshot_date: date
    score: float
    risk_band: str
    model_version: str
    reasons: list[str]


class ModelHealthResponse(BaseModel):
    model_version: str
    algorithm: str
    metrics: dict
    trained_at: datetime
    artifact_uri: str
