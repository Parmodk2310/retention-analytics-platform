from sqlalchemy import create_engine, text

from app.core.config import settings


def refresh() -> None:
    engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text("ANALYZE users"))
        conn.execute(text("ANALYZE events"))


if __name__ == "__main__":
    refresh()
