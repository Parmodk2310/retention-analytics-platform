from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.executor import execute_query


async def query(db: AsyncSession, name: str, params: dict) -> list[dict]:
    return await execute_query(db, name, params)
