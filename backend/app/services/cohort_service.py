from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.executor import execute_query


async def get_retention(
    db: AsyncSession, months: int = 12, channel: str | None = None
) -> list[dict]:
    return await execute_query(db, "retention", {"months": months, "channel": channel})
