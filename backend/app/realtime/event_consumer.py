import json

from redis.asyncio import Redis
from redis.exceptions import ResponseError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.event import EventBatch, EventIn
from app.services.event_service import ingest


def _text(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value


def _fields(raw: dict) -> dict[str, str]:
    return {_text(key): _text(value) for key, value in raw.items()}


def _event(raw: dict) -> EventIn:
    fields = _fields(raw)

    if fields.get("schema_version") != settings.EVENT_STREAM_SCHEMA_VERSION:
        raise ValueError("unsupported event stream schema version")

    return EventIn.model_validate(json.loads(fields["payload"]))


async def ensure_consumer_group(redis: Redis) -> None:
    try:
        await redis.xgroup_create(
            settings.EVENT_STREAM_NAME,
            settings.EVENT_STREAM_GROUP,
            id="0-0",
            mkstream=True,
        )
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def consume_once(
    redis: Redis,
    db: AsyncSession,
    consumer_name: str,
) -> tuple[int, int]:
    messages = await redis.xreadgroup(
        groupname=settings.EVENT_STREAM_GROUP,
        consumername=consumer_name,
        streams={settings.EVENT_STREAM_NAME: ">"},
        count=settings.EVENT_STREAM_READ_COUNT,
        block=settings.EVENT_STREAM_BLOCK_MS,
    )

    if not messages:
        return 0, 0

    stream_messages = messages[0][1]
    ids = []
    events = []

    for message_id, raw_fields in stream_messages:
        ids.append(_text(message_id))
        events.append(_event(raw_fields))

    accepted, duplicated = await ingest(db, EventBatch(events=events))

    if ids:
        await redis.xack(
            settings.EVENT_STREAM_NAME,
            settings.EVENT_STREAM_GROUP,
            *ids,
        )

    return accepted, duplicated
