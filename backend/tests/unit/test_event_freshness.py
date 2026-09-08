import pytest

from uuid import uuid4
from typing import cast, Any
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from redis.asyncio import Redis
from app.schemas.event import EventIn
from app.core.config import settings
from app.realtime.event_freshness import pipeline_status, acknowledge_persisted


class FakePipeline:
    def __init__(self) -> None:
        self.hset_args: tuple[Any, ...] | None = None
        self.hset_kwargs: dict[str, Any] | None = None

        self.xack_args: tuple[Any, ...] | None = None

        self.executed = False

    def hset(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> "FakePipeline":
        self.hset_args = args
        self.hset_kwargs = kwargs
        return self

    def xack(
        self,
        *args: Any,
    ) -> "FakePipeline":
        self.xack_args = args
        return self

    async def execute(self) -> list[int]:
        self.executed = True
        return [1, 1]


class FakeRedis:
    def __init__(self) -> None:
        self.pipe = FakePipeline()

    def pipeline(
        self,
        transaction: bool = True,
    ) -> FakePipeline:
        assert transaction is True
        return self.pipe


@pytest.mark.asyncio
async def test_pipeline_status_is_fresh():
    redis = AsyncMock()
    redis.hgetall.return_value = {
        b"last_persisted_at": datetime.now(UTC).isoformat().encode(),
        b"latest_event_time": datetime.now(UTC).isoformat().encode(),
        b"last_stream_id": b"1000-0",
    }
    redis.xinfo_groups.return_value = [
        {
            b"name": settings.EVENT_STREAM_GROUP.encode(),
            b"pending": 0,
            b"lag": 0,
        }
    ]

    result = await pipeline_status(cast(Redis, redis))

    assert result["status"] == "fresh"
    assert result["pending"] == 0
    assert result["lag"] == 0


@pytest.mark.asyncio
async def test_pipeline_status_without_watermark_is_unknown():
    redis = AsyncMock()
    redis.hgetall.return_value = {}
    redis.xinfo_groups.return_value = []

    result = await pipeline_status(cast(Redis, redis))

    assert result["status"] == "unknown"
    assert result["freshness_seconds"] is None


@pytest.mark.asyncio
async def test_acknowledge_persisted_updates_watermark_and_acks():
    redis = FakeRedis()

    event = EventIn(
        event_id=uuid4(),
        anonymous_id="freshness-test",
        event_name="page_view",
        event_time=datetime.now(UTC),
    )

    await acknowledge_persisted(
        cast(Redis, redis),
        ["1000-0"],
        [event],
        accepted=1,
        duplicated=0,
    )

    assert redis.pipe.hset_args is not None
    assert redis.pipe.hset_kwargs is not None
    assert redis.pipe.xack_args is not None
    assert redis.pipe.executed is True

    assert redis.pipe.xack_args[-1] == "1000-0"
