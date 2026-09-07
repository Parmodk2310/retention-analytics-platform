import { FunnelChart } from '@/components/charts/FunnelChart'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useFunnel } from '@/hooks/useAnalytics'

export default function FunnelAnalysis() {
  const query = useFunnel()

  if (query.isLoading && !query.data) return <Skeleton className="h-[520px]" />
  if (query.error) return <ErrorState onRetry={() => query.refetch()} />

  const rows = query.data ?? []
  if (!rows.length) {
    return <EmptyState title="No funnel activity" description="Try a wider date range or another channel." />
  }

  const bottleneck = [...rows]
    .slice(1)
    .sort((left, right) => right.dropoff_from_previous - left.dropoff_from_previous)[0]

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
      <FunnelChart data={rows} />
    </div>
  )
}
