import { Card } from '@/components/ui/Card'
import type {
  ExperimentAnalysis,
  ExperimentResults,
  SampleRatioMismatch,
} from '@/types/api'

interface Props {
  result: ExperimentResults
}

const SRM_LABELS: Record<SampleRatioMismatch['method'], string> = {
  exact_binomial: 'Exact binomial allocation check',
  pearson_chi_square: 'Pearson chi-square allocation check',
  not_tested: 'Allocation check not performed',
}

const percentage = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : `${(value * 100).toFixed(digits)}%`

const percentagePoints = (value: number | null | undefined) =>
  value == null ? '—' : `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)} pp`

const fixed = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : value.toFixed(digits)

const title = (value: string) =>
  value.replaceAll('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase())

function Stat({ label, value, note }: { label: string; value: string; note?: string }) {
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
  const effect = analysis.effect_size
  const power = analysis.power
  const confidence = Math.round(analysis.confidence_level * 100)

  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          label="Absolute lift"
          value={percentagePoints(analysis.absolute_lift)}
          note={`${confidence}% CI ${percentagePoints(lower)} to ${percentagePoints(upper)}`}
        />
        <Stat
          label="Relative lift"
          value={percentage(analysis.relative_lift)}
          note={`z = ${fixed(analysis.z_stat)} · p = ${analysis.p_value.toFixed(4)}`}
        />
        <Stat
          label="Risk ratio"
          value={fixed(effect.risk_ratio, 3)}
          note={`Odds ratio ${fixed(effect.odds_ratio, 3)}`}
        />
        <Stat
          label={effect.number_needed_type?.toUpperCase() ?? 'Number needed'}
          value={fixed(effect.number_needed, 1)}
          note={`Effect direction: ${effect.direction}`}
        />
      </div>

      {power && (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Stat
            label={`Power for ${percentage(power.target_relative_lift, 0)} target`}
            value={percentage(power.power_at_target_effect)}
            note="Prospective power for target relative lift"
          />
          <Stat
            label="Target power"
            value={percentage(power.target_power, 0)}
            note={power.adequately_powered_for_target ? 'Current sample meets target' : 'More sample required'}
          />
          <Stat
            label={`${percentage(power.target_power, 0)} MDE`}
            value={percentage(power.mde_relative)}
            note={`${percentagePoints(power.mde_absolute)} absolute`}
          />
          <Stat
            label="Required sample"
            value={(power.required_control_n + power.required_treatment_n).toLocaleString()}
            note={`${power.required_control_n.toLocaleString()} control · ${power.required_treatment_n.toLocaleString()} treatment`}
          />
        </div>
      )}
    </div>
  )
}

export function ExperimentIntelligence({ result }: Props) {
  return (
    <Card className="space-y-5 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">Experiment intelligence</h3>
          <p className="mt-1 text-sm opacity-60">
            {result.metric.label} · {result.metric.window_days}-day outcome window
          </p>
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
        {result.variants.map((variant) => (
          <div key={variant.variant} className="rounded-xl border bg-background/40 p-5">
            <div className="flex items-center justify-between gap-3">
              <span className="font-medium capitalize">
                {variant.variant.replaceAll('_', ' ')}
              </span>
              <span className="text-xs opacity-50">n={variant.n.toLocaleString()}</span>
            </div>

            <p className="mt-3 text-3xl font-semibold tabular-nums">
              {percentage(variant.conversion_rate)}
            </p>
            <p className="mt-1 text-xs opacity-50">
              {variant.conversions.toLocaleString()} conversions
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
          value={result.srm.tested ? result.srm.p_value.toFixed(4) : '—'}
          note={SRM_LABELS[result.srm.method]}
        />
        <Stat
          label="Mature exposures"
          value={result.srm.total.toLocaleString()}
          note="Users with completed outcome windows"
        />
        <Stat
          label="Decision"
          value={title(result.decision)}
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