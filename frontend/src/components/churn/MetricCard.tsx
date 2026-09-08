import {
  Card,
} from '@/components/ui/Card'

type Props = {
  label: string
  value: string | number
  hint?: string
}

export function MetricCard({
  label,
  value,
  hint,
}: Props) {
  return (
    <Card className="p-5">
      <p className="text-sm opacity-60">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold tracking-tight">
        {value}
      </p>

      {hint && (
        <p className="mt-1 text-xs opacity-50">
          {hint}
        </p>
      )}
    </Card>
  )
}