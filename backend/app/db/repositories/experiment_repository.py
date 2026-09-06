from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Experiment
async def get_experiment(db:AsyncSession,experiment_id:UUID)->Experiment|None:
    return await db.scalar(select(Experiment).where(Experiment.id==experiment_id))
