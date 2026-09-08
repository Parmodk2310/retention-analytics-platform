import json
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.realtime import event_consumer


def stream_event():
    payload = {
        "event_id": str(uuid4()),
        "anonymous_id": "consumer-test",
        "event_name": "page_view",
        "event_time": datetime.now(UTC).isoformat(),
        "revenue": "0",
        "properties": {},
        "idempotency_key": None,
        "session_id": None,
        "user_id": None,
    }

    return {
        b"schema_version": settings.EVENT_STREAM_SCHEMA_VERSION.encode(),
        b"payload": json.dumps(payload).encode(),
    }


@pytest.mark.asyncio
async def test_consume_once_persists_then_acks(monkeypatch):
    redis = AsyncMock()
    db = cast(AsyncSession, AsyncMock(spec=AsyncSession))

    redis.xreadgroup.return_value = [
        [
            b"events:ingest",
            [
                (b"1000-0", stream_event()),
            ],
        ]
    ]

    persist = AsyncMock(return_value=(1, 0))
    monkeypatch.setattr(event_consumer, "ingest", persist)

    accepted, duplicated = await event_consumer.consume_once(
        cast(Redis, redis),
        db,
        "worker-1",
    )

    assert accepted == 1
    assert duplicated == 0

    persist.assert_awaited_once()
    redis.xack.assert_awaited_once_with(
        settings.EVENT_STREAM_NAME,
        settings.EVENT_STREAM_GROUP,
        "1000-0",
    )


@pytest.mark.asyncio
async def test_empty_stream_returns_zero():
    redis = AsyncMock()
    redis.xreadgroup.return_value = []
    db = cast(AsyncSession, AsyncMock(spec=AsyncSession))

    result = await event_consumer.consume_once(
        cast(Redis, redis),
        db,
        "worker-1",
    )

    assert result == (0, 0)
    redis.xack.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_persistence_does_not_ack(monkeypatch):
    redis = AsyncMock()
    db = cast(AsyncSession, AsyncMock(spec=AsyncSession))

    redis.xreadgroup.return_value = [
        [
            b"events:ingest",
            [(b"1000-0", stream_event())],
        ]
    ]

    persist = AsyncMock(side_effect=RuntimeError("database unavailable"))
    monkeypatch.setattr(event_consumer, "ingest", persist)

    with pytest.raises(RuntimeError, match="database unavailable"):
        await event_consumer.consume_once(
            cast(Redis, redis),
            db,
            "worker-1",
        )

    redis.xack.assert_not_awaited()
