import asyncio
import logging
import os
import socket

from prometheus_client import start_http_server
from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.observability.metrics import (
    EVENT_WORKER_FAILURES,
)
from app.realtime.event_consumer import (
    consume_once,
    ensure_consumer_group,
    recover_pending_once,
)
from app.realtime.event_freshness import (
    pipeline_status,
)

logger = logging.getLogger(__name__)

ERROR_BACKOFF_SECONDS = 2


def _consumer_name() -> str:
    return f"{socket.gethostname()}-{os.getpid()}"


async def run() -> None:
    start_http_server(
        settings.EVENT_WORKER_METRICS_PORT,
        addr="0.0.0.0",
    )

    redis = Redis.from_url(settings.REDIS_URL)
    consumer_name = _consumer_name()

    try:
        await ensure_consumer_group(redis)

        while True:
            try:
                async with AsyncSessionLocal() as db:
                    await recover_pending_once(
                        redis,
                        db,
                        consumer_name,
                    )

                    await consume_once(
                        redis,
                        db,
                        consumer_name,
                    )

                await pipeline_status(redis)

            except Exception:
                EVENT_WORKER_FAILURES.inc()

                logger.exception("event worker iteration failed")

                await asyncio.sleep(ERROR_BACKOFF_SECONDS)

    finally:
        await redis.connection_pool.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
