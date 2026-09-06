import { FunnelChart } from '@/components/charts/FunnelChart'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useFunnel } from '@/hooks/useAnalytics'

export default function FunnelAnalysis() {
  const query = useFunnel()

  if (query.isLoading) {
    return <Skeleton className="h-[520px]" />
  }

  if (query.error) {
    return <ErrorState onRetry={() => query.refetch()} />
  }

  const bottleneck = [...(query.data ?? [])]
    .slice(1)
    .sort((a, b) => b.dropoff_from_previous - a.dropoff_from_previous)[0]

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-semibold">Sequential funnel</h2>
        <p className="text-sm opacity-60">Stages are counted only when they happen in order.</p>
      </div>

      {bottleneck && (
        <div className="rounded-xl border bg-warning/10 p-4 text-sm">
          <b>Largest current drop-off:</b> {bottleneck.stage} ·{' '}
          {(bottleneck.dropoff_from_previous * 100).toFixed(1)}%
        </div>
      )}

      <FunnelChart data={query.data ?? []} />
    </div>
  )
}
