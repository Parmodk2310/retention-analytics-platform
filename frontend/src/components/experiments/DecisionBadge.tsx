import type { ExperimentDecision } from '@/types/api'

const labels: Record<ExperimentDecision, string> = {
  investigate_srm: 'Investigate SRM',
  do_not_ship_guardrail_regression: 'Do Not Ship',
  collect_more_data: 'Collect More Data',
  ship_treatment: 'Ship Treatment',
  stop_treatment: 'Stop Treatment',
  inconclusive_collect_more_data: 'Inconclusive',
}

const styles: Record<ExperimentDecision, string> = {
  investigate_srm: 'border-warning/30 bg-warning/10 text-warning',
  do_not_ship_guardrail_regression: 'border-danger/30 bg-danger/10 text-danger',
  collect_more_data: 'border-warning/30 bg-warning/10 text-warning',
  ship_treatment: 'border-success/30 bg-success/10 text-success',
  stop_treatment: 'border-danger/30 bg-danger/10 text-danger',
  inconclusive_collect_more_data: 'border-warning/30 bg-warning/10 text-warning',
}

export function DecisionBadge({ decision }: { decision: ExperimentDecision }) {
  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-semibold ${styles[decision]}`}
    >
      {labels[decision]}
    </span>
  )
}