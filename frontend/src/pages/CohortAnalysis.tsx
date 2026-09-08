import { RetentionHeatmap } from '@/components/charts/RetentionHeatmap'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useRetention } from '@/hooks/useAnalytics'
import { useUIStore } from '@/store/uiStore'

export default function CohortAnalysis() {
  const query = useRetention()
  const channel = useUIStore((state) => state.channel)

  if (query.isLoading && !query.data) return <Skeleton className="h-[540px]" />
  if (query.error) return <ErrorState onRetry={() => query.refetch()} />

  const rows = query.data ?? []
  if (!rows.length) {
    return <EmptyState title="No cohort data" description="Try another acquisition channel." />
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-semibold">Cohort retention</h2>
        <p className="text-sm opacity-60">
          Monthly retention for {channel ? channel.replaceAll('_', ' ') : 'all acquisition channels'}.
          M0 is the original cohort population.
        </p>
      </div>
      <RetentionHeatmap data={rows} />
    </div>
  )
}
