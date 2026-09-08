import { useQueries } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { DecisionBadge } from '@/components/experiments/DecisionBadge'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useExperiments } from '@/hooks/useExperiments'
import { experimentApi } from '@/services/experimentApi'

const percentage = (value: number | null | undefined) =>
  value == null ? '—' : `${(value * 100).toFixed(2)}%`

const humanize = (value: string) =>
  value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())

function SummaryCard({
  label,
  value,
  note,
}: {
  label: string
  value: string
  note: string
}) {
  return (
    <Card className="p-4">
      <p className="text-xs font-medium uppercase tracking-wide opacity-50">{label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
      <p className="mt-1 text-xs opacity-50">{note}</p>
    </Card>
  )
}

export default function Experiments() {
  const query = useExperiments()
  const experiments = query.data ?? []

  const resultQueries = useQueries({
    queries: experiments.map((experiment) => ({
      queryKey: ['experiment-results', experiment.id],
      queryFn: () => experimentApi.results(experiment.id),
      staleTime: 60_000,
    })),
  })

  if (query.isLoading && !query.data) {
    return (
      <div className="space-y-4">
        <div className="grid gap-3 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-48" />
      </div>
    )
  }

  if (query.error) return <ErrorState onRetry={() => query.refetch()} />

  const results = resultQueries.flatMap((result) => (result.data ? [result.data] : []))
  const resultById = new Map(
    experiments.map((experiment, index) => [
      experiment.id,
      resultQueries[index]?.data,
    ]),
  )

  const running = experiments.filter((experiment) => experiment.status === 'running').length
  const matureExposures = results.reduce((total, result) => total + result.srm.total, 0)
  const significant = results.filter((result) => result.analysis?.significant).length
  const srmAlerts = results.filter((result) => result.srm.detected).length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Experiments</h2>
        <p className="mt-1 text-sm opacity-60">
          Deterministic assignment, mature post-exposure outcomes and production statistical inference.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Running"
          value={running.toLocaleString()}
          note={`${experiments.length} experiment${experiments.length === 1 ? '' : 's'} configured`}
        />
        <SummaryCard
          label="Mature exposures"
          value={matureExposures.toLocaleString()}
          note="Completed outcome windows"
        />
        <SummaryCard
          label="Significant results"
          value={significant.toLocaleString()}
          note="Current production analyses"
        />
        <SummaryCard
          label="SRM alerts"
          value={srmAlerts.toLocaleString()}
          note={srmAlerts ? 'Instrumentation review required' : 'Assignment health normal'}
        />
      </div>

      {!experiments.length ? (
        <EmptyState
          title="No experiments configured"
          description="Create an experiment through the API or seed the demonstration experiment."
        />
      ) : (
        <div className="space-y-3">
          {experiments.map((experiment) => {
            const result = resultById.get(experiment.id)
            const control = result?.variants.find((variant) => variant.variant === 'control')
            const treatment = result?.variants.find((variant) => variant.variant === 'treatment')
            const relativeLift = result?.analysis?.relative_lift

            return (
              <Link
                key={experiment.id}
                to={`/experiments/${experiment.id}`}
                className="block"
              >
                <Card className="p-5 transition hover:-translate-y-0.5 hover:border-primary/30">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="font-semibold">{experiment.name}</h3>
                        <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                          {humanize(experiment.status)}
                        </span>
                      </div>

                      <p className="mt-2 max-w-3xl text-sm opacity-60">
                        {experiment.hypothesis}
                      </p>

                      <p className="mt-3 text-xs opacity-50">
                        {experiment.primary_metric} ·{' '}
                        {experiment.variants
                          .map(
                            (variant) =>
                              `${humanize(variant)} ${(
                                (experiment.traffic_allocation[variant] ?? 0) * 100
                              ).toFixed(0)}%`,
                          )
                          .join(' / ')}
                      </p>
                    </div>

                    {result && <DecisionBadge decision={result.decision} />}
                  </div>

                  {result ? (
                    <div className="mt-5 grid gap-3 border-t pt-4 sm:grid-cols-2 lg:grid-cols-4">
                      <div>
                        <p className="text-xs uppercase tracking-wide opacity-40">Control</p>
                        <p className="mt-1 text-lg font-semibold tabular-nums">
                          {percentage(control?.conversion_rate)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide opacity-40">Treatment</p>
                        <p className="mt-1 text-lg font-semibold tabular-nums">
                          {percentage(treatment?.conversion_rate)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide opacity-40">Relative lift</p>
                        <p className="mt-1 text-lg font-semibold tabular-nums">
                          {relativeLift == null
                            ? '—'
                            : `${relativeLift >= 0 ? '+' : ''}${percentage(relativeLift)}`}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide opacity-40">Analysis health</p>
                        <p
                          className={`mt-1 text-sm font-semibold ${
                            result.srm.detected ? 'text-danger' : 'text-success'
                          }`}
                        >
                          {result.srm.detected ? 'SRM detected' : 'Assignment healthy'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="mt-5 border-t pt-4 text-xs opacity-50">
                      Loading experiment analysis…
                    </p>
                  )}
                </Card>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}