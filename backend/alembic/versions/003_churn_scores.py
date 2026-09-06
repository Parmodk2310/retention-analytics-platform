"""model runs and churn scores
Revision ID: 003
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="003";down_revision="002";branch_labels=None;depends_on=None

def upgrade():
    op.create_table("model_runs",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("model_version",sa.String(80),nullable=False),sa.Column("algorithm",sa.String(80),nullable=False),sa.Column("metrics",postgresql.JSONB(),nullable=False),sa.Column("feature_names",postgresql.JSONB(),nullable=False),sa.Column("artifact_uri",sa.String(500),nullable=False),sa.Column("trained_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("model_version"))
    op.create_table("churn_scores",sa.Column("id",sa.BigInteger(),primary_key=True,autoincrement=True),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("snapshot_date",sa.Date(),nullable=False),sa.Column("score",sa.Float(),nullable=False),sa.Column("risk_band",sa.String(16),nullable=False),sa.Column("model_version",sa.String(80),nullable=False),sa.Column("reasons",postgresql.JSONB(),nullable=False,server_default=sa.text("'[]'::jsonb")),sa.Column("scored_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("user_id","snapshot_date","model_version",name="uq_churn_score"))
    op.create_index("ix_churn_scores_snapshot_risk","churn_scores",["snapshot_date","risk_band"])
def downgrade(): op.drop_table("churn_scores");op.drop_table("model_runs")
