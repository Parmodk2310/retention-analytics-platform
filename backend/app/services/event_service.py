from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.event_repository import insert_events
from app.schemas.event import EventBatch
async def ingest(db:AsyncSession,batch:EventBatch)->tuple[int,int]:
    rows=[]
    for item in batch.events:
        d=item.model_dump();d["event_id"]=d["event_id"] or uuid4();d["event_date"]=d["event_time"].date();rows.append(d)
    return await insert_events(db,rows)
