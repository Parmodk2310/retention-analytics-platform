import { Activity, DollarSign, ShoppingBag, Users } from 'lucide-react'
import { ActivityChart } from '@/components/charts/ActivityChart'
import { MetricCard } from '@/components/charts/MetricCard'
import { DataScope } from '@/components/ui/DataScope'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useActivity, useOverview } from '@/hooks/useAnalytics'
import { compact, money, percent } from '@/lib/formatters'
import { useUIStore } from '@/store/uiStore'

export default function Dashboard() {
  const overview = useOverview()
  const activity = useActivity()
  const days = useUIStore((state) => state.days)
  const channel = useUIStore((state) => state.channel)

  if (overview.isLoading && !overview.data) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <Skeleton key={item} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-[360px]" />
      </div>
    )
  }

  if (overview.error) {
    return <ErrorState onRetry={() => overview.refetch()} />
  }

  const metrics = overview.data

  if (!metrics) {
    return <EmptyState title="No overview data" description="Seed events or change the selected filters." />
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div>
          <p className="text-sm opacity-60">Live product health from PostgreSQL analytics</p>
          <h2 className="mt-1 text-2xl font-semibold">Retention and engagement overview</h2>
        </div>
        <DataScope asOf={metrics.as_of_date} days={days} channel={channel} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Daily active users"
          value={compact(metrics.dau)}
          subtitle={`WAU ${compact(metrics.wau)} · MAU ${compact(metrics.mau)}`}
          icon={Users}
        />
        <MetricCard
          title="Stickiness"
          value={percent(metrics.stickiness)}
          subtitle="DAU / MAU"
          icon={Activity}
        />
        <MetricCard
          title="Revenue"
          value={money(metrics.revenue)}
          subtitle={`${compact(metrics.purchasers)} purchasers`}
          icon={DollarSign}
        />
        <MetricCard
          title="New users"
          value={compact(metrics.new_users)}
          subtitle={`ARPPU ${money(metrics.arpu)}`}
          icon={ShoppingBag}
        />
      </div>

      {activity.isLoading && !activity.data ? (
        <Skeleton className="h-[360px]" />
      ) : activity.error ? (
        <ErrorState message="Could not load activity trend" onRetry={() => activity.refetch()} />
      ) : activity.data?.length ? (
        <ActivityChart data={activity.data} />
      ) : (
        <EmptyState title="No activity in this scope" description="Try a wider date range or another channel." />
      )}
    </div>
  )
}
