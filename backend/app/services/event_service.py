from collections.abc import Iterator
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.repositories.event_repository import insert_events
from app.schemas.event import EventBatch, EventIn


def deduplicate_events(events: list[EventIn]) -> tuple[list[EventIn], int]:
    unique: list[EventIn] = []
    event_ids: set[UUID] = set()
    idempotency_keys: set[str] = set()
    duplicated = 0

    for event in events:
        duplicate_id = event.event_id is not None and event.event_id in event_ids
        duplicate_key = (
            event.idempotency_key is not None and event.idempotency_key in idempotency_keys
        )

        if duplicate_id or duplicate_key:
            duplicated += 1
            continue

        if event.event_id is not None:
            event_ids.add(event.event_id)
        if event.idempotency_key is not None:
            idempotency_keys.add(event.idempotency_key)

        unique.append(event)

    return unique, duplicated


def _event_row(event: EventIn) -> dict:
    row = event.model_dump()
    row["event_id"] = row["event_id"] or uuid4()
    row["event_date"] = row["event_time"].date()
    return row


def _chunks(rows: list[dict], size: int) -> Iterator[list[dict]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


async def ingest(db: AsyncSession, batch: EventBatch) -> tuple[int, int]:
    unique, request_duplicates = deduplicate_events(batch.events)
    rows = [_event_row(event) for event in unique]

    accepted = 0
    database_duplicates = 0

    for chunk in _chunks(rows, settings.EVENT_DB_BATCH_SIZE):
        chunk_accepted, chunk_duplicates = await insert_events(db, chunk)
        accepted += chunk_accepted
        database_duplicates += chunk_duplicates

    return accepted, request_duplicates + database_duplicates
