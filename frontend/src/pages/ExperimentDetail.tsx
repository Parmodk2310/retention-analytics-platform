import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { DecisionBadge } from '@/components/experiments/DecisionBadge'
import { ExperimentIntelligence } from '@/components/experiments/ExperimentIntelligence'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { percent } from '@/lib/formatters'
import { experimentApi } from '@/services/experimentApi'

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
    return <p className="opacity-60">Loading experiment result…</p>
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

  if (!result) {
    return <p className="opacity-60">No experiment result is available yet.</p>
  }

  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <p className="text-sm opacity-60">Experiments</p>

        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-2xl font-semibold">
            {experiment?.name ?? 'Experiment Analysis'}
          </h2>
          <DecisionBadge decision={result.decision} />
        </div>

        {experiment && (
          <div className="space-y-1 text-sm opacity-60">
            <p>{experiment.hypothesis}</p>
            <p>
              Primary metric:{' '}
              <span className="font-medium text-foreground">
                {experiment.primary_metric}
              </span>
            </p>
          </div>
        )}
      </div>

      {result.srm.detected && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm">
          <b>Sample Ratio Mismatch detected.</b> Do not trust the treatment conclusion until
          assignment or instrumentation is investigated. p={result.srm.p_value.toPrecision(3)}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {['control', 'treatment']
          .filter((variant) => variant in result.conversion_rates)
          .map((variant) => {
            const conversionRate = result.conversion_rates[variant]

            return (
              <Card key={variant} className="p-5">
                <p className="text-sm capitalize opacity-60">{variant}</p>
                <p className="mt-2 text-3xl font-semibold">{percent(conversionRate)}</p>
                <p className="text-xs opacity-50">
                  n={result.counts[variant]?.toLocaleString() ?? '0'}
                </p>
              </Card>
            )
          })}
      </div>

      {result.analysis && (
        <Card className="p-5">
          <h3 className="font-semibold">Frequentist analysis</h3>
          <div className="mt-4 grid gap-3 text-sm md:grid-cols-4">
            <div>
              Absolute lift
              <br />
              <b>
                {result.analysis.absolute_lift >= 0 ? '+' : ''}
                {(result.analysis.absolute_lift * 100).toFixed(1)} pp
              </b>
            </div>
            <div>
              Relative lift
              <br />
              <b>
                {result.analysis.relative_lift == null
                  ? '—'
                  : `${result.analysis.relative_lift >= 0 ? '+' : ''}${percent(
                      result.analysis.relative_lift,
                    )}`}
              </b>
            </div>
            <div>
              p-value
              <br />
              <b>{result.analysis.p_value.toFixed(4)}</b>
            </div>
            <div>
              Significant
              <br />
              <b>{result.analysis.significant ? 'Yes' : 'No'}</b>
            </div>
          </div>
        </Card>
      )}

      <ExperimentIntelligence
        result={result}
        metricLabel={experiment?.primary_metric}
      />
    </div>
  )
}
