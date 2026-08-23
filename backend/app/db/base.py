from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    signup_date = Column(DateTime(timezone=True), nullable=False, index=True)
    acquisition_channel = Column(String(50), nullable=False, index=True)
    device_type = Column(String(20), nullable=False)
    experiment_variant = Column(String(20), nullable=False)
    initial_ltv = Column(Numeric(12, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    session_id = Column(String(20), nullable=False, index=True)
    revenue = Column(Numeric(12, 2), default=0.0)
    properties = Column(JSONB, default=dict)
    
    user = relationship("User", back_populates="events")


class Experiment(Base):
    __tablename__ = "experiments"
    
    experiment_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    hypothesis = Column(Text, nullable=False)
    metric_type = Column(String(50), nullable=False)
    status = Column(String(20), default="running")
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"
    
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String(50), ForeignKey("experiments.experiment_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    variant = Column(String(50), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("experiment_id", "user_id", name="uq_exp_user"),
    )