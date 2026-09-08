from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.event import EventBatch, EventIn


def payload(**overrides):
    value = {
        "event_id": uuid4(),
        "user_id": uuid4(),
        "event_name": "page_view",
        "event_time": datetime.now(UTC),
    }
    value.update(overrides)
    return value


def test_valid_event():
    event = EventIn(**payload())
    offset = event.event_time.utcoffset()

    assert event.event_id is not None
    assert offset is not None
    assert offset.total_seconds() == 0


def test_identity_is_required():
    with pytest.raises(ValidationError):
        EventIn(**payload(user_id=None, anonymous_id=None))


def test_idempotency_identity_is_required():
    with pytest.raises(ValidationError):
        EventIn(**payload(event_id=None, idempotency_key=None))


def test_batch_accepts_valid_events():
    batch = EventBatch(events=[EventIn(**payload())])

    assert len(batch.events) == 1
