from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_account, get_redis
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    token_fingerprint,
    verify_password,
)
from app.db.models import Account
from app.db.session import get_db
from app.schemas.auth import AccountResponse, LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _cookie(response: Response, token: str):
    response.set_cookie(
        "refresh_token",
        token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="strict",
        path=f"{settings.API_V1_PREFIX}/auth",
    )


async def _token_response(account: Account, response: Response) -> TokenResponse:
    access = create_access_token(str(account.id))
    refresh = create_refresh_token(str(account.id))
    _cookie(response, refresh)
    return TokenResponse(access_token=access, account=AccountResponse.model_validate(account))


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    if await db.scalar(select(Account).where(Account.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="Email already registered")
    account = Account(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return await _token_response(account, response)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    account = await db.scalar(select(Account).where(Account.email == payload.email.lower()))
    if (
        not account
        or not account.is_active
        or not verify_password(payload.password, account.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return await _token_response(account, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        payload = decode_token(token, "refresh")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    fp = token_fingerprint(token)
    if await redis.get(f"revoked:{fp}"):
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    await redis.setex(f"revoked:{fp}", settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")
    account = await db.get(Account, UUID(payload["sub"]))
    if not account or not account.is_active:
        raise HTTPException(status_code=401, detail="Account not found")
    return await _token_response(account, response)


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, redis: Redis = Depends(get_redis)):
    token = request.cookies.get("refresh_token")
    if token:
        await redis.setex(
            f"revoked:{token_fingerprint(token)}", settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1"
        )
    response.delete_cookie("refresh_token", path=f"{settings.API_V1_PREFIX}/auth")


@router.get("/me", response_model=AccountResponse)
async def me(account: Account = Depends(get_current_account)):
    return account
