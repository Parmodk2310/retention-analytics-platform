from pathlib import Path
from time import perf_counter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.observability.metrics import ANALYTICS_QUERY_DURATION
QUERY_DIR=Path(__file__).parent/"queries"
async def execute_query(db:AsyncSession,name:str,params:dict|None=None)->list[dict]:
    sql=(QUERY_DIR/f"{name}.sql").read_text(encoding="utf-8")
    started=perf_counter()
    try:
        result=await db.execute(text(sql),params or {})
        return [dict(row._mapping) for row in result]
    finally:
        ANALYTICS_QUERY_DURATION.labels(name).observe(perf_counter()-started)
