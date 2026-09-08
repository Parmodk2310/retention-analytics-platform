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
        "user_id": None,
        "anonymous_id": "consumer-test",
        "session_id": None,
        "event_name": "page_view",
        "event_time": datetime.now(UTC).isoformat(),
        "revenue": "0",
        "properties": {},
        "idempotency_key": None,
    }

    return {
        b"schema_version": settings.EVENT_STREAM_SCHEMA_VERSION.encode(),
        b"payload": json.dumps(payload).encode(),
    }


def make_db() -> AsyncSession:
    return cast(AsyncSession, AsyncMock(spec=AsyncSession))


@pytest.mark.asyncio
async def test_consume_once_persists_then_acks(monkeypatch):
    redis = AsyncMock()
    redis.xreadgroup.return_value = [
        [
            b"events:ingest",
            [(b"1000-0", stream_event())],
        ]
    ]

    persist = AsyncMock(return_value=(1, 0))
    monkeypatch.setattr(event_consumer, "ingest", persist)

    accepted, duplicated, dead_lettered = await event_consumer.consume_once(
        cast(Redis, redis),
        make_db(),
        "worker-1",
    )

    assert (accepted, duplicated, dead_lettered) == (1, 0, 0)
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

    result = await event_consumer.consume_once(
        cast(Redis, redis),
        make_db(),
        "worker-1",
    )

    assert result == (0, 0, 0)
    redis.xack.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_persistence_does_not_ack(monkeypatch):
    redis = AsyncMock()
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
            make_db(),
            "worker-1",
        )

    redis.xack.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_message_goes_to_dlq():
    redis = AsyncMock()
    redis.xreadgroup.return_value = [
        [
            b"events:ingest",
            [
                (
                    b"1000-0",
                    {
                        b"schema_version": b"999",
                        b"payload": b"{}",
                    },
                )
            ],
        ]
    ]

    result = await event_consumer.consume_once(
        cast(Redis, redis),
        make_db(),
        "worker-1",
    )

    assert result == (0, 0, 1)
    redis.xadd.assert_awaited_once()
    redis.xack.assert_awaited_once()


@pytest.mark.asyncio
async def test_pending_message_is_claimed_for_retry(monkeypatch):
    redis = AsyncMock()
    redis.xpending_range.return_value = [
        {
            "message_id": b"1000-0",
            "times_delivered": 2,
        }
    ]
    redis.xclaim.return_value = [(b"1000-0", stream_event())]

    persist = AsyncMock(return_value=(1, 0))
    monkeypatch.setattr(event_consumer, "ingest", persist)

    result = await event_consumer.recover_pending_once(
        cast(Redis, redis),
        make_db(),
        "worker-1",
    )

    assert result == (1, 0, 0)
    redis.xclaim.assert_awaited_once()
    redis.xack.assert_awaited_once()


@pytest.mark.asyncio
async def test_max_delivery_message_goes_to_dlq():
    redis = AsyncMock()
    redis.xpending_range.return_value = [
        {
            "message_id": b"1000-0",
            "times_delivered": settings.EVENT_STREAM_MAX_DELIVERIES,
        }
    ]
    redis.xrange.return_value = [(b"1000-0", stream_event())]

    result = await event_consumer.recover_pending_once(
        cast(Redis, redis),
        make_db(),
        "worker-1",
    )

    assert result == (0, 0, 1)
    redis.xadd.assert_awaited_once()
    redis.xack.assert_awaited_once()
    redis.xclaim.assert_not_awaited()
