from fastapi import APIRouter,Depends
from app.api.deps import get_current_account
from app.core.config import settings
router=APIRouter(prefix="/system",tags=["system"],dependencies=[Depends(get_current_account)])
@router.get("/info")
async def info():return {"environment":settings.APP_ENV,"version":"1.0.0","features":{"realtime":True,"churn_ml":True,"experimentation":True}}
