import json
from uuid import uuid4

from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.event import EventIn


def _payload(event: EventIn) -> str:
    data = event.model_dump(mode="json")
    data["event_id"] = data["event_id"] or str(uuid4())
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _stream_id(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value


async def enqueue_events(redis: Redis, events: list[EventIn]) -> list[str]:
    if not events:
        return []

    pipe = redis.pipeline(transaction=False)

    for event in events:
        pipe.xadd(
            settings.EVENT_STREAM_NAME,
            {
                "schema_version": settings.EVENT_STREAM_SCHEMA_VERSION,
                "payload": _payload(event),
            },
            maxlen=settings.EVENT_STREAM_MAXLEN,
            approximate=True,
        )

    return [_stream_id(value) for value in await pipe.execute()]
