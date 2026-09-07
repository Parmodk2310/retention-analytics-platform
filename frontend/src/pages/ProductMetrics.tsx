import { DollarSign, ShoppingCart, Users } from 'lucide-react'
import { MetricCard } from '@/components/charts/MetricCard'
import { RevenueChart } from '@/components/charts/RevenueChart'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useChannels, useRevenue } from '@/hooks/useAnalytics'
import { compact, money, percent } from '@/lib/formatters'
import { useUIStore } from '@/store/uiStore'

export default function ProductMetrics() {
  const channel = useUIStore((state) => state.channel)
  const channels = useChannels()
  const revenue = useRevenue()

  if ((channels.isLoading && !channels.data) || (revenue.isLoading && !revenue.data)) {
    return (
      <div className="space-y-5">
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-[360px]" />
      </div>
    )
  }

  if (channels.error || revenue.error) {
    return (
      <ErrorState
        message="Could not load product metrics"
        onRetry={() => Promise.all([channels.refetch(), revenue.refetch()])}
      />
    )
  }

  const visibleChannels = (channels.data ?? []).filter(
    (row) => !channel || row.acquisition_channel === channel,
  )
  const totalUsers = visibleChannels.reduce((sum, row) => sum + row.users, 0)
  const totalPurchasers = visibleChannels.reduce((sum, row) => sum + row.purchasers, 0)
  const totalRevenue = visibleChannels.reduce((sum, row) => sum + row.revenue, 0)

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm opacity-60">Acquisition quality, conversion and monetization</p>
        <h2 className="text-2xl font-semibold">Product metrics</h2>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard title="Active users" value={compact(totalUsers)} icon={Users} />
        <MetricCard
          title="Purchasers"
          value={compact(totalPurchasers)}
          subtitle={percent(totalUsers ? totalPurchasers / totalUsers : 0)}
          icon={ShoppingCart}
        />
        <MetricCard title="Revenue" value={money(totalRevenue)} icon={DollarSign} />
      </div>

      {revenue.data?.length ? (
        <RevenueChart data={revenue.data} />
      ) : (
        <EmptyState title="No revenue data" description="No purchases match the selected scope." />
      )}

      {visibleChannels.length ? (
        <Card className="overflow-auto">
          <table className="w-full min-w-[680px] text-sm">
            <thead>
              <tr className="border-b text-left opacity-60">
                <th className="p-4">Channel</th>
                <th>Users</th>
                <th>Purchasers</th>
                <th>Purchase rate</th>
                <th>Revenue</th>
              </tr>
            </thead>
            <tbody>
              {visibleChannels.map((row) => (
                <tr key={row.acquisition_channel} className="border-b last:border-0">
                  <td className="p-4 font-medium">{row.acquisition_channel.replaceAll('_', ' ')}</td>
                  <td>{row.users.toLocaleString()}</td>
                  <td>{row.purchasers.toLocaleString()}</td>
                  <td>{percent(row.users ? row.purchasers / row.users : 0)}</td>
                  <td>{money(row.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ) : (
        <EmptyState title="No channel metrics" description="Try another acquisition channel or date range." />
      )}
    </div>
  )
}
