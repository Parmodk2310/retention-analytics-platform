"""experiment exposures
Revision ID: 002
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="002";down_revision="001";branch_labels=None;depends_on=None

def upgrade():
    op.create_table("experiment_exposures",sa.Column("id",sa.BigInteger(),primary_key=True,autoincrement=True),sa.Column("experiment_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("experiments.id",ondelete="CASCADE"),nullable=False),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("variant",sa.String(40),nullable=False),sa.Column("exposed_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.UniqueConstraint("experiment_id","user_id",name="uq_exposure_experiment_user"))
    op.create_index("ix_exposure_exp_variant","experiment_exposures",["experiment_id","variant"])
def downgrade(): op.drop_table("experiment_exposures")
