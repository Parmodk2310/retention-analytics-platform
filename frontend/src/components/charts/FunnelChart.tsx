import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import type { FunnelResponse } from '@/types/analytics'

interface Props {
  data?: FunnelResponse
}

const COLORS = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))', '#ef4444']

export function FunnelChart({ data }: Props) {
  if (!data) return <div className="h-96 rounded-xl border bg-card animate-pulse" />
  
  const chartData = data.stages.map((stage, i) => ({
    name: stage.stage,
    users: stage.users,
    dropOff: stage.drop_off,
    rate: stage.conversion_rate,
    fill: COLORS[i % COLORS.length],
  }))
  
  return (
    <div className="rounded-xl border bg-card p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Conversion Funnel</h3>
        <p className="text-sm text-muted-foreground">Last {data.period_days} days · {chartData[0]?.users.toLocaleString()} total users</p>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis 
              type="category" 
              dataKey="name" 
              stroke="hsl(var(--muted-foreground))" 
              fontSize={12}
              width={80}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                fontSize: '13px',
              }}
              formatter={(value: number, _name: string, props: any) => [
                `${value.toLocaleString()} users (${(props.payload.rate * 100).toFixed(1)}% conv.)`,
                'Users'
              ]}
            />
            <Bar dataKey="users" radius={[0, 4, 4, 0]} barSize={32}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Drop-off badges */}
      <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-border">
        {data.stages.slice(1).map((stage, i) => (
          <div key={stage.stage} className="text-center">
            <p className="text-xs text-muted-foreground">{stage.stage} drop-off</p>
            <p className="text-sm font-semibold text-destructive">
              {stage.drop_off > 0 ? `-${((stage.drop_off / data.stages[i].users) * 100).toFixed(1)}%` : '—'}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}