import { useCohortRetention } from '@/hooks/useAnalytics'
import { RetentionHeatmap } from '@/components/charts/RetentionHeatmap'
import { Skeleton } from '@/components/ui/Skeleton'

export function CohortAnalysis() {
  const { data, isLoading } = useCohortRetention(12)
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Cohort Analysis</h2>
        <p className="text-muted-foreground">Track user retention across monthly signup cohorts</p>
      </div>
      
      {isLoading ? <Skeleton className="h-[500px]" /> : (
        <div className="space-y-6">
          <RetentionHeatmap data={data} />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">Best Channel</p>
              <p className="text-xl font-bold text-emerald-500">Referral</p>
              <p className="text-xs text-muted-foreground mt-1">18.5% Month-6 retention</p>
            </div>
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">Worst Channel</p>
              <p className="text-xl font-bold text-destructive">Affiliate</p>
              <p className="text-xs text-muted-foreground mt-1">4.2% Month-6 retention</p>
            </div>
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">Avg. Month-1</p>
              <p className="text-xl font-bold">42.3%</p>
              <p className="text-xs text-muted-foreground mt-1">Across all channels</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}