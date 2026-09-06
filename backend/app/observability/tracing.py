import sentry_sdk
from app.core.config import settings

def init_tracing() -> None:
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.APP_ENV, traces_sample_rate=0.1)
