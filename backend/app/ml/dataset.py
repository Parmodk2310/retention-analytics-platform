from datetime import date,timedelta
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from app.ml.labels import churn_label

SNAPSHOT_SQL=text("""
WITH eligible AS (
  SELECT id AS user_id,acquisition_channel,device_type FROM users
  WHERE signup_date <= CAST(:snapshot_date AS date)-INTERVAL '30 days'
),
features AS (
 SELECT u.user_id,u.acquisition_channel,u.device_type,
   COUNT(DISTINCT e.session_id) FILTER (WHERE e.event_name='session_start' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '90 days' AND e.event_time<CAST(:snapshot_date AS date)) AS sessions_90d,
   COUNT(DISTINCT e.session_id) FILTER (WHERE e.event_name='session_start' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '30 days' AND e.event_time<CAST(:snapshot_date AS date)) AS sessions_30d,
   COUNT(*) FILTER (WHERE e.event_name='search' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '30 days' AND e.event_time<CAST(:snapshot_date AS date)) AS searches_30d,
   COUNT(*) FILTER (WHERE e.event_name='add_to_cart' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '30 days' AND e.event_time<CAST(:snapshot_date AS date)) AS carts_30d,
   COUNT(*) FILTER (WHERE e.event_name='checkout' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '30 days' AND e.event_time<CAST(:snapshot_date AS date)) AS checkouts_30d,
   COUNT(*) FILTER (WHERE e.event_name='purchase' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '90 days' AND e.event_time<CAST(:snapshot_date AS date)) AS purchases_90d,
   COALESCE(SUM(e.revenue) FILTER (WHERE e.event_name='purchase' AND e.event_time>=CAST(:snapshot_date AS date)-INTERVAL '90 days' AND e.event_time<CAST(:snapshot_date AS date)),0)::float AS revenue_90d,
   GREATEST(0,COALESCE((CAST(:snapshot_date AS date)-MAX(e.event_date) FILTER (WHERE e.event_time<CAST(:snapshot_date AS date))),90))::int AS days_since_last_activity
 FROM eligible u LEFT JOIN events e ON e.user_id=u.user_id GROUP BY 1,2,3
),
future AS (
 SELECT u.user_id,COUNT(e.id)::int AS future_activity
 FROM eligible u LEFT JOIN events e ON e.user_id=u.user_id AND e.event_name IN ('session_start','purchase')
   AND e.event_time>=CAST(:snapshot_date AS date) AND e.event_time<CAST(:snapshot_date AS date)+(:label_days*INTERVAL '1 day')
 GROUP BY 1
)
SELECT f.*,future.future_activity FROM features f JOIN future USING(user_id)
""")

def build_snapshot(engine:Engine,snapshot_date:date,label_days:int=30)->pd.DataFrame:
    with engine.connect() as conn:
        df=pd.read_sql(SNAPSHOT_SQL,conn,params={"snapshot_date":snapshot_date,"label_days":label_days})
    df["snapshot_date"]=pd.Timestamp(snapshot_date)
    if label_days>0: df["churned"]=df["future_activity"].map(churn_label).astype(int)
    return df

def build_training_dataset(engine:Engine,end_date:date|None=None,snapshots:int=8,spacing_days:int=30,label_days:int=30)->pd.DataFrame:
    end=end_date or (date.today()-timedelta(days=label_days+1))
    frames=[]
    for i in range(snapshots):
        snap=end-timedelta(days=i*spacing_days);df=build_snapshot(engine,snap,label_days)
        if not df.empty:frames.append(df)
    if not frames:raise RuntimeError("No training rows. Seed enough historical events first.")
    return pd.concat(frames,ignore_index=True)
