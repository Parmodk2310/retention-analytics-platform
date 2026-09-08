import { useUIStore } from '@/store/uiStore'

type TimeMode = 'days' | 'months'

type Props = {
  timeMode?: TimeMode
}

const DAY_OPTIONS = [
  { label: 'Last 7 days', value: 7 },
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'Last 12 months', value: 365 },
] as const

const MONTH_OPTIONS = [
  { label: 'Last 3 months', value: 3 },
  { label: 'Last 6 months', value: 6 },
  { label: 'Last 9 months', value: 9 },
  { label: 'Last 12 months', value: 12 },
] as const

const CHANNEL_OPTIONS = [
  { label: 'All channels', value: '' },
  { label: 'Organic', value: 'organic' },
  { label: 'Email', value: 'email' },
  { label: 'Paid Social', value: 'paid_social' },
  { label: 'Referral', value: 'referral' },
  { label: 'Affiliate', value: 'affiliate' },
] as const

export function GlobalFilters({ timeMode = 'days' }: Props) {
  const days = useUIStore((state) => state.days)
  const cohortMonths = useUIStore((state) => state.cohortMonths)
  const channel = useUIStore((state) => state.channel)

  const setDays = useUIStore((state) => state.setDays)
  const setCohortMonths = useUIStore((state) => state.setCohortMonths)
  const setChannel = useUIStore((state) => state.setChannel)

  const timeValue = timeMode === 'months' ? cohortMonths : days
  const timeOptions = timeMode === 'months' ? MONTH_OPTIONS : DAY_OPTIONS

  function changeTime(value: string) {
    const numericValue = Number(value)

    if (timeMode === 'months') {
      setCohortMonths(numericValue)
      return
    }

    setDays(numericValue)
  }

  function changeChannel(value: string) {
    setChannel(value || null)
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <select
        value={timeValue}
        onChange={(event) => changeTime(event.target.value)}
        className="rounded-xl border bg-card px-3 py-2 text-sm"
        aria-label={
          timeMode === 'months'
            ? 'Cohort lookback period'
            : 'Analytics lookback period'
        }
      >
        {timeOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <select
        value={channel ?? ''}
        onChange={(event) => changeChannel(event.target.value)}
        className="rounded-xl border bg-card px-3 py-2 text-sm"
        aria-label="Acquisition channel"
      >
        {CHANNEL_OPTIONS.map((option) => (
          <option key={option.label} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <span className="rounded-xl border bg-card px-3 py-2 text-xs opacity-60">
        UTC · API-backed
      </span>
    </div>
  )
}
