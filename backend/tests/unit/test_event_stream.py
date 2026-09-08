import json
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import pytest
from redis.asyncio import Redis

from app.core.config import settings
from app.realtime.event_stream import enqueue_events
from app.schemas.event import EventIn


class FakePipeline:
    def __init__(self):
        self.calls = []

    def xadd(self, name, fields, *, maxlen=None, approximate=True):
        self.calls.append(
            {
                "name": name,
                "fields": fields,
                "maxlen": maxlen,
                "approximate": approximate,
            }
        )
        return self

    async def execute(self):
        return [f"1000{i}-0".encode() for i in range(len(self.calls))]


class FakeRedis:
    def __init__(self):
        self.pipe = FakePipeline()

    def pipeline(self, transaction=False):
        assert transaction is False
        return self.pipe


def make_event(**overrides) -> EventIn:
    payload = {
        "event_id": None,
        "anonymous_id": "stream-test",
        "idempotency_key": "stream-event-001",
        "event_name": "page_view",
        "event_time": datetime.now(UTC),
    }
    payload.update(overrides)
    return EventIn(**payload)


@pytest.mark.asyncio
async def test_enqueue_events():
    redis = FakeRedis()

    ids = await enqueue_events(
        cast(Redis, redis),
        [
            make_event(idempotency_key="stream-001"),
            make_event(idempotency_key="stream-002"),
        ],
    )

    assert ids == ["10000-0", "10001-0"]
    assert len(redis.pipe.calls) == 2
    assert redis.pipe.calls[0]["name"] == settings.EVENT_STREAM_NAME


@pytest.mark.asyncio
async def test_stream_payload_has_stable_event_id():
    redis = FakeRedis()

    await enqueue_events(cast(Redis, redis), [make_event()])

    payload = json.loads(redis.pipe.calls[0]["fields"]["payload"])

    UUID(payload["event_id"])
    assert payload["idempotency_key"] == "stream-event-001"


@pytest.mark.asyncio
async def test_empty_batch_does_not_write():
    redis = FakeRedis()

    ids = await enqueue_events(cast(Redis, redis), [])

    assert ids == []
    assert redis.pipe.calls == []
