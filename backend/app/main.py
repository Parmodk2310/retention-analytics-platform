from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import make_asgi_app
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.rate_limit import limiter
from app.db.session import engine
from app.observability.tracing import init_tracing


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_tracing()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestContextMiddleware)
if settings.TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Idempotency-Key"],
        max_age=600,
    )
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.mount("/metrics", make_asgi_app())
