from datetime import date
import json
from sqlalchemy import create_engine,delete
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import ChurnScore
from app.ml.dataset import build_snapshot
from app.ml.predict import load_metadata,load_model,predict_scores,reason_codes,risk_band
from app.observability.metrics import CHURN_PREDICTIONS

def score_latest()->dict:
    engine=create_engine(settings.DATABASE_URL_SYNC,pool_pre_ping=True);snapshot=date.today();frame=build_snapshot(engine,snapshot,label_days=0)
    if frame.empty:return {"scored":0}
    model=load_model();meta=load_metadata();scores=predict_scores(model,frame);version=meta["model_version"]
    rows=[]
    for (_,row),score in zip(frame.iterrows(),scores,strict=True):
        band=risk_band(float(score));CHURN_PREDICTIONS.labels(band).inc();rows.append(ChurnScore(user_id=row.user_id,snapshot_date=snapshot,score=float(score),risk_band=band,model_version=version,reasons=reason_codes(row)))
    with Session(engine) as session:
        session.execute(delete(ChurnScore).where(ChurnScore.snapshot_date==snapshot,ChurnScore.model_version==version));session.add_all(rows);session.commit()
    return {"scored":len(rows),"snapshot_date":str(snapshot),"model_version":version}
if __name__=="__main__":print(json.dumps(score_latest(),indent=2))
