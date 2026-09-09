from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    APP_NAME: str = "Retention Analytics API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "development-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)
    TRUSTED_HOSTS: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    MODEL_ARTIFACT_DIR: Path = Path("app/ml/artifacts")
    MODEL_ARTIFACT_BUCKET: str | None = None
    SENTRY_DSN: str | None = None
    EVENT_INGEST_KEY: str | None = None
    MAX_PAGE_SIZE: int = 100
    RATE_LIMIT_DEFAULT: str = "120/minute"
    EVENT_STREAM_NAME: str = "events:ingest"
    EVENT_STREAM_SCHEMA_VERSION: str = "1"

    EVENT_STREAM_GROUP: str = "retention-event-workers"
    EVENT_STREAM_BLOCK_MS: int = 5_000
    EVENT_STREAM_READ_COUNT: int = 100
    EVENT_WORKER_METRICS_PORT: int = 9_101

    EVENT_STREAM_MAX_DELIVERIES: int = 5
    EVENT_STREAM_RETRY_IDLE_MS: int = 30_000
    EVENT_STREAM_DLQ_NAME: str = "events:ingest:dlq"
    EVENT_STREAM_DLQ_MAXLEN: int = 10_000

    EVENT_DB_BATCH_SIZE: int = 100

    EVENT_PIPELINE_FRESHNESS_KEY: str = "events:pipeline:freshness"
    EVENT_PIPELINE_FRESHNESS_SLA_SECONDS: int = 60

    EVENT_STREAM_BACKLOG_LIMIT: int = 50_000
    EVENT_STREAM_RETRY_AFTER_SECONDS: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()
