"""Initial schema for retention analytics platform

Revision ID: 001
Revises: 
Create Date: 2026-08-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── Users Dimension ──────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('signup_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('acquisition_channel', sa.String(50), nullable=False, index=True),
        sa.Column('device_type', sa.String(20), nullable=False),
        sa.Column('experiment_variant', sa.String(20), nullable=False),
        sa.Column('initial_ltv', sa.Numeric(12, 2), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # ─── Events Fact Table ────────────────────────────────────────────────────
    op.create_table(
        'events',
        sa.Column('event_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('event_type', sa.String(50), nullable=False, index=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('session_id', sa.String(20), nullable=False, index=True),
        sa.Column('revenue', sa.Numeric(12, 2), default=0.0),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), default=dict),
    )
    
    # ─── Composite Indexes ────────────────────────────────────────────────────
    op.create_index('idx_events_user_timestamp', 'events', ['user_id', 'timestamp'])
    op.create_index('idx_events_type_timestamp', 'events', ['event_type', 'timestamp'])
    op.create_index('idx_events_session', 'events', ['session_id', 'timestamp'])
    
    # ─── Experiments Metadata ─────────────────────────────────────────────────
    op.create_table(
        'experiments',
        sa.Column('experiment_id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),  # proportion, continuous
        sa.Column('status', sa.String(20), default='running'),  # running, stopped, concluded
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # ─── Experiment Assignments ───────────────────────────────────────────────
    op.create_table(
        'experiment_assignments',
        sa.Column('assignment_id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('experiment_id', sa.String(50), sa.ForeignKey('experiments.experiment_id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('variant', sa.String(50), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('experiment_id', 'user_id', name='uq_exp_user'),
    )


def downgrade() -> None:
    op.drop_table('experiment_assignments')
    op.drop_table('experiments')
    op.drop_index('idx_events_session', table_name='events')
    op.drop_index('idx_events_type_timestamp', table_name='events')
    op.drop_index('idx_events_user_timestamp', table_name='events')
    op.drop_table('events')
    op.drop_table('users')