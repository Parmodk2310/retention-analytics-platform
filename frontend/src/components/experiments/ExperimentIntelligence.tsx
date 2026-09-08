import { DecisionBadge } from '@/components/experiments/DecisionBadge'
import { Card } from '@/components/ui/Card'
import type {
  ExperimentAnalysis,
  ExperimentResults,
  ExperimentVariantResult,
} from '@/types/api'

interface Props {
  result: ExperimentResults
}

const percentage = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : `${(value * 100).toFixed(digits)}%`

const percentagePoints = (value: number | null | undefined) =>
  value == null ? '—' : `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)} pp`

const fixed = (value: number | null | undefined, digits = 2) =>
  value == null ? '—' : value.toFixed(digits)

const humanize = (value: string) =>
  value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())

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
      <p className="text-xs font-medium uppercase tracking-wide opacity-45">{label}</p>
      <p className="mt-2 text-xl font-semibold tabular-nums">{value}</p>
      {note && <p className="mt-1 text-xs leading-relaxed opacity-50">{note}</p>}
    </div>
  )
}

function Section({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <section className="space-y-3">
      <div>
        <h4 className="font-semibold">{title}</h4>
        <p className="mt-1 text-xs opacity-50">{description}</p>
      </div>
      {children}
    </section>
  )
}

function VariantComparison({
  variants,
}: {
  variants: ExperimentVariantResult[]
}) {
  const maxRate = Math.max(...variants.map((variant) => variant.conversion_rate), 0.0001)

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {variants.map((variant) => {
        const width = Math.max((variant.conversion_rate / maxRate) * 100, 2)
        const treatment = variant.variant === 'treatment'

        return (
          <div key={variant.variant} className="rounded-xl border bg-background/40 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-medium">{humanize(variant.variant)}</p>
                <p className="mt-3 text-3xl font-semibold tabular-nums">
                  {percentage(variant.conversion_rate)}
                </p>
              </div>

              <p className="text-right text-xs opacity-50">
                n={variant.n.toLocaleString()}
                <br />
                {variant.conversions.toLocaleString()} conversions
              </p>
            </div>

            <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full rounded-full ${
                  treatment ? 'bg-success' : 'bg-primary'
                }`}
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ObservedEffect({ analysis }: { analysis: ExperimentAnalysis }) {
  const effect = analysis.effect_size
  const [lower, upper] = analysis.difference_ci

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Stat
        label="Absolute lift"
        value={percentagePoints(analysis.absolute_lift)}
        note={`${Math.round(analysis.confidence_level * 100)}% CI ${percentagePoints(
          lower,
        )} to ${percentagePoints(upper)}`}
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
        label={effect.number_needed_type?.toUpperCase() ?? 'NNT'}
        value={fixed(effect.number_needed, 1)}
        note={`Effect direction: ${effect.direction}`}
      />
    </div>
  )
}

export function ExperimentIntelligence({ result }: Props) {
  const analysis = result.analysis
  const power = analysis?.power

  const srmMethod = {
    exact_binomial: 'Exact binomial allocation check',
    pearson_chi_square: 'Pearson chi-square allocation check',
    not_tested: 'Allocation check not performed',
  }[result.srm.method]

  const heroTone = result.srm.detected
    ? 'border-danger/30 bg-danger/10'
    : result.decision === 'ship_treatment'
      ? 'border-success/30 bg-success/5'
      : 'bg-background/40'

  return (
    <div className="space-y-5">
      <Card className={`p-5 ${heroTone}`}>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-50">
              Experiment decision
            </p>

            <h3 className="mt-2 text-2xl font-semibold">
              {humanize(result.decision)}
            </h3>

            {analysis ? (
              <p className="mt-2 text-sm opacity-70">
                {percentagePoints(analysis.absolute_lift)} absolute ·{' '}
                {percentage(analysis.relative_lift)} relative · p=
                {analysis.p_value.toFixed(4)}
              </p>
            ) : (
              <p className="mt-2 text-sm opacity-60">
                More mature outcome data is required before inference.
              </p>
            )}

            {analysis && (
              <p className="mt-1 text-xs opacity-50">
                {Math.round(analysis.confidence_level * 100)}% CI{' '}
                {percentagePoints(analysis.difference_ci[0])} to{' '}
                {percentagePoints(analysis.difference_ci[1])}
              </p>
            )}
          </div>

          <div className="flex flex-col items-end gap-2">
            <DecisionBadge decision={result.decision} />
            <span
              className={`text-xs font-medium ${
                result.srm.detected ? 'text-danger' : 'text-success'
              }`}
            >
              {result.srm.detected ? 'Assignment issue detected' : 'Assignment healthy'}
            </span>
          </div>
        </div>
      </Card>

      <Card className="space-y-6 p-5">
        <div>
          <h3 className="text-lg font-semibold">Experiment intelligence</h3>
          <p className="mt-1 text-sm opacity-60">
            {result.metric.label} · {result.metric.window_days}-day mature outcome window
          </p>
        </div>

        <Section
          title="Conversion comparison"
          description="Observed conversion among users with completed outcome windows."
        >
          <VariantComparison variants={result.variants} />
        </Section>

        {analysis ? (
          <Section
            title="Observed treatment effect"
            description="Frequentist effect estimates and practical effect-size diagnostics."
          >
            <ObservedEffect analysis={analysis} />
          </Section>
        ) : (
          <div className="rounded-xl border p-4 text-sm opacity-60">
            More mature exposure data is required before statistical inference.
          </div>
        )}

        <Section
          title="Experiment health"
          description="Assignment balance, sample maturity and statistical reliability."
        >
          <div className="grid gap-3 md:grid-cols-3">
            <Stat
              label="SRM p-value"
              value={result.srm.p_value.toFixed(4)}
              note={srmMethod}
            />
            <Stat
              label="Mature exposures"
              value={result.srm.total.toLocaleString()}
              note={`${result.metric.window_days}-day outcome windows complete`}
            />
            <Stat
              label="Significance"
              value={analysis?.significant ? 'Yes' : 'No'}
              note={
                analysis
                  ? `${Math.round(analysis.confidence_level * 100)}% confidence level`
                  : 'Inference unavailable'
              }
            />
          </div>
        </Section>

        {power && (
          <Section
            title="Planning diagnostics"
            description="Prospective sensitivity for future experiment planning — not post-hoc proof of the observed result."
          >
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Stat
                label={`Power for ${percentage(power.target_relative_lift, 0)} target`}
                value={percentage(power.power_at_target_effect)}
                note="Prospective power for target relative lift"
              />
              <Stat
                label="Target power"
                value={percentage(power.target_power, 0)}
                note={
                  power.adequately_powered_for_target
                    ? 'Current sample is adequate'
                    : 'More sample required'
                }
              />
              <Stat
                label={`${percentage(power.target_power, 0)} MDE`}
                value={percentage(power.mde_relative)}
                note={`${percentagePoints(power.mde_absolute)} absolute`}
              />
              <Stat
                label="Required sample"
                value={(
                  power.required_control_n + power.required_treatment_n
                ).toLocaleString()}
                note={`${power.required_control_n.toLocaleString()} control · ${power.required_treatment_n.toLocaleString()} treatment`}
              />
            </div>
          </Section>
        )}

        <div className="rounded-xl border bg-background/30 p-4 text-xs leading-relaxed opacity-55">
          <b className="text-foreground">Methodology:</b> deterministic assignment ·
          post-exposure outcomes · mature {result.metric.window_days}-day windows ·{' '}
          {srmMethod.toLowerCase()} · two-proportion z-test ·{' '}
          {analysis
            ? `${Math.round(analysis.confidence_level * 100)}% confidence interval`
            : 'inference pending'}
          .
        </div>
      </Card>
    </div>
  )
}