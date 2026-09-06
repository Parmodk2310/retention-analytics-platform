import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelRun(Base):
    __tablename__ = "model_runs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    algorithm: Mapped[str] = mapped_column(String(80))
    metrics: Mapped[dict] = mapped_column(JSONB)
    feature_names: Mapped[list] = mapped_column(JSONB)
    artifact_uri: Mapped[str] = mapped_column(String(500))
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
