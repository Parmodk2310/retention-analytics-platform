import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { ExperimentIntelligence } from '@/components/experiments/ExperimentIntelligence'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { experimentApi } from '@/services/experimentApi'

const dateTime = new Intl.DateTimeFormat('en-IN', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'Asia/Kolkata',
})

const humanize = (value: string) =>
  value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())

function Meta({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide opacity-40">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  )
}

export default function ExperimentDetail() {
  const { id = '' } = useParams()

  const resultsQuery = useQuery({
    queryKey: ['experiment-results', id],
    queryFn: () => experimentApi.results(id),
    enabled: Boolean(id),
  })

  const experimentsQuery = useQuery({
    queryKey: ['experiments'],
    queryFn: experimentApi.list,
  })

  const experiment = experimentsQuery.data?.find((item) => item.id === id)

  if (resultsQuery.isLoading || experimentsQuery.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-24" />
        <Skeleton className="h-[620px]" />
      </div>
    )
  }

  if (resultsQuery.error || experimentsQuery.error) {
    return (
      <ErrorState
        onRetry={() => {
          void resultsQuery.refetch()
          void experimentsQuery.refetch()
        }}
      />
    )
  }

  const result = resultsQuery.data
  if (!result) return <p className="opacity-60">No experiment result is available yet.</p>

  const allocation = experiment
    ? experiment.variants
        .map(
          (variant) =>
            `${humanize(variant)} ${(
              (experiment.traffic_allocation[variant] ?? 0) * 100
            ).toFixed(0)}%`,
        )
        .join(' / ')
    : '—'

  return (
    <div className="space-y-5">
      <div>
        <Link
          to="/experiments"
          className="text-sm opacity-50 transition hover:opacity-100"
        >
          ← Experiments
        </Link>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h2 className="text-2xl font-semibold">
            {experiment?.name ?? 'Experiment Analysis'}
          </h2>

          {experiment && (
            <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
              {humanize(experiment.status)}
            </span>
          )}
        </div>

        {experiment && (
          <p className="mt-2 max-w-3xl text-sm opacity-60">
            {experiment.hypothesis}
          </p>
        )}
      </div>

      <Card className="grid gap-5 p-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Meta label="Status" value={humanize(experiment?.status ?? 'unknown')} />
        <Meta label="Metric" value={result.metric.label} />
        <Meta label="Outcome window" value={`${result.metric.window_days} days`} />
        <Meta label="Allocation" value={allocation} />
        <Meta
          label="Starts"
          value={
            experiment?.starts_at
              ? dateTime.format(new Date(experiment.starts_at))
              : 'No fixed start'
          }
        />
        <Meta
          label="Ends"
          value={
            experiment?.ends_at
              ? dateTime.format(new Date(experiment.ends_at))
              : 'Open-ended'
          }
        />
      </Card>

      {result.srm.detected && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm">
          <b>Sample Ratio Mismatch detected.</b> Treatment conclusions should not be
          trusted until assignment or instrumentation is investigated. SRM p=
          {result.srm.p_value.toPrecision(3)}.
        </div>
      )}

      <ExperimentIntelligence result={result} />
    </div>
  )
}