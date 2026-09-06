from pathlib import Path
import boto3
from app.core.config import settings

def upload_artifact(local_path:Path,key:str)->str:
    if not settings.MODEL_ARTIFACT_BUCKET:return str(local_path)
    boto3.client("s3").upload_file(str(local_path),settings.MODEL_ARTIFACT_BUCKET,key)
    return f"s3://{settings.MODEL_ARTIFACT_BUCKET}/{key}"

def download_latest(filename:str)->Path:
    local=settings.MODEL_ARTIFACT_DIR/filename
    if local.exists():return local
    if not settings.MODEL_ARTIFACT_BUCKET:raise FileNotFoundError(local)
    local.parent.mkdir(parents=True,exist_ok=True)
    boto3.client("s3").download_file(settings.MODEL_ARTIFACT_BUCKET,f"models/latest/{filename}",str(local))
    return local
