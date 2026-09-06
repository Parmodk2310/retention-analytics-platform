from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token, token_fingerprint
from app.db.models import Account
from app.db.session import get_db

bearer = HTTPBearer(auto_error=False)


async def get_redis() -> Redis:
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


async def get_current_account(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Account:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    try:
        payload = decode_token(credentials.credentials, "access")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
    if await redis.get(f"revoked:{token_fingerprint(credentials.credentials)}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    account = await db.scalar(
        select(Account).where(Account.id == UUID(payload["sub"]), Account.is_active.is_(True))
    )
    if account is None:
        raise HTTPException(status_code=401, detail="Account not found")
    return account


async def verify_ingest_key(request: Request) -> None:
    """Require a shared ingestion key in non-development environments.

    The analytics UI never needs this key; it is intended for SDK/webhook event
    ingestion only. In local development the key may be omitted for convenience.
    """
    configured = settings.EVENT_INGEST_KEY
    if settings.APP_ENV == "development" and not configured:
        return
    if not configured:
        raise HTTPException(status_code=503, detail="Event ingestion is not configured")
    supplied = request.headers.get("X-Event-Ingest-Key")
    if supplied != configured:
        raise HTTPException(status_code=401, detail="Invalid event ingestion key")
