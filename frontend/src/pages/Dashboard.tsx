import { useMetrics, useFunnel, useCohortRetention } from '@/hooks/useAnalytics'
import { MetricCard } from '@/components/charts/MetricCard'
import { RetentionHeatmap } from '@/components/charts/RetentionHeatmap'
import { FunnelChart } from '@/components/charts/FunnelChart'
import { Skeleton } from '@/components/ui/Skeleton'

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
    </div>
  )
}

export function Dashboard() {
  const { data: metrics, isLoading: mLoading } = useMetrics()
  const { data: funnel } = useFunnel(30)
  const { data: cohorts } = useCohortRetention(12)
  
  if (mLoading) return <DashboardSkeleton />
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">Overview of product health and key metrics</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="DAU" value={metrics?.dau ?? 0} trend={2.4} format="compact" icon="Users" />
        <MetricCard title="Stickiness" value={metrics?.stickiness ?? 0} trend={-0.8} format="percent" icon="Activity" />
        <MetricCard title="Revenue/User" value={metrics?.dau ? 28.5 : 0} trend={5.2} format="currency" icon="DollarSign" />
        <MetricCard title="Churn Risk" value={1240} trend={12.3} format="number" variant="destructive" icon="AlertTriangle" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RetentionHeatmap data={cohorts} />
        <FunnelChart data={funnel} />
      </div>
    </div>
  )
}