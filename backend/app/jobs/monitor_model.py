import json
from sqlalchemy import create_engine,text
from app.core.config import settings

def status()->dict:
    engine=create_engine(settings.DATABASE_URL_SYNC,pool_pre_ping=True)
    with engine.connect() as conn:
        row=conn.execute(text("SELECT model_version,metrics,trained_at FROM model_runs ORDER BY trained_at DESC LIMIT 1")).mappings().first()
    if not row:return {"status":"missing_model"}
    auc=float(row["metrics"].get("roc_auc",0));return {"status":"ok" if auc>=0.75 else "alert","model_version":row["model_version"],"roc_auc":auc,"trained_at":row["trained_at"].isoformat()}
if __name__=="__main__":print(json.dumps(status(),indent=2))
