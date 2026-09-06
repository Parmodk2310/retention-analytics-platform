export type Account={id:string;email:string;full_name:string|null}
export type Overview={dau:number;wau:number;mau:number;stickiness:number;revenue:number;arpu:number;purchasers:number;new_users:number}
export type ActivityPoint={date:string;active_users:number;sessions:number;revenue:number}
export type FunnelStage={stage:string;users:number;conversion_from_previous:number;dropoff_from_previous:number}
export type CohortCell={cohort_month:string;acquisition_channel:string;period_month:number;retained_users:number;cohort_size:number;retention_rate:number}
export type ChurnScore={user_id:string;external_id:string;snapshot_date:string;score:number;risk_band:'low'|'medium'|'high'|'critical';model_version:string;reasons:string[]}
export type Experiment={id:string;key:string;name:string;hypothesis:string;primary_metric:string;variants:string[];traffic_allocation:Record<string,number>;status:string;starts_at:string|null;ends_at:string|null}
