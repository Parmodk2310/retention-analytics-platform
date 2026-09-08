from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.event import EventBatch, EventIn
from app.services import event_service


def make_event(**overrides) -> EventIn:
    payload = {
        "event_id": uuid4(),
        "user_id": uuid4(),
        "event_name": "page_view",
        "event_time": datetime.now(UTC),
    }
    payload.update(overrides)
    return EventIn(**payload)


def make_db() -> AsyncSession:
    return cast(AsyncSession, AsyncMock(spec=AsyncSession))


def test_duplicate_event_id_is_removed():
    event_id = uuid4()

    unique, duplicated = event_service.deduplicate_events(
        [
            make_event(event_id=event_id),
            make_event(event_id=event_id),
        ]
    )

    assert len(unique) == 1
    assert duplicated == 1


def test_duplicate_idempotency_key_is_removed():
    unique, duplicated = event_service.deduplicate_events(
        [
            make_event(event_id=None, idempotency_key="same-key"),
            make_event(event_id=None, idempotency_key="same-key"),
        ]
    )

    assert len(unique) == 1
    assert duplicated == 1


@pytest.mark.asyncio
async def test_ingest_combines_duplicate_counts(monkeypatch):
    event_id = uuid4()
    insert = AsyncMock(return_value=(1, 1))
    monkeypatch.setattr(event_service, "insert_events", insert)

    accepted, duplicated = await event_service.ingest(
        make_db(),
        EventBatch(
            events=[
                make_event(event_id=event_id),
                make_event(event_id=event_id),
                make_event(),
            ]
        ),
    )

    insert.assert_awaited_once()
    rows = insert.await_args_list[0].args[1]

    assert accepted == 1
    assert duplicated == 2
    assert len(rows) == 2
    assert all(row["event_id"] is not None for row in rows)
    assert all(row["event_date"] == row["event_time"].date() for row in rows)
