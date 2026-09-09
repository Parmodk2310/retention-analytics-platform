from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.api.deps import get_current_account, get_redis
from app.core.config import settings
from app.realtime.event_freshness import pipeline_status
from app.schemas.system import EventPipelineStatus, SystemFeatures, SystemInfo


router = APIRouter(
    prefix="/system",
    tags=["system"],
    dependencies=[Depends(get_current_account)],
)


@router.get(
    "/event-pipeline",
    response_model=EventPipelineStatus,
)
async def event_pipeline(
    redis: Redis = Depends(get_redis),
) -> EventPipelineStatus:
    return EventPipelineStatus.model_validate(await pipeline_status(redis))


@router.get(
    "/info",
    response_model=SystemInfo,
)
async def info() -> SystemInfo:
    return SystemInfo(
        environment=settings.APP_ENV,
        version="1.0.0",
        features=SystemFeatures(
            realtime=True,
            churn_ml=True,
            experimentation=True,
        ),
    )
