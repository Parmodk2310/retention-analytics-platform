from sqlalchemy.ext.asyncio import AsyncSession
from app.analytics.executor import execute_query
async def get_funnel(db:AsyncSession,days:int=30,channel:str|None=None)->list[dict]:
    rows=await execute_query(db,"funnel",{"days":days,"channel":channel}); out=[]; prev=None
    for row in rows:
        users=row["users"]; conv=1.0 if prev is None else (users/prev if prev else 0.0)
        out.append({"stage":row["stage"],"users":users,"conversion_from_previous":round(conv,4),"dropoff_from_previous":round(1-conv,4) if prev is not None else 0.0}); prev=users
    return out
