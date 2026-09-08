import asyncio
import os
import socket

from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.realtime.event_consumer import consume_once, ensure_consumer_group


def _consumer_name() -> str:
    return f"{socket.gethostname()}-{os.getpid()}"


async def run() -> None:
    redis = Redis.from_url(settings.REDIS_URL)
    consumer_name = _consumer_name()

    try:
        await ensure_consumer_group(redis)

        while True:
            async with AsyncSessionLocal() as db:
                await consume_once(redis, db, consumer_name)
    finally:
        await redis.connection_pool.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
