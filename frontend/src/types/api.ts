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

/* -------------------------------------------------------------------------- */
/* Churn intelligence                                                         */
/* -------------------------------------------------------------------------- */

export type RiskBand = 'low' | 'medium' | 'high' | 'critical'

export type ChurnReason = {
  feature: string
  label: string
  impact: number
  direction: 'increases_risk' | 'reduces_risk'
}

export type ChurnScore = {
  user_id: string
  external_id: string
  snapshot_date: string
  score: number
  risk_band: RiskBand
  model_version: string
  acquisition_channel: string
  device_type: string
  reasons: ChurnReason[]
  scored_at: string
}

export type ChurnSummary = {
  snapshot_date: string | null
  model_version: string | null
  total_scored: number
  average_score: number
  high_risk_count: number
  risk_bands: Record<RiskBand, number>
}

/* -------------------------------------------------------------------------- */
/* Model health                                                               */
/* -------------------------------------------------------------------------- */

export type FeatureImportance = {
  feature: string
  label: string
  importance: number
}

export type ModelDataset = {
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

export type CalibrationMetadata = {
  method: string
  fit_rows: number
  calibration_rows: number
  calibration_snapshot: string
}

export type RiskBandPolicy = {
  method: string
  thresholds: {
    critical: number
    high: number
    medium: number
  }
}

export type LabelDrift = {
  train_prevalence: number
  validation_prevalence: number
  test_prevalence: number
  train_to_test_pp: number
}

export type ValidationCandidate = {
  uncalibrated: Record<string, number>
  calibrated: Record<string, number>
}

export type ModelHealth = {
  model_version: string
  algorithm: string
  metrics: Record<string, number>
  feature_names: string[]
  trained_at: string
  artifact_uri: string
  dataset: ModelDataset | null
  splits: ModelSplits | null
  calibration: CalibrationMetadata | null
  risk_bands: RiskBandPolicy | null
  label_drift: LabelDrift | null
  global_feature_importance: FeatureImportance[]
  validation_candidates: Record<string, ValidationCandidate> | null
}

/* -------------------------------------------------------------------------- */
/* Experiments                                                                */
/* -------------------------------------------------------------------------- */

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

export type ExperimentCreatePayload = {
  key: string
  name: string
  hypothesis: string
  primary_metric?: string
  variants: string[]
  traffic_allocation: Record<string, number>
  starts_at?: string | null
  ends_at?: string | null
}

export type AssignmentResponse = {
  experiment_id: string
  user_id: string
  variant: string
}

export type ExposureResponse = {
  variant: string
  status: 'exposed'
}

export type ExperimentMetric = {
  key: string
  label: string
  event_name: string
  window_days: number
}

export type ExperimentVariantResult = {
  variant: string
  n: number
  conversions: number
  conversion_rate: number
}

export type SrmMethod =
  | 'exact_binomial'
  | 'pearson_chi_square'
  | 'not_tested'

export type SrmReason =
  | 'no_exposures'
  | 'insufficient_expected_count'
  | null

export type SampleRatioMismatch = {
  alpha: number
  total: number
  observed: Record<string, number>
  expected: Record<string, number>
  method: SrmMethod
  tested: boolean
  detected: boolean
  chi_square: number
  p_value: number
  reason: SrmReason
}

export type EffectDirection = 'positive' | 'negative' | 'neutral'
export type NumberNeededType = 'nnt' | 'nnh' | null

export type ExperimentEffectSize = {
  risk_difference: number
  relative_lift: number | null
  risk_ratio: number | null
  odds_ratio: number | null
  number_needed: number | null
  number_needed_type: NumberNeededType
  direction: EffectDirection
}

export type ExperimentPower = {
  alpha: number
  target_power: number
  allocation_ratio: number
  control_n: number
  treatment_n: number
  target_relative_lift: number
  target_absolute_lift: number
  power_at_target_effect: number
  mde_absolute: number
  mde_relative: number
  required_control_n: number
  required_treatment_n: number
  adequately_powered_for_target: boolean
}

export type ExperimentAnalysis = {
  control_rate: number
  treatment_rate: number
  absolute_lift: number
  relative_lift: number | null
  standard_error: number
  z_stat: number
  p_value: number
  difference_ci: [number, number]
  confidence_level: number
  alpha: number
  significant: boolean
  effect_size: ExperimentEffectSize
  power: ExperimentPower | null
}

export type ExperimentDecision =
  | 'investigate_srm'
  | 'do_not_ship_guardrail_regression'
  | 'collect_more_data'
  | 'ship_treatment'
  | 'stop_treatment'
  | 'inconclusive_collect_more_data'

export type ExperimentResults = {
  experiment_id: string
  metric: ExperimentMetric
  variants: ExperimentVariantResult[]
  counts: Record<string, number>
  conversion_rates: Record<string, number>
  srm: SampleRatioMismatch
  analysis: ExperimentAnalysis | null
  decision: ExperimentDecision
}


/* -------------------------------------------------------------------------- */
/* System health                                                              */
/* -------------------------------------------------------------------------- */

export type SystemFeatures = {
  realtime: boolean
  churn_ml: boolean
  experimentation: boolean
}

export type SystemInfo = {
  environment: string
  version: string
  features: SystemFeatures
}

export type EventPipelineStatus = {
  status: 'fresh' | 'stale' | 'unknown'
  last_persisted_at: string | null
  latest_event_time: string | null
  last_stream_id: string | null
  freshness_seconds: number | null
  pending: number
  lag: number
  backlog: number
}