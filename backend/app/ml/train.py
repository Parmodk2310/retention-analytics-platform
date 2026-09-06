from datetime import UTC,datetime
import json
from pathlib import Path
import joblib
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import ModelRun
from app.ml.artifact_store import upload_artifact
from app.ml.dataset import build_training_dataset
from app.ml.evaluate import evaluate_binary
from app.ml.features import FEATURES
from app.ml.pipeline import logistic_pipeline,xgboost_pipeline

def temporal_split(df):
    dates=sorted(df["snapshot_date"].dt.date.unique())
    if len(dates)<2:raise RuntimeError("Need at least two snapshot dates for temporal validation")
    cutoff=dates[max(0,int(len(dates)*0.8)-1)]
    return df[df.snapshot_date.dt.date<=cutoff],df[df.snapshot_date.dt.date>cutoff]

def train()->dict:
    engine=create_engine(settings.DATABASE_URL_SYNC,pool_pre_ping=True)
    df=build_training_dataset(engine);train_df,test_df=temporal_split(df)
    Xtr=train_df[FEATURES];ytr=train_df["churned"];Xte=test_df[FEATURES];yte=test_df["churned"]
    ratio=float((ytr==0).sum()/max((ytr==1).sum(),1))
    candidates={"logistic_regression":logistic_pipeline(),"xgboost":xgboost_pipeline(ratio)}
    evaluations={};best_name=None;best=None;best_score=-1.0
    for name,model in candidates.items():
        model.fit(Xtr,ytr);prob=model.predict_proba(Xte)[:,1];metrics=evaluate_binary(yte,prob);evaluations[name]=metrics
        if metrics["pr_auc"]>best_score:best_score=metrics["pr_auc"];best_name=name;best=model
    version=datetime.now(UTC).strftime("churn_%Y%m%dT%H%M%SZ")
    settings.MODEL_ARTIFACT_DIR.mkdir(parents=True,exist_ok=True)
    model_path=settings.MODEL_ARTIFACT_DIR/"churn_model.joblib";meta_path=settings.MODEL_ARTIFACT_DIR/"model_metadata.json"
    joblib.dump(best,model_path)
    metadata={"model_version":version,"algorithm":best_name,"metrics":evaluations[best_name],"all_candidates":evaluations,"features":FEATURES,"trained_at":datetime.now(UTC).isoformat(),"train_rows":len(train_df),"test_rows":len(test_df)}
    meta_path.write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    artifact_uri=upload_artifact(model_path,f"models/{version}/churn_model.joblib");upload_artifact(model_path,"models/latest/churn_model.joblib");upload_artifact(meta_path,"models/latest/model_metadata.json")
    with Session(engine) as session:
        session.add(ModelRun(model_version=version,algorithm=best_name,metrics=metadata["metrics"],feature_names=FEATURES,artifact_uri=artifact_uri));session.commit()
    return metadata

if __name__=="__main__": print(json.dumps(train(),indent=2))
