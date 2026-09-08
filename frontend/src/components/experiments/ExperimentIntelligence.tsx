import { Card } from '@/components/ui/Card'
import type { ExperimentAnalysis, ExperimentResults } from '@/types/api'

interface Props {
  result: ExperimentResults
  metricLabel?: string
}

const percentage = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : `${(value * 100).toFixed(digits)}%`

const percentagePoints = (value: number | null | undefined) =>
  value == null ? '—' : `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)} pp`

const fixed = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : value.toFixed(digits)

function Stat({
  label,
  value,
  note,
}: {
  label: string
  value: string
  note?: string
}) {
  return (
    <div className="rounded-xl border bg-background/40 p-4">
      <p className="text-xs font-medium uppercase tracking-wide opacity-50">{label}</p>
      <p className="mt-2 text-xl font-semibold tabular-nums">{value}</p>
      {note && <p className="mt-1 text-xs opacity-50">{note}</p>}
    </div>
  )
}

function Inference({ analysis }: { analysis: ExperimentAnalysis }) {
  const [lower, upper] = analysis.difference_ci

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Stat
        label="Absolute lift"
        value={percentagePoints(analysis.absolute_lift)}
        note={`95% CI ${percentagePoints(lower)} to ${percentagePoints(upper)}`}
      />
      <Stat
        label="Relative lift"
        value={percentage(analysis.relative_lift)}
        note={`z = ${fixed(analysis.z_stat)} · p = ${analysis.p_value.toFixed(4)}`}
      />
      <Stat
        label="Control rate"
        value={percentage(analysis.control_rate)}
        note="Observed control conversion"
      />
      <Stat
        label="Treatment rate"
        value={percentage(analysis.treatment_rate)}
        note={analysis.significant ? 'Statistically significant' : 'Not statistically significant'}
      />
    </div>
  )
}

export function ExperimentIntelligence({
  result,
  metricLabel = 'Primary conversion metric',
}: Props) {
  const variants = Object.entries(result.conversion_rates).map(
    ([variant, conversionRate]) => ({
      variant,
      conversionRate,
      n: result.counts[variant] ?? 0,
    }),
  )
  const matureExposures = Object.values(result.counts).reduce((total, count) => total + count, 0)

  return (
    <Card className="space-y-5 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">Experiment intelligence</h3>
          <p className="mt-1 text-sm opacity-60">{metricLabel}</p>
        </div>

        <span
          className={
            result.srm.detected
              ? 'rounded-full border border-danger/30 bg-danger/10 px-3 py-1 text-xs font-semibold text-danger'
              : 'rounded-full border border-success/30 bg-success/10 px-3 py-1 text-xs font-semibold text-success'
          }
        >
          {result.srm.detected ? 'SRM detected' : 'Assignment healthy'}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {variants.map((variant) => (
          <div key={variant.variant} className="rounded-xl border bg-background/40 p-5">
            <div className="flex items-center justify-between">
              <span className="font-medium capitalize">
                {variant.variant.replaceAll('_', ' ')}
              </span>
              <span className="text-xs opacity-50">n={variant.n.toLocaleString()}</span>
            </div>
            <p className="mt-3 text-3xl font-semibold tabular-nums">
              {percentage(variant.conversionRate)}
            </p>
          </div>
        ))}
      </div>

      {result.analysis ? (
        <Inference analysis={result.analysis} />
      ) : (
        <div className="rounded-xl border p-4 text-sm opacity-60">
          More mature exposure data is required before statistical inference.
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-3">
        <Stat
          label="SRM p-value"
          value={result.srm.p_value.toFixed(4)}
          note="Chi-square allocation check"
        />
        <Stat
          label="Mature exposures"
          value={matureExposures.toLocaleString()}
          note="Users included in current analysis"
        />
        <Stat
          label="Decision"
          value={result.decision.replaceAll('_', ' ')}
          note={
            result.analysis?.significant
              ? 'Statistically significant'
              : 'Not statistically significant'
          }
        />
      </div>
    </Card>
  )
}
