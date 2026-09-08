from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis

from app.api.deps import get_redis, verify_ingest_key
from app.core.config import settings
from app.core.rate_limit import limiter
from app.realtime.event_stream import enqueue_events
from app.schemas.event import EnqueueResponse, EventBatch
from app.services.event_service import deduplicate_events

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(verify_ingest_key)],
)


@router.post("/batch", response_model=EnqueueResponse, status_code=202)
@limiter.limit("60/minute")
async def batch(
    request: Request,
    payload: EventBatch,
    redis: Redis = Depends(get_redis),
):
    unique, duplicated = deduplicate_events(payload.events)
    stream_ids = await enqueue_events(redis, unique)

    return EnqueueResponse(
        queued=len(stream_ids),
        duplicated_in_batch=duplicated,
        stream=settings.EVENT_STREAM_NAME,
        first_stream_id=stream_ids[0] if stream_ids else None,
        last_stream_id=stream_ids[-1] if stream_ids else None,
    )
