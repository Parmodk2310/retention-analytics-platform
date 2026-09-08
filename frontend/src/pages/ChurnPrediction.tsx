import { useState } from 'react'
import { BrainCircuit, ChevronLeft, ChevronRight, Database } from 'lucide-react'

import { ChurnTable } from '@/components/churn/ChurnTable'
import { DriverList } from '@/components/churn/DriverList'
import { MetricCard } from '@/components/churn/MetricCard'
import { RiskDistribution } from '@/components/churn/RiskDistribution'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import {
  useChurnModelHealth,
  useChurnScores,
  useChurnSummary,
} from '@/hooks/useChurn'
import type { RiskBand } from '@/types/api'

const PAGE_SIZE = 25

const numberFormatter = new Intl.NumberFormat('en-US')

const percentageFormatter = new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const riskBandOptions: Array<{ label: string; value: RiskBand | '' }> = [
  { label: 'All risk bands', value: '' },
  { label: 'Critical', value: 'critical' },
  { label: 'High', value: 'high' },
  { label: 'Medium', value: 'medium' },
  { label: 'Low', value: 'low' },
]

const acquisitionChannelOptions = [
  { label: 'All channels', value: '' },
  { label: 'Organic', value: 'organic' },
  { label: 'Email', value: 'email' },
  { label: 'Paid Social', value: 'paid_social' },
  { label: 'Referral', value: 'referral' },
  { label: 'Affiliate', value: 'affiliate' },
] as const

const deviceTypeOptions = [
  { label: 'All devices', value: '' },
  { label: 'Web', value: 'web' },
  { label: 'iOS', value: 'ios' },
  { label: 'Android', value: 'android' },
] as const

export default function ChurnPrediction() {
  const [riskBand, setRiskBand] = useState<RiskBand | null>(null)
  const [acquisitionChannel, setAcquisitionChannel] = useState('')
  const [deviceType, setDeviceType] = useState('')
  const [offset, setOffset] = useState(0)

  const summaryQuery = useChurnSummary()
  const modelQuery = useChurnModelHealth()

  const scoresQuery = useChurnScores({
    limit: PAGE_SIZE,
    offset,
    riskBand,
    acquisitionChannel,
    deviceType,
  })

  const summary = summaryQuery.data
  const model = modelQuery.data
  const rows = scoresQuery.data ?? []

  const isLoading =
    summaryQuery.isLoading ||
    modelQuery.isLoading ||
    scoresQuery.isLoading

  const hasError =
    summaryQuery.isError ||
    modelQuery.isError ||
    scoresQuery.isError

  function changeRiskBand(value: string) {
    setRiskBand(value ? (value as RiskBand) : null)
    setOffset(0)
  }

  function changeChannel(value: string) {
    setAcquisitionChannel(value)
    setOffset(0)
  }

  function changeDevice(value: string) {
    setDeviceType(value)
    setOffset(0)
  }

  function clearFilters() {
    setRiskBand(null)
    setAcquisitionChannel('')
    setDeviceType('')
    setOffset(0)
  }

  if (isLoading && !summary && !model && rows.length === 0) {
    return <p className="opacity-60">Loading churn intelligence…</p>
  }

  if (hasError) {
    return (
      <ErrorState
        onRetry={() => {
          void summaryQuery.refetch()
          void modelQuery.refetch()
          void scoresQuery.refetch()
        }}
      />
    )
  }

  if (summary && summary.total_scored === 0) {
    return (
      <EmptyState
        title="No production churn scores"
        description="Run the Phase 4 batch scorer after an accepted model artifact is available."
      />
    )
  }

  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-primary">
          <BrainCircuit className="h-4 w-4" />
          <p className="text-sm font-semibold uppercase tracking-[0.14em]">
            ML Intelligence
          </p>
        </div>

        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-end">
          <div>
            <h2 className="text-2xl font-semibold">Churn Intelligence</h2>
            <p className="mt-1 max-w-3xl text-sm opacity-60">
              Calibrated 30-day inactivity-risk scoring backed by persisted batch
              predictions and local TreeSHAP explanations.
            </p>
          </div>

          {summary?.snapshot_date && (
            <div className="flex items-center gap-2 text-xs opacity-60">
              <Database className="h-4 w-4" />
              <span>Latest snapshot</span>
              <span className="font-medium text-foreground">
                {summary.snapshot_date}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Users scored"
          value={summary ? numberFormatter.format(summary.total_scored) : '—'}
          hint="Latest eligible production snapshot"
        />

        <MetricCard
          label="High + critical"
          value={summary ? numberFormatter.format(summary.high_risk_count) : '—'}
          hint={
            summary?.total_scored
              ? `${((summary.high_risk_count / summary.total_scored) * 100).toFixed(
                  1,
                )}% of scored users`
              : undefined
          }
        />

        <MetricCard
          label="Mean 30-day risk"
          value={
            summary
              ? percentageFormatter.format(summary.average_score)
              : '—'
          }
          hint="Mean calibrated inactivity-risk score"
        />

        <MetricCard
          label="Model"
          value={model ? model.algorithm.replaceAll('_', ' ').toUpperCase() : '—'}
          hint={model?.model_version}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card className="p-5">
          {summary ? (
            <RiskDistribution summary={summary} />
          ) : (
            <p className="text-sm opacity-50">Loading risk distribution…</p>
          )}
        </Card>

        <Card className="p-5">
          <DriverList drivers={model?.global_feature_importance ?? []} />
        </Card>
      </div>

      <Card className="p-4">
        <div className="grid gap-3 md:grid-cols-3">
          <label className="space-y-1.5">
            <span className="text-xs font-medium opacity-60">Risk band</span>

            <select
              value={riskBand ?? ''}
              onChange={(event) => changeRiskBand(event.target.value)}
              className="w-full rounded-xl border bg-background px-3 py-2 text-sm"
            >
              {riskBandOptions.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1.5">
            <span className="text-xs font-medium opacity-60">
              Acquisition channel
            </span>

            <select
              value={acquisitionChannel}
              onChange={(event) => changeChannel(event.target.value)}
              className="w-full rounded-xl border bg-background px-3 py-2 text-sm"
            >
              {acquisitionChannelOptions.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1.5">
            <span className="text-xs font-medium opacity-60">Device type</span>

            <select
              value={deviceType}
              onChange={(event) => changeDevice(event.target.value)}
              className="w-full rounded-xl border bg-background px-3 py-2 text-sm"
            >
              {deviceTypeOptions.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {(riskBand || acquisitionChannel || deviceType) && (
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={clearFilters}
              className="rounded-lg border px-3 py-2 text-xs font-medium transition hover:bg-muted"
            >
              Clear filters
            </button>
          </div>
        )}
      </Card>

      <Card className="overflow-hidden">
        <div className="flex flex-col justify-between gap-3 border-b p-4 sm:flex-row sm:items-center">
          <div>
            <h3 className="font-semibold">Scored users</h3>
            <p className="mt-1 text-xs opacity-50">
              Ranked by calibrated churn probability.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs opacity-50">
            {scoresQuery.isFetching && !scoresQuery.isLoading && (
              <span>Updating…</span>
            )}

            <span>
              {rows.length > 0
                ? `Rows ${offset + 1}–${offset + rows.length}`
                : 'No matching rows'}
            </span>
          </div>
        </div>

        {scoresQuery.isLoading && rows.length === 0 ? (
          <div className="p-8 text-center text-sm opacity-50">
            Loading churn scores…
          </div>
        ) : rows.length === 0 ? (
          <div className="p-8 text-center">
            <p className="font-medium">No matching users</p>
            <p className="mt-1 text-sm opacity-50">
              Change or clear the current filters.
            </p>
          </div>
        ) : (
          <ChurnTable rows={rows} />
        )}

        <div className="flex items-center justify-between border-t p-4">
          <button
            type="button"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            className="inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </button>

          <span className="text-xs opacity-50">
            Page {Math.floor(offset / PAGE_SIZE) + 1}
          </span>

          <button
            type="button"
            disabled={rows.length < PAGE_SIZE}
            onClick={() => setOffset(offset + PAGE_SIZE)}
            className="inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </Card>

      <p className="text-xs leading-relaxed opacity-40">
        Risk bands are operational segments learned from the validation
        distribution. SHAP impacts explain the underlying XGBoost margin and
        should not be interpreted as additive changes to the displayed
        calibrated probability.
      </p>
    </div>
  )
}