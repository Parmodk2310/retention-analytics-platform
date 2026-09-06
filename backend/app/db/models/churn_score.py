import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChurnScore(Base):
    __tablename__ = "churn_scores"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    score: Mapped[float] = mapped_column(Float)
    risk_band: Mapped[str] = mapped_column(String(16), index=True)
    model_version: Mapped[str] = mapped_column(String(80), index=True)
    reasons: Mapped[list] = mapped_column(JSONB, default=list)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", "model_version", name="uq_churn_score"),
    )
