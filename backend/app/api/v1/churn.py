from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_account
from app.db.session import get_db
from app.services.churn_service import latest_model,latest_scores
router=APIRouter(prefix="/churn",tags=["churn"],dependencies=[Depends(get_current_account)])
@router.get("/scores")
async def scores(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0),risk_band:str|None=None,db:AsyncSession=Depends(get_db)):return await latest_scores(db,limit,offset,risk_band)
@router.get("/model-health")
async def model_health(db:AsyncSession=Depends(get_db)):
    model=await latest_model(db)
    return None if model is None else {"model_version":model.model_version,"algorithm":model.algorithm,"metrics":model.metrics,"trained_at":model.trained_at,"artifact_uri":model.artifact_uri}
