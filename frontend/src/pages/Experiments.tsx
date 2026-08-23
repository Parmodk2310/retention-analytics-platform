import { useQuery } from '@tanstack/react-query'
import { FlaskConical, CheckCircle2, XCircle, HelpCircle } from 'lucide-react'
import { experimentApi } from '@/services/experimentApi'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn, formatPercent } from '@/lib/utils'

export function Experiments() {
  const { data, isLoading } = useQuery({
    queryKey: ['experiment', 'exp_onboarding_v2'],
    queryFn: () => experimentApi.getResults('exp_onboarding_v2'),
    staleTime: 5 * 60 * 1000,
  })
  
  const analysis = data?.analysis
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <FlaskConical className="w-6 h-6 text-primary" />
          A/B Testing
        </h2>
        <p className="text-muted-foreground">Statistical experimentation framework</p>
      </div>
      
      {isLoading ? <Skeleton className="h-96" /> : data ? (
        <div className="space-y-6">
          {/* Experiment Card */}
          <div className="rounded-xl border bg-card p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
                    {data.status}
                  </span>
                  <span className="text-xs text-muted-foreground">{data.metric_type}</span>
                </div>
                <h3 className="text-lg font-semibold">{data.hypothesis}</h3>
                <p className="text-sm text-muted-foreground mt-1">Experiment ID: {data.experiment_id}</p>
              </div>
            </div>
            
            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Control */}
              <div className="rounded-lg border border-border p-4">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Control (A)</p>
                <p className="text-3xl font-bold">{formatPercent(analysis?.control_rate ?? 0)}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {data.sample_sizes.control.toLocaleString()} users
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  CI: [{analysis?.ci_control[0] ?? 0}, {analysis?.ci_control[1] ?? 0}]
                </p>
              </div>
              
              {/* Treatment */}
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
                <p className="text-xs font-medium text-primary uppercase tracking-wider mb-3">Treatment (B)</p>
                <p className="text-3xl font-bold text-primary">{formatPercent(analysis?.treatment_rate ?? 0)}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {data.sample_sizes.treatment.toLocaleString()} users
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  CI: [{analysis?.ci_treatment[0] ?? 0}, {analysis?.ci_treatment[1] ?? 0}]
                </p>
              </div>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-border">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Relative Lift</p>
                <p className={cn(
                  "text-lg font-bold",
                  (analysis?.relative_lift ?? 0) > 0 ? "text-emerald-500" : "text-destructive"
                )}>
                  {(analysis?.relative_lift ?? 0) > 0 ? '+' : ''}{(analysis?.relative_lift ?? 0).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">P-Value</p>
                <p className="text-lg font-bold font-mono">{analysis?.p_value ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Power</p>
                <p className="text-lg font-bold">{((analysis?.power ?? 0) * 100).toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Significant?</p>
                <div className="flex items-center gap-1.5">
                  {analysis?.significant ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      <span className="text-sm font-medium text-emerald-500">Yes</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-5 h-5 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">No</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            {/* Recommendation */}
            <div className={cn(
              "mt-6 p-4 rounded-lg flex items-start gap-3",
              analysis?.significant && (analysis?.relative_lift ?? 0) > 0
                ? "bg-emerald-500/10 border border-emerald-500/20"
                : "bg-yellow-500/10 border border-yellow-500/20"
            )}>
              {analysis?.significant && (analysis?.relative_lift ?? 0) > 0 ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500 mt-0.5" />
              ) : (
                <HelpCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
              )}
              <div>
                <p className="font-medium text-sm">Recommendation</p>
                <p className="text-sm text-muted-foreground mt-1">{analysis?.recommendation}</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border bg-card p-12 text-center">
          <FlaskConical className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No experiment data available</p>
        </div>
      )}
    </div>
  )
}