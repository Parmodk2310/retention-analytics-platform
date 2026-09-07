from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.executor import execute_query


async def overview(
    db: AsyncSession,
    days: int = 30,
    channel: str | None = None,
) -> dict:
    rows = await execute_query(db, "overview", {"days": days, "channel": channel})
    return rows[0]


async def activity(
    db: AsyncSession,
    days: int = 30,
    channel: str | None = None,
) -> list[dict]:
    return await execute_query(db, "activity", {"days": days, "channel": channel})


async def revenue(
    db: AsyncSession,
    months: int = 12,
    channel: str | None = None,
) -> list[dict]:
    return await execute_query(db, "revenue", {"months": months, "channel": channel})


async def channels(db: AsyncSession, days: int = 30) -> list[dict]:
    return await execute_query(db, "channel_performance", {"days": days})
