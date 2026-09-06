"""analytics query indexes

Revision ID: 005
Revises: 004
"""

from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_events_user_name_time "
        "ON events (user_id, event_name, event_time)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_events_name_date_user "
        "ON events (event_name, event_date, user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_signup_channel "
        "ON users (signup_date, acquisition_channel)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_signup_channel")
    op.execute("DROP INDEX IF EXISTS ix_events_name_date_user")
    op.execute("DROP INDEX IF EXISTS ix_events_user_name_time")
