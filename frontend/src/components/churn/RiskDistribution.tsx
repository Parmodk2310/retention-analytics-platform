import type {
  ChurnSummary,
  RiskBand,
} from '@/types/api'

const bands: RiskBand[] = [
  'critical',
  'high',
  'medium',
  'low',
]

const barClasses:
  Record<RiskBand, string> = {
    critical: 'bg-danger',
    high: 'bg-warning',
    medium: 'bg-primary',
    low: 'bg-success',
  }

const numberFormatter =
  new Intl.NumberFormat('en-US')

export function RiskDistribution({
  summary,
}: {
  summary: ChurnSummary
}) {
  return (
    <div>
      <div className="mb-5">
        <h3 className="font-semibold">
          Risk distribution
        </h3>

        <p className="mt-1 text-xs opacity-50">
          Operational segments based on
          validation-derived thresholds.
        </p>
      </div>

      <div className="space-y-4">
        {bands.map((band) => {
          const count =
            summary.risk_bands[
              band
            ] ?? 0

          const percentage =
            summary.total_scored > 0
              ? (
                  count /
                  summary.total_scored
                ) * 100
              : 0

          return (
            <div key={band}>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="capitalize">
                  {band}
                </span>

                <span className="text-xs opacity-60">
                  {numberFormatter.format(
                    count,
                  )}
                  {' · '}
                  {percentage.toFixed(
                    1,
                  )}
                  %
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className={`h-full rounded-full ${barClasses[band]}`}
                  style={{
                    width:
                      `${Math.min(
                        percentage,
                        100,
                      )}%`,
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}