from fastapi import APIRouter,Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.api.deps import verify_ingest_key
from app.schemas.event import EventBatch,IngestResponse
from app.services.event_service import ingest
router=APIRouter(prefix="/events",tags=["events"],dependencies=[Depends(verify_ingest_key)])
@router.post("/batch",response_model=IngestResponse,status_code=202)
@limiter.limit("60/minute")
async def batch(request:Request,payload:EventBatch,db:AsyncSession=Depends(get_db)):
    accepted,duplicated=await ingest(db,payload);return IngestResponse(accepted=accepted,duplicated=duplicated)
