import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BrainCircuit, AlertTriangle, Shield, UserX } from 'lucide-react'
import { mlApi } from '@/services/mlApi'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn, formatCurrency } from '@/lib/utils'

export function ChurnPrediction() {
  const [topN, setTopN] = useState(50)
  
  const { data, isLoading } = useQuery({
    queryKey: ['churn-predictions', topN],
    queryFn: () => mlApi.predictChurn(topN),
    staleTime: 5 * 60 * 1000,
  })
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-primary" />
            Churn Prediction
          </h2>
          <p className="text-muted-foreground">XGBoost model · 83% AUC-ROC · Updated daily</p>
        </div>
        <select 
          value={topN} 
          onChange={(e) => setTopN(Number(e.target.value))}
          className="bg-muted border border-border rounded-lg px-3 py-2 text-sm"
        >
          <option value={50}>Top 50</option>
          <option value={100}>Top 100</option>
          <option value={500}>Top 500</option>
        </select>
      </div>
      
      {isLoading ? <Skeleton className="h-96" /> : (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">Total Scored</p>
              <p className="text-2xl font-bold">{data?.total_scored.toLocaleString()}</p>
            </div>
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">High Risk</p>
              <p className="text-2xl font-bold text-destructive">{data?.high_risk_count.toLocaleString()}</p>
            </div>
            <div className="rounded-xl border bg-card p-6">
              <p className="text-sm text-muted-foreground mb-1">At-Risk Revenue</p>
              <p className="text-2xl font-bold">
                {formatCurrency(data?.predictions.reduce((sum, p) => sum + (p.risk_level === 'high' ? p.total_revenue : 0), 0) ?? 0)}
              </p>
            </div>
          </div>
          
          {/* Predictions Table */}
          <div className="rounded-xl border bg-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">User ID</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Risk Level</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Probability</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Days Inactive</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Revenue</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Sessions (30d)</th>
                </tr>
              </thead>
              <tbody>
                {data?.predictions.map((pred) => (
                  <tr key={pred.user_id} className="border-b border-border hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs">#{pred.user_id}</td>
                    <td className="px-4 py-3">
                      <span className={cn(
                        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium",
                        pred.risk_level === 'high' && "bg-destructive/10 text-destructive",
                        pred.risk_level === 'medium' && "bg-yellow-500/10 text-yellow-500",
                        pred.risk_level === 'low' && "bg-emerald-500/10 text-emerald-500"
                      )}>
                        {pred.risk_level === 'high' && <AlertTriangle className="w-3 h-3" />}
                        {pred.risk_level === 'medium' && <UserX className="w-3 h-3" />}
                        {pred.risk_level === 'low' && <Shield className="w-3 h-3" />}
                        {pred.risk_level}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 rounded-full bg-muted overflow-hidden">
                          <div 
                            className={cn(
                              "h-full rounded-full",
                              pred.churn_probability > 0.7 ? "bg-destructive" :
                              pred.churn_probability > 0.4 ? "bg-yellow-500" : "bg-emerald-500"
                            )}
                            style={{ width: `${pred.churn_probability * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium">{(pred.churn_probability * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{pred.days_since_last_login}d</td>
                    <td className="px-4 py-3 font-medium">{formatCurrency(pred.total_revenue)}</td>
                    <td className="px-4 py-3 text-muted-foreground">{pred.key_features.sessions_30d}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}