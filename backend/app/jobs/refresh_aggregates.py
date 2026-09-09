from sqlalchemy import create_engine, text

from app.core.config import settings


def refresh_statistics() -> None:
    """Refresh PostgreSQL planner statistics for high-volume analytics tables."""
    engine = create_engine(
        settings.DATABASE_URL_SYNC,
        pool_pre_ping=True,
    )

    with engine.begin() as conn:
        conn.execute(text("ANALYZE users"))
        conn.execute(text("ANALYZE events"))


def refresh() -> None:
    """Backward-compatible scheduled-job entry point."""
    refresh_statistics()


if __name__ == "__main__":
    refresh()
