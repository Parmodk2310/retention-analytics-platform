import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.middleware import RequestTimingMiddleware, ErrorHandlingMiddleware
from app.db.base import engine
from app.ml.predict import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting up...")
    load_model()
    yield
    # Shutdown
    await engine.dispose()
    print("👋 Shutting down...")


def create_application() -> FastAPI:
    app = FastAPI(
        title="Retention Analytics API",
        description="Product Analytics · SQL · A/B Testing · ML",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        max_age=600,
    )
    
    # Custom middleware
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # API routes
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app


app = create_application()