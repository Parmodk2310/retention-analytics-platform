import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn, formatNumber, formatPercent } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: number
  trend?: number
  format: 'compact' | 'percent' | 'currency' | 'number'
  icon: string
  variant?: 'default' | 'destructive'
}

const iconMap: Record<string, React.ElementType> = {
  Users: () => <span className="text-lg">👥</span>,
  Activity: () => <span className="text-lg">📈</span>,
  DollarSign: () => <span className="text-lg">💰</span>,
  AlertTriangle: () => <span className="text-lg">⚠️</span>,
}

export function MetricCard({ title, value, trend, format, icon, variant = 'default' }: MetricCardProps) {
  const Icon = iconMap[icon] || (() => <span>📊</span>)
  
  const displayValue = format === 'percent' 
    ? formatPercent(value) 
    : format === 'currency' 
    ? `$${formatNumber(value)}`
    : formatNumber(value, true)
  
  const trendPositive = trend && trend > 0
  const trendNegative = trend && trend < 0
  
  return (
    <div className={cn(
      "rounded-xl border bg-card p-6 transition-all hover:shadow-lg hover:border-primary/20",
      variant === 'destructive' && "border-destructive/20 bg-destructive/5"
    )}>
      <div className="flex items-center justify-between mb-4">
        <div className={cn(
          "w-10 h-10 rounded-lg flex items-center justify-center bg-primary/10",
          variant === 'destructive' && "bg-destructive/10"
        )}>
          <Icon />
        </div>
        {trend !== undefined && (
          <div className={cn(
            "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
            trendPositive && "bg-emerald-500/10 text-emerald-500",
            trendNegative && "bg-red-500/10 text-red-500",
            !trendPositive && !trendNegative && "bg-muted text-muted-foreground"
          )}>
            {trendPositive ? <TrendingUp className="w-3 h-3" /> : trendNegative ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
            {Math.abs(trend).toFixed(1)}%
          </div>
        )}
      </div>
      
      <p className="text-sm text-muted-foreground mb-1">{title}</p>
      <p className={cn(
        "text-2xl font-bold tracking-tight",
        variant === 'destructive' && "text-destructive"
      )}>
        {displayValue}
      </p>
    </div>
  )
}