import { useQuery } from '@tanstack/react-query'
import { RiskBadge } from '@/components/churn/RiskBadge'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { percent } from '@/lib/formatters'
import { mlApi } from '@/services/mlApi'

export default function ChurnPrediction() {
  const query = useQuery({
    queryKey: ['churn-scores'],
    queryFn: () => mlApi.scores({ limit: 100 }),
  })

  const rows = query.data ?? []

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-semibold">Churn risk queue</h2>
        <p className="text-sm opacity-60">
          Persisted batch scores using a future 30-day churn label. No model runs on page load.
        </p>
      </div>

      {!query.isLoading && rows.length === 0 ? (
        <EmptyState
          title="No churn scores yet"
          description="Run `make train` and then `make score` after seeding data."
        />
      ) : (
        <Card className="overflow-auto">
          <table className="w-full min-w-[800px] text-sm">
            <thead>
              <tr className="border-b text-left opacity-60">
                <th className="p-4">User</th>
                <th>Risk</th>
                <th>Probability</th>
                <th>Primary reasons</th>
                <th>Model</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.user_id} className="border-b last:border-0">
                  <td className="p-4 font-medium">{row.external_id}</td>
                  <td>
                    <RiskBadge risk={row.risk_band} />
                  </td>
                  <td>{percent(row.score)}</td>
                  <td className="max-w-md">{row.reasons.join(' · ')}</td>
                  <td className="text-xs opacity-60">{row.model_version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
