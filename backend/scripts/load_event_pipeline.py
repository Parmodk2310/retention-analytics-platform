import asyncio
import os
import time
from datetime import UTC, datetime
from uuid import uuid4

from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.realtime.event_stream import (
    enqueue_events,
    ensure_stream_capacity,
    stream_backlog,
)
from app.schemas.event import EventIn

TOTAL = int(os.getenv("LOAD_EVENTS", "2000"))
BATCH_SIZE = int(os.getenv("LOAD_BATCH_SIZE", "100"))
CONCURRENCY = int(os.getenv("LOAD_CONCURRENCY", "5"))
RUN_ID = f"phase6i-{uuid4().hex[:10]}"


def _event(index: int) -> EventIn:
    return EventIn(
        anonymous_id=f"{RUN_ID}-{index}",
        idempotency_key=f"{RUN_ID}-{index}",
        event_name="page_view",
        event_time=datetime.now(UTC),
        properties={
            "source": "phase6i-load",
            "load_run": RUN_ID,
        },
    )


async def _publish(redis: Redis) -> list[str]:
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def publish_batch(start: int) -> list[str]:
        events = [
            _event(index)
            for index in range(
                start,
                min(start + BATCH_SIZE, TOTAL),
            )
        ]

        async with semaphore:
            await ensure_stream_capacity(
                redis,
                len(events),
            )
            return await enqueue_events(
                redis,
                events,
            )

    batches = await asyncio.gather(*(publish_batch(start) for start in range(0, TOTAL, BATCH_SIZE)))

    return [stream_id for batch in batches for stream_id in batch]


async def _wait_for_drain(redis: Redis) -> None:
    for _ in range(120):
        if await stream_backlog(redis) == 0:
            return
        await asyncio.sleep(0.5)

    raise TimeoutError("event pipeline did not drain")


async def _persisted_count() -> int:
    async with AsyncSessionLocal() as db:
        return int(
            await db.scalar(
                text("""
                    SELECT COUNT(*)
                    FROM events
                    WHERE properties->>'load_run' = :run_id
                """),
                {"run_id": RUN_ID},
            )
            or 0
        )


async def _cleanup_db() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                DELETE FROM events
                WHERE properties->>'load_run' = :run_id
                RETURNING id
            """),
            {"run_id": RUN_ID},
        )
        deleted = len(result.scalars().all())
        await db.commit()
        return deleted


async def _cleanup_stream(
    redis: Redis,
    ids: list[str],
) -> None:
    for start in range(0, len(ids), 500):
        await redis.xdel(
            settings.EVENT_STREAM_NAME,
            *ids[start : start + 500],
        )


async def main() -> None:
    redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    ids: list[str] = []

    try:
        started = time.perf_counter()

        ids = await _publish(redis)
        published = time.perf_counter()

        await _wait_for_drain(redis)
        finished = time.perf_counter()

        persisted = await _persisted_count()

        publish_seconds = published - started
        total_seconds = finished - started

        print("EVENT PIPELINE LOAD TEST")
        print("run:", RUN_ID)
        print("events:", TOTAL)
        print("persisted:", persisted)
        print("publish_seconds:", round(publish_seconds, 3))
        print("end_to_end_seconds:", round(total_seconds, 3))
        print(
            "throughput_events_per_second:",
            round(TOTAL / total_seconds, 2),
        )
        print("final_backlog:", await stream_backlog(redis))

        if persisted != TOTAL:
            raise RuntimeError(f"expected {TOTAL} rows, found {persisted}")
    finally:
        deleted = await _cleanup_db()

        if ids:
            await _cleanup_stream(redis, ids)

        print("cleanup_deleted:", deleted)
        await redis.connection_pool.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
