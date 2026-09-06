from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
    APP_NAME: str = "Retention Analytics API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "development-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "postgresql+asyncpg://retention:retention@localhost:5432/retention"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://retention:retention@localhost:5432/retention"
    REDIS_URL: str = "redis://localhost:6379/0"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)
    TRUSTED_HOSTS: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    MODEL_ARTIFACT_DIR: Path = Path("app/ml/artifacts")
    MODEL_ARTIFACT_BUCKET: str | None = None
    SENTRY_DSN: str | None = None
    EVENT_INGEST_KEY: str | None = None
    MAX_PAGE_SIZE: int = 100
    RATE_LIMIT_DEFAULT: str = "120/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
