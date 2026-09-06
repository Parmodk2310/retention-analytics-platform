import { Activity, DollarSign, ShoppingBag, Users } from 'lucide-react'
import { ActivityChart } from '@/components/charts/ActivityChart'
import { MetricCard } from '@/components/charts/MetricCard'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useActivity, useOverview } from '@/hooks/useAnalytics'
import { compact, money, percent } from '@/lib/formatters'

export default function Dashboard() {
  const overview = useOverview()
  const activity = useActivity()

  if (overview.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((item) => (
          <Skeleton key={item} className="h-32" />
        ))}
      </div>
    )
  }

  if (overview.error) {
    return <ErrorState onRetry={() => overview.refetch()} />
  }

  const metrics = overview.data

  if (!metrics) {
    return <ErrorState onRetry={() => overview.refetch()} />
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm opacity-60">Live product health from PostgreSQL analytics</p>
        <h2 className="mt-1 text-2xl font-semibold">Retention and engagement overview</h2>
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

      {activity.data && <ActivityChart data={activity.data} />}
    </div>
  )
}
