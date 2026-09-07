import { CHANNELS } from '@/lib/constants'
import { useUIStore } from '@/store/uiStore'

export function GlobalFilters() {
  const { days, channel, setDays, setChannel } = useUIStore()
  const controlClass = 'rounded-xl border bg-card px-3 py-2 text-sm'

  return (
    <div className="flex flex-wrap gap-2" aria-label="Global analytics filters">
      <select
        aria-label="Date range"
        className={controlClass}
        value={days}
        onChange={(event) => setDays(Number(event.target.value))}
      >
        <option value={7}>Last 7 days</option>
        <option value={30}>Last 30 days</option>
        <option value={90}>Last 90 days</option>
        <option value={365}>Last 12 months</option>
      </select>
      <select
        aria-label="Acquisition channel"
        className={controlClass}
        value={channel || ''}
        onChange={(event) => setChannel(event.target.value || null)}
      >
        <option value="">All channels</option>
        {CHANNELS.map((item) => (
          <option key={item} value={item}>
            {item.replaceAll('_', ' ')}
          </option>
        ))}
      </select>
      <span className="rounded-xl border bg-card px-3 py-2 text-xs opacity-60">UTC · API-backed</span>
    </div>
  )
}
