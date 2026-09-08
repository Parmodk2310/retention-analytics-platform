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
export type RiskBand =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type ChurnReason = {
  feature: string
  impact: number
  direction:
    | 'increases_risk'
    | 'reduces_risk'
}

export type ChurnScore = {
  user_id: string
  external_id: string
  snapshot_date: string
  score: number
  risk_band: RiskBand
  model_version: string
  reasons: ChurnReason[]
  scored_at: string
  acquisition_channel: string
  device_type: string
}

export type ChurnSummary = {
  snapshot_date: string | null
  model_version: string | null
  total_scored: number
  average_score: number
  high_risk_count: number
  risk_bands: Record<RiskBand, number>
}

export type FeatureImportance = {
  feature: string
  importance: number
}

export type ModelDatasetMetadata = {
  feature_window_days: number
  label_window_days: number
  snapshot_count: number
}

export type ModelSplit = {
  rows: number
  snapshot_count: number
  start: string
  end: string
  churn_rate: number
}

export type ModelSplits = {
  train: ModelSplit
  validation: ModelSplit
  test: ModelSplit
}

export type ModelCalibration = {
  method: string
  fit_rows: number
  calibration_rows: number
  calibration_snapshot: string
}

export type ModelRiskBands = {
  method: string
  thresholds: {
    critical: number
    high: number
    medium: number
  }
}

export type ModelLabelDrift = {
  train_prevalence: number
  validation_prevalence: number
  test_prevalence: number
  train_to_test_pp: number
}

export type ModelHealth = {
  model_version: string
  algorithm: string
  metrics: Record<string, number>
  feature_names: string[]
  trained_at: string
  artifact_uri: string | null

  dataset: ModelDatasetMetadata | null
  splits: ModelSplits | null
  calibration: ModelCalibration | null
  risk_bands: ModelRiskBands | null
  label_drift: ModelLabelDrift | null

  global_feature_importance:
    FeatureImportance[]

  validation_candidates:
    | Record<
        string,
        Record<string, number>
      >
    | null
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
