export type Account = {
  id: string
  email: string
  full_name: string | null
}

export type Overview = {
  as_of_date: string
  dau: number
  wau: number
  mau: number
  stickiness: number
  revenue: number
  arpu: number
  purchasers: number
  new_users: number
}

export type ActivityPoint = {
  date: string
  active_users: number
  sessions: number
  revenue: number
}

export type FunnelStage = {
  stage: string
  users: number
  conversion_from_previous: number
  dropoff_from_previous: number
}

export type CohortCell = {
  cohort_month: string
  acquisition_channel: string | null
  period_month: number
  retained_users: number
  cohort_size: number
  retention_rate: number
}

export type RevenuePoint = {
  month: string
  revenue: number
  purchasers: number
  orders: number
}

export type ChannelPerformance = {
  acquisition_channel: string
  users: number
  purchasers: number
  revenue: number
}

export type ChurnScore = {
  user_id: string
  external_id: string
  snapshot_date: string
  score: number
  risk_band: 'low' | 'medium' | 'high' | 'critical'
  model_version: string
  reasons: string[]
}

export type ModelHealth = {
  model_version: string
  algorithm: string
  metrics: Record<string, number>
  trained_at: string
  artifact_uri: string
}

export type Experiment = {
  id: string
  key: string
  name: string
  hypothesis: string
  primary_metric: string
  variants: string[]
  traffic_allocation: Record<string, number>
  status: string
  starts_at: string | null
  ends_at: string | null
}

export type SampleRatioMismatch = {
  chi_square?: number
  p_value: number
  detected: boolean
  observed: Record<string, number>
  expected: Record<string, number>
}

export type ExperimentAnalysis = {
  control_rate: number
  treatment_rate: number
  absolute_lift: number
  relative_lift: number | null
  z_stat: number
  p_value: number
  difference_ci: [number, number]
  significant: boolean
  alpha: number
}

export type ExperimentResults = {
  experiment_id: string
  counts: Record<string, number>
  conversion_rates: Record<string, number>
  srm: SampleRatioMismatch
  analysis: ExperimentAnalysis | null
  decision: string
}
