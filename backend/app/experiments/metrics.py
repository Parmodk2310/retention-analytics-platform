from datetime import timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
async def binary_conversion_counts(db:AsyncSession,experiment_id:str,conversion_event:str="purchase",window_days:int=14)->dict[str,dict[str,int]]:
    sql=text("""
    WITH exposed AS (SELECT user_id,variant,exposed_at FROM experiment_exposures WHERE experiment_id=CAST(:experiment_id AS uuid)),
    conv AS (SELECT DISTINCT x.user_id,x.variant FROM exposed x JOIN events e ON e.user_id=x.user_id AND e.event_name=:event AND e.event_time>=x.exposed_at AND e.event_time<x.exposed_at+(:window_days*INTERVAL '1 day'))
    SELECT x.variant,COUNT(*)::int n,COUNT(c.user_id)::int conversions FROM exposed x LEFT JOIN conv c ON c.user_id=x.user_id AND c.variant=x.variant GROUP BY x.variant
    """)
    rows=(await db.execute(sql,{"experiment_id":experiment_id,"event":conversion_event,"window_days":window_days})).mappings().all()
    return {r["variant"]:{"n":r["n"],"conversions":r["conversions"]} for r in rows}
