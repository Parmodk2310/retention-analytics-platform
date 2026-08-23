import { useMemo } from 'react'
import { formatPercent } from '@/lib/utils'
import type { CohortResponse } from '@/types/analytics'

interface Props {
  data?: CohortResponse
}

export function RetentionHeatmap({ data }: Props) {
  const { cohorts, maxPeriod, matrix } = useMemo(() => {
    if (!data?.cohorts) return { cohorts: [], maxPeriod: 0, matrix: [] as number[][] }
    
    const cohortList = Object.entries(data.cohorts)
      .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
      .slice(0, 12)
    
    const maxP = Math.max(...cohortList.flatMap(([, v]) => Object.keys(v.retention).map(Number)))
    
    const mat = cohortList.map(([, values]) => {
      const row: number[] = []
      for (let i = 0; i <= maxP; i++) {
        row.push(values.retention[i] ?? 0)
      }
      return row
    })
    
    return { cohorts: cohortList, maxPeriod: maxP, matrix: mat }
  }, [data])
  
  const getColor = (value: number) => {
    if (value >= 0.4) return 'bg-emerald-500/80'
    if (value >= 0.25) return 'bg-emerald-400/60'
    if (value >= 0.15) return 'bg-yellow-400/50'
    if (value >= 0.08) return 'bg-orange-400/50'
    if (value > 0) return 'bg-red-400/40'
    return 'bg-muted'
  }
  
  if (!data) return <div className="h-96 rounded-xl border bg-card animate-pulse" />
  
  return (
    <div className="rounded-xl border bg-card p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Cohort Retention</h3>
        <p className="text-sm text-muted-foreground">Monthly retention by signup cohort</p>
      </div>
      
      <div className="overflow-x-auto">
        <div className="min-w-[600px]">
          {/* Header */}
          <div className="flex mb-1">
            <div className="w-24 text-xs text-muted-foreground font-medium py-1">Cohort</div>
            {Array.from({ length: maxPeriod + 1 }, (_, i) => (
              <div key={i} className="w-12 text-center text-xs text-muted-foreground py-1">
                M{i}
              </div>
            ))}
          </div>
          
          {/* Rows */}
          {cohorts.map(([month, values], rowIdx) => (
            <div key={month} className="flex items-center mb-1">
              <div className="w-24 text-xs font-medium text-muted-foreground py-1">
                {new Date(month).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                <span className="ml-1 text-[10px] opacity-60">({values.size})</span>
              </div>
              {matrix[rowIdx]?.map((val, colIdx) => (
                <div
                  key={colIdx}
                  className={`w-12 h-8 mx-0.5 rounded flex items-center justify-center text-[10px] font-medium cursor-pointer heatmap-cell ${getColor(val)}`}
                  title={`Month ${colIdx}: ${formatPercent(val)} retained`}
                >
                  {val > 0 ? `${(val * 100).toFixed(0)}` : ''}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border">
        <span className="text-xs text-muted-foreground">Low</span>
        {['bg-red-400/40', 'bg-orange-400/50', 'bg-yellow-400/50', 'bg-emerald-400/60', 'bg-emerald-500/80'].map((c, i) => (
          <div key={i} className={`w-6 h-4 rounded ${c}`} />
        ))}
        <span className="text-xs text-muted-foreground">High</span>
      </div>
    </div>
  )
}