import { useFunnel } from '@/hooks/useAnalytics'
import { FunnelChart } from '@/components/charts/FunnelChart'
import { Skeleton } from '@/components/ui/Skeleton'

export function FunnelAnalysis() {
  const { data, isLoading } = useFunnel(30)
  
  const worstDropoff = data?.stages.reduce((max, stage, i) => {
    if (i === 0) return max
    const rate = stage.drop_off / data.stages[i - 1].users
    return rate > max.rate ? { stage: stage.stage, rate } : max
  }, { stage: '', rate: 0 })
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Funnel Analysis</h2>
        <p className="text-muted-foreground">6-stage conversion funnel with drop-off diagnostics</p>
      </div>
      
      {isLoading ? <Skeleton className="h-96" /> : (
        <div className="space-y-6">
          <FunnelChart data={data} />
          
          <div className="rounded-xl border bg-destructive/5 border-destructive/20 p-6">
            <h4 className="font-semibold text-destructive mb-2">🚨 Critical Insight</h4>
            <p className="text-sm text-muted-foreground">
              Highest drop-off at <strong>{worstDropoff?.stage}</strong> stage with 
              {' '}<strong>{((worstDropoff?.rate ?? 0) * 100).toFixed(1)}%</strong> of users leaving. 
              Recommend: Simplify UI, add progress indicators, and implement exit-intent surveys.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}