import { CalendarDays, Database } from 'lucide-react'
import { dateLabel } from '@/lib/formatters'

export function DataScope({
  asOf,
  days,
  channel,
}: {
  asOf?: string
  days: number
  channel: string | null
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs opacity-55">
      <span className="inline-flex items-center gap-1.5">
        <Database className="h-3.5 w-3.5" />
        PostgreSQL-backed
      </span>
      <span>·</span>
      <span>{channel ? channel.replaceAll('_', ' ') : 'all channels'}</span>
      <span>·</span>
      <span>{days}-day window</span>
      {asOf && (
        <>
          <span>·</span>
          <span className="inline-flex items-center gap-1.5">
            <CalendarDays className="h-3.5 w-3.5" />
            As of {dateLabel(asOf)}
          </span>
        </>
      )}
    </div>
  )
}
