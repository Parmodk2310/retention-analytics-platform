import type { RiskBand } from '@/types/api'
import { cn } from '@/lib/utils'

type Props = {
  risk: RiskBand
}

export function RiskBadge({
  risk,
}: Props) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full px-2.5 py-1 text-xs font-semibold capitalize',
        risk === 'critical' &&
          'bg-danger/15 text-danger',
        risk === 'high' &&
          'bg-warning/15 text-warning',
        risk === 'medium' &&
          'bg-primary/15 text-primary',
        risk === 'low' &&
          'bg-success/15 text-success',
      )}
    >
      {risk}
    </span>
  )
}