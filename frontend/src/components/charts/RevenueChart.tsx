import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Card } from '@/components/ui/Card'
import { money } from '@/lib/formatters'
import type { RevenuePoint } from '@/types/api'

export function RevenueChart({ data }: { data: RevenuePoint[] }) {
  return (
    <Card className="p-5">
      <div className="mb-4">
        <h3 className="font-semibold">Revenue trend</h3>
        <p className="text-sm opacity-60">Monthly purchase revenue for the selected acquisition scope</p>
      </div>
      <div className="h-72">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} minTickGap={35} />
            <YAxis
              tick={{ fontSize: 11 }}
              width={70}
              tickFormatter={(value: number) => money(value).replace('.00', '')}
            />
            <Tooltip formatter={(value) => money(Number(value))} />
            <Area
              type="monotone"
              dataKey="revenue"
              fill="hsl(var(--primary)/.15)"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
