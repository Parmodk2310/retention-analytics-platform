import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { DecisionBadge } from '@/components/experiments/DecisionBadge'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { percent } from '@/lib/formatters'
import { experimentApi } from '@/services/experimentApi'

export default function ExperimentDetail() {
  const { id = '' } = useParams()

  const query = useQuery({
    queryKey: ['experiment-results', id],
    queryFn: () => experimentApi.results(id),
    enabled: Boolean(id),
  })

  if (query.isLoading) {
    return <p className="opacity-60">Loading experiment result…</p>
  }

  if (query.error) {
    return <ErrorState onRetry={() => query.refetch()} />
  }

  const result = query.data

  if (!result) {
    return <p className="opacity-60">No experiment result is available yet.</p>
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <h2 className="text-2xl font-semibold">Experiment result</h2>
        <DecisionBadge decision={result.decision} />
      </div>

      {result.srm.detected && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm">
          <b>Sample Ratio Mismatch detected.</b> Do not trust the treatment conclusion until
          assignment or instrumentation is investigated. p={result.srm.p_value.toPrecision(3)}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(result.conversion_rates).map(([variant, conversionRate]) => (
          <Card key={variant} className="p-5">
            <p className="text-sm opacity-60">{variant}</p>
            <p className="mt-2 text-3xl font-semibold">{percent(conversionRate)}</p>
            <p className="text-xs opacity-50">
              n={result.counts[variant]?.toLocaleString() ?? '0'}
            </p>
          </Card>
        ))}
      </div>

      {result.analysis && (
        <Card className="p-5">
          <h3 className="font-semibold">Frequentist analysis</h3>
          <div className="mt-4 grid gap-3 text-sm md:grid-cols-4">
            <div>
              Absolute lift
              <br />
              <b>{percent(result.analysis.absolute_lift)}</b>
            </div>
            <div>
              Relative lift
              <br />
              <b>
                {result.analysis.relative_lift == null
                  ? '—'
                  : percent(result.analysis.relative_lift)}
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
    </div>
  )
}
