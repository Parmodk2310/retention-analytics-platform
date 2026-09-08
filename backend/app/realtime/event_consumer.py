import json
from datetime import UTC, datetime

from redis.asyncio import Redis
from redis.exceptions import ResponseError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.event import EventBatch, EventIn
from app.services.event_service import ingest
from app.realtime.event_freshness import acknowledge_persisted


def _text(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value


def _fields(raw: dict) -> dict[str, str]:
    return {_text(key): _text(value) for key, value in raw.items()}


def _event(raw: dict) -> EventIn:
    fields = _fields(raw)

    if fields.get("schema_version") != settings.EVENT_STREAM_SCHEMA_VERSION:
        raise ValueError("unsupported event stream schema version")

    return EventIn.model_validate(json.loads(fields["payload"]))


async def _dead_letter(
    redis: Redis,
    message_id: str,
    raw: dict,
    reason: str,
) -> None:
    fields = _fields(raw)

    await redis.xadd(
        settings.EVENT_STREAM_DLQ_NAME,
        {
            "source_stream": settings.EVENT_STREAM_NAME,
            "source_id": message_id,
            "reason": reason[:500],
            "failed_at": datetime.now(UTC).isoformat(),
            "schema_version": fields.get("schema_version", ""),
            "payload": fields.get("payload", ""),
        },
        maxlen=settings.EVENT_STREAM_DLQ_MAXLEN,
        approximate=True,
    )

    await redis.xack(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        message_id,
    )


async def _process_messages(
    redis: Redis,
    db: AsyncSession,
    messages: list,
) -> tuple[int, int, int]:
    ids: list[str] = []
    events: list[EventIn] = []
    dead_lettered = 0

    for raw_id, raw_fields in messages:
        message_id = _text(raw_id)

        try:
            event = _event(raw_fields)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            await _dead_letter(redis, message_id, raw_fields, str(exc))
            dead_lettered += 1
            continue

        ids.append(message_id)
        events.append(event)

    if not events:
        return 0, 0, dead_lettered

    accepted, duplicated = await ingest(db, EventBatch(events=events))

    await redis.xack(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        *ids,
    )

    await acknowledge_persisted(
        redis,
        ids,
        events,
        accepted,
        duplicated,
    )

    return accepted, duplicated, dead_lettered


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
) -> tuple[int, int, int]:
    response = await redis.xreadgroup(
        groupname=settings.EVENT_STREAM_GROUP,
        consumername=consumer_name,
        streams={settings.EVENT_STREAM_NAME: ">"},
        count=settings.EVENT_STREAM_READ_COUNT,
        block=settings.EVENT_STREAM_BLOCK_MS,
    )

    if not response:
        return 0, 0, 0

    return await _process_messages(redis, db, response[0][1])


async def recover_pending_once(
    redis: Redis,
    db: AsyncSession,
    consumer_name: str,
) -> tuple[int, int, int]:
    pending = await redis.xpending_range(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        min="-",
        max="+",
        count=settings.EVENT_STREAM_READ_COUNT,
        idle=settings.EVENT_STREAM_RETRY_IDLE_MS,
    )

    if not pending:
        return 0, 0, 0

    retry_ids: list[str] = []
    dead_lettered = 0

    for item in pending:
        message_id = _text(item["message_id"])
        deliveries = int(item["times_delivered"])

        if deliveries < settings.EVENT_STREAM_MAX_DELIVERIES:
            retry_ids.append(message_id)
            continue

        rows = await redis.xrange(
            settings.EVENT_STREAM_NAME,
            min=message_id,
            max=message_id,
            count=1,
        )

        if rows:
            await _dead_letter(
                redis,
                message_id,
                rows[0][1],
                f"maximum deliveries exceeded: {deliveries}",
            )
        else:
            await redis.xack(
                settings.EVENT_STREAM_NAME,
                settings.EVENT_STREAM_GROUP,
                message_id,
            )

        dead_lettered += 1

    if not retry_ids:
        return 0, 0, dead_lettered

    claimed = await redis.xclaim(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        consumer_name,
        settings.EVENT_STREAM_RETRY_IDLE_MS,
        retry_ids,
    )

    accepted, duplicated, invalid = await _process_messages(
        redis,
        db,
        claimed,
    )

    return accepted, duplicated, dead_lettered + invalid
