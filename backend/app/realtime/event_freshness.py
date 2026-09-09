from datetime import UTC, datetime

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.core.config import settings
from app.observability.metrics import (
    EVENT_PIPELINE_BACKLOG,
    EVENT_PIPELINE_FRESHNESS_SECONDS,
    EVENT_PIPELINE_LAG,
    EVENT_PIPELINE_LAST_PERSISTED,
    EVENT_PIPELINE_PENDING,
)

from app.schemas.event import EventIn


def _text(value: bytes | str | None) -> str | None:
    if value is None:
        return None
    return value.decode() if isinstance(value, bytes) else value


async def acknowledge_persisted(
    redis: Redis,
    message_ids: list[str],
    events: list[EventIn],
    accepted: int,
    duplicated: int,
) -> None:
    if not message_ids:
        return

    now = datetime.now(UTC)
    latest_event_time = max(event.event_time for event in events)

    pipeline = redis.pipeline(transaction=True)
    pipeline.hset(
        settings.EVENT_PIPELINE_FRESHNESS_KEY,
        mapping={
            "last_persisted_at": now.isoformat(),
            "latest_event_time": latest_event_time.isoformat(),
            "last_stream_id": message_ids[-1],
            "batch_events": str(len(events)),
            "accepted": str(accepted),
            "duplicated": str(duplicated),
        },
    )
    pipeline.xack(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        *message_ids,
    )

    await pipeline.execute()


async def pipeline_status(redis: Redis) -> dict:
    raw = await redis.hgetall(settings.EVENT_PIPELINE_FRESHNESS_KEY)

    fields = {_text(key): _text(value) for key, value in raw.items()}

    try:
        groups = await redis.xinfo_groups(settings.EVENT_STREAM_NAME)
    except ResponseError:
        groups = []

    group = next(
        (item for item in groups if _text(item.get("name")) == settings.EVENT_STREAM_GROUP),
        None,
    )

    last_persisted = fields.get("last_persisted_at")
    freshness_seconds: float | None = None

    if last_persisted:
        persisted_at = datetime.fromisoformat(last_persisted)
        freshness_seconds = max(
            0.0,
            (datetime.now(UTC) - persisted_at).total_seconds(),
        )

    pending = int(group.get("pending", 0)) if group else 0
    lag = int(group.get("lag") or 0) if group else 0
    backlog = pending + lag
    EVENT_PIPELINE_BACKLOG.set(backlog)
    EVENT_PIPELINE_PENDING.set(pending)
    EVENT_PIPELINE_LAG.set(lag)

    if freshness_seconds is not None:
        EVENT_PIPELINE_FRESHNESS_SECONDS.set(freshness_seconds)

    if last_persisted:
        EVENT_PIPELINE_LAST_PERSISTED.set(datetime.fromisoformat(last_persisted).timestamp())

    if freshness_seconds is None:
        status = "unknown"
    elif freshness_seconds <= settings.EVENT_PIPELINE_FRESHNESS_SLA_SECONDS:
        status = "fresh"
    else:
        status = "stale"

    return {
        "status": status,
        "last_persisted_at": last_persisted,
        "latest_event_time": fields.get("latest_event_time"),
        "last_stream_id": fields.get("last_stream_id"),
        "freshness_seconds": freshness_seconds,
        "pending": pending,
        "lag": lag,
        "backlog": backlog,
    }
