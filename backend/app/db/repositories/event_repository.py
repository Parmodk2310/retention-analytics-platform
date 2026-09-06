from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event


async def insert_events(db: AsyncSession, rows: list[dict]) -> tuple[int, int]:
    if not rows:
        return 0, 0
    stmt = insert(Event).values(rows).on_conflict_do_nothing().returning(Event.id)
    result = await db.execute(stmt)
    inserted = len(result.scalars().all())
    await db.commit()
    return inserted, len(rows) - inserted
