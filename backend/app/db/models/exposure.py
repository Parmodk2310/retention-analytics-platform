import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExperimentExposure(Base):
    __tablename__ = "experiment_exposures"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    variant: Mapped[str] = mapped_column(String(40), index=True)
    exposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("experiment_id", "user_id", name="uq_exposure_experiment_user"),
    )
