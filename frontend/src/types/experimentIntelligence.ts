export type ExperimentDecision =
  | "investigate_srm"
  | "do_not_ship_guardrail_regression"
  | "collect_more_data"
  | "ship_treatment"
  | "stop_treatment"
  | "inconclusive_collect_more_data";

export interface ExperimentMetric {
  key: string;
  label: string;
  event_name: string;
  window_days: number;
}

export interface VariantResult {
  variant: string;
  n: number;
  conversions: number;
  conversion_rate: number;
}

export interface SrmResult {
  alpha: number;
  total: number;
  observed: Record<string, number>;
  expected: Record<string, number>;
  method: "exact_binomial" | "pearson_chi_square" | "not_tested";
  tested: boolean;
  detected: boolean;
  chi_square: number;
  p_value: number;
  reason: "no_exposures" | "insufficient_expected_count" | null;
}

export interface EffectSizeResult {
  risk_difference: number;
  relative_lift: number | null;
  risk_ratio: number | null;
  odds_ratio: number | null;
  number_needed: number | null;
  number_needed_type: "nnt" | "nnh" | null;
  direction: "positive" | "negative" | "neutral";
}

export interface PowerResult {
  alpha: number;
  target_power: number;
  allocation_ratio: number;
  control_n: number;
  treatment_n: number;
  target_relative_lift: number;
  target_absolute_lift: number;
  power_at_target_effect: number;
  mde_absolute: number;
  mde_relative: number;
  required_control_n: number;
  required_treatment_n: number;
  adequately_powered_for_target: boolean;
}

export interface BinaryAnalysis {
  control_rate: number;
  treatment_rate: number;
  absolute_lift: number;
  relative_lift: number | null;
  standard_error: number;
  z_stat: number;
  p_value: number;
  difference_ci: [number, number];
  confidence_level: number;
  alpha: number;
  significant: boolean;
  effect_size: EffectSizeResult;
  power: PowerResult | null;
}

export interface ExperimentIntelligenceResult {
  experiment_id: string;
  metric: ExperimentMetric;
  variants: VariantResult[];
  counts: Record<string, number>;
  conversion_rates: Record<string, number>;
  srm: SrmResult;
  analysis: BinaryAnalysis | null;
  decision: ExperimentDecision;
}