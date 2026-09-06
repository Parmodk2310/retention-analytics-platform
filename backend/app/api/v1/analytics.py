from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_account
from app.db.models import Account
from app.db.session import get_db
from app.services import analytics_service,cohort_service,funnel_service
router=APIRouter(prefix="/analytics",tags=["analytics"],dependencies=[Depends(get_current_account)])
@router.get("/overview")
async def overview(days:int=Query(30,ge=1,le=365),db:AsyncSession=Depends(get_db)):return await analytics_service.overview(db,days)
@router.get("/activity")
async def activity(days:int=Query(30,ge=7,le=365),db:AsyncSession=Depends(get_db)):return await analytics_service.activity(db,days)
@router.get("/funnel")
async def funnel(days:int=Query(30,ge=1,le=365),channel:str|None=None,db:AsyncSession=Depends(get_db)):return await funnel_service.get_funnel(db,days,channel)
@router.get("/retention")
async def retention(months:int=Query(12,ge=1,le=24),channel:str|None=None,db:AsyncSession=Depends(get_db)):return await cohort_service.get_retention(db,months,channel)
@router.get("/revenue")
async def revenue(months:int=Query(12,ge=1,le=24),db:AsyncSession=Depends(get_db)):return await analytics_service.revenue(db,months)
@router.get("/channels")
async def channels(days:int=Query(30,ge=1,le=365),db:AsyncSession=Depends(get_db)):return await analytics_service.channels(db,days)
