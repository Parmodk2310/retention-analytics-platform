"""analytics indexes
Revision ID: 004
"""
from alembic import op
revision="004";down_revision="003";branch_labels=None;depends_on=None

def upgrade():
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_event_date_brin ON events USING BRIN (event_date)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_purchase_date ON events (event_date, user_id) WHERE event_name='purchase'")
def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_events_purchase_date");op.execute("DROP INDEX IF EXISTS ix_events_event_date_brin")
