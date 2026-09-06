from fastapi import APIRouter,Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_redis
from app.db.session import get_db
router=APIRouter(prefix="/health",tags=["health"])
@router.get("/live")
async def live():return {"status":"ok"}
@router.get("/ready")
async def ready(db:AsyncSession=Depends(get_db),redis:Redis=Depends(get_redis)):
    await db.execute(text("SELECT 1"));await redis.ping();return {"status":"ready","database":"ok","redis":"ok"}
