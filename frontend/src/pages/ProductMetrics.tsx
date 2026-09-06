import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/Card'
import { money, percent } from '@/lib/formatters'
import { analyticsApi } from '@/services/analyticsApi'
import { useUIStore } from '@/store/uiStore'

export default function ProductMetrics() {
  const days = useUIStore((state) => state.days)
  const query = useQuery({
    queryKey: ['channels', days],
    queryFn: () => analyticsApi.channels(days),
  })

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Channel performance</h2>

      <Card className="overflow-auto">
        <table className="w-full text-sm">
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
            {query.data?.map((row) => (
              <tr key={row.acquisition_channel} className="border-b last:border-0">
                <td className="p-4 font-medium">{row.acquisition_channel}</td>
                <td>{row.users.toLocaleString()}</td>
                <td>{row.purchasers.toLocaleString()}</td>
                <td>{percent(row.users ? row.purchasers / row.users : 0)}</td>
                <td>{money(row.revenue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  )
}
