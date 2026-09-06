import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    signup_date: Mapped[date] = mapped_column(Date, index=True)
    acquisition_channel: Mapped[str] = mapped_column(String(32), index=True)
    device_type: Mapped[str] = mapped_column(String(16), index=True)
    country: Mapped[str] = mapped_column(String(2), default="IN", index=True)
    baseline_engagement: Mapped[float] = mapped_column(Float, default=0.5)
