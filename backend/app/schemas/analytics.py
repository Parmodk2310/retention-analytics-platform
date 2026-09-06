from datetime import date
from pydantic import BaseModel
class OverviewMetrics(BaseModel):
    dau:int; wau:int; mau:int; stickiness:float; revenue:float; arpu:float; purchasers:int; new_users:int
class FunnelStage(BaseModel):
    stage:str; users:int; conversion_from_previous:float; dropoff_from_previous:float
class CohortCell(BaseModel):
    cohort_month:date; period_month:int; retained_users:int; cohort_size:int; retention_rate:float; acquisition_channel:str|None=None
