import json
from typing import Any
from uuid import uuid4

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.core.config import settings
from app.schemas.event import EventIn


class EventStreamBackpressure(RuntimeError):
    def __init__(self, backlog: int, limit: int) -> None:
        super().__init__(f"event stream backlog {backlog} exceeds limit {limit}")
        self.backlog = backlog
        self.limit = limit


def _stream_id(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value


def _group_value(
    group: dict[Any, Any],
    key: str,
) -> Any:
    if key in group:
        return group[key]

    return group.get(key.encode())


def _event_payload(event: EventIn) -> str:
    payload = event.model_dump(mode="json")

    if payload["event_id"] is None:
        payload["event_id"] = str(uuid4())

    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )


async def stream_backlog(redis: Redis) -> int:
    try:
        groups = await redis.xinfo_groups(settings.EVENT_STREAM_NAME)
    except ResponseError:
        return 0

    for group in groups:
        raw_name = _group_value(group, "name")

        if raw_name is None:
            continue

        name = _stream_id(raw_name)

        if name != settings.EVENT_STREAM_GROUP:
            continue

        pending = int(_group_value(group, "pending") or 0)
        lag = int(_group_value(group, "lag") or 0)

        return pending + lag

    return 0


async def ensure_stream_capacity(
    redis: Redis,
    incoming: int,
) -> int:
    backlog = await stream_backlog(redis)

    if backlog + incoming > settings.EVENT_STREAM_BACKLOG_LIMIT:
        raise EventStreamBackpressure(
            backlog,
            settings.EVENT_STREAM_BACKLOG_LIMIT,
        )

    return backlog


async def enqueue_events(
    redis: Redis,
    events: list[EventIn],
) -> list[str]:
    if not events:
        return []

    pipeline = redis.pipeline(transaction=False)

    for event in events:
        pipeline.xadd(
            settings.EVENT_STREAM_NAME,
            {
                "schema_version": (settings.EVENT_STREAM_SCHEMA_VERSION),
                "payload": _event_payload(event),
            },
        )

    results = await pipeline.execute()

    return [_stream_id(result) for result in results]
