"""initial accounts, users, events, experiments
Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="001"; down_revision=None; branch_labels=None; depends_on=None

def upgrade():
    op.create_table("accounts",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("email",sa.String(320),nullable=False),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("full_name",sa.String(120)),sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("email"))
    op.create_index("ix_accounts_email","accounts",["email"],unique=True)
    op.create_table("users",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("external_id",sa.String(64),nullable=False),sa.Column("signup_date",sa.Date(),nullable=False),sa.Column("acquisition_channel",sa.String(32),nullable=False),sa.Column("device_type",sa.String(16),nullable=False),sa.Column("country",sa.String(2),nullable=False,server_default="IN"),sa.Column("baseline_engagement",sa.Float(),nullable=False,server_default="0.5"),sa.UniqueConstraint("external_id"))
    op.create_index("ix_users_signup_date","users",["signup_date"]);op.create_index("ix_users_channel","users",["acquisition_channel"])
    op.create_table("events",
      sa.Column("id",sa.BigInteger(),primary_key=True,autoincrement=True),sa.Column("event_id",postgresql.UUID(as_uuid=True),nullable=False),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE")),sa.Column("anonymous_id",sa.String(64)),sa.Column("session_id",sa.String(64)),sa.Column("event_name",sa.String(64),nullable=False),sa.Column("event_time",sa.DateTime(timezone=True),nullable=False),sa.Column("event_date",sa.Date(),nullable=False),sa.Column("revenue",sa.Numeric(12,2),nullable=False,server_default="0"),sa.Column("properties",postgresql.JSONB(),nullable=False,server_default=sa.text("'{}'::jsonb")),sa.Column("idempotency_key",sa.String(128)),sa.Column("received_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("event_id"),sa.UniqueConstraint("idempotency_key"))
    op.create_index("ix_events_user_time","events",["user_id","event_time"]);op.create_index("ix_events_name_time","events",["event_name","event_time"]);op.create_index("ix_events_event_date","events",["event_date"]);op.create_index("ix_events_session_id","events",["session_id"])
    op.create_table("experiments",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("key",sa.String(80),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("hypothesis",sa.String(500),nullable=False),sa.Column("primary_metric",sa.String(80),nullable=False),sa.Column("variants",postgresql.JSONB(),nullable=False),sa.Column("traffic_allocation",postgresql.JSONB(),nullable=False),sa.Column("status",sa.String(24),nullable=False,server_default="draft"),sa.Column("starts_at",sa.DateTime(timezone=True)),sa.Column("ends_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("key"))
    op.create_table("experiment_assignments",
      sa.Column("id",sa.BigInteger(),primary_key=True,autoincrement=True),sa.Column("experiment_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("experiments.id",ondelete="CASCADE"),nullable=False),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("variant",sa.String(40),nullable=False),sa.Column("assigned_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("experiment_id","user_id",name="uq_assignment_experiment_user"))
    op.create_index("ix_assignments_experiment_variant","experiment_assignments",["experiment_id","variant"])

def downgrade():
    op.drop_table("experiment_assignments");op.drop_table("experiments");op.drop_table("events");op.drop_table("users");op.drop_table("accounts")
