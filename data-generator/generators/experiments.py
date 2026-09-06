import hashlib
from datetime import datetime,time,UTC
from config import EXPERIMENT_ID,EXPERIMENT_SALT

def bucket_for(user_id:str)->int:
    digest=hashlib.sha256(f"{EXPERIMENT_SALT}:{EXPERIMENT_ID}:{user_id}".encode()).digest();return int.from_bytes(digest[:8],"big")%10_000
def assign(user_id:str)->str:return "control" if bucket_for(user_id)<5000 else "treatment"
def experiment_row():
    return {"id":EXPERIMENT_ID,"key":"onboarding_v2","name":"Onboarding v2 activation test","hypothesis":"A shorter onboarding flow increases first-14-day purchase activation.","primary_metric":"purchase_rate_14d","variants":["control","treatment"],"traffic_allocation":{"control":.5,"treatment":.5},"status":"running"}
def exposure_time(signup_date):return datetime.combine(signup_date,time(hour=10),tzinfo=UTC)
