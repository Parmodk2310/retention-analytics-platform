import {
  RiskBadge,
} from '@/components/churn/RiskBadge'
import type {
  ChurnReason,
  ChurnScore,
} from '@/types/api'

const percentageFormatter =
  new Intl.NumberFormat(
    'en-US',
    {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    },
  )

function displayFeature(
  feature: string,
) {
  return feature
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    )
}

function displayValue(
  value: string,
) {
  return value
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    )
}

function ReasonChip({
  reason,
}: {
  reason: ChurnReason
}) {
  const increasing =
    reason.direction ===
    'increases_risk'

  return (
    <span
      title={
        'TreeSHAP contribution on the ' +
        'underlying XGBoost model margin'
      }
      className="inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-xs"
    >
      <span
        className={
          increasing
            ? 'text-danger'
            : 'text-success'
        }
      >
        {increasing
          ? '↑'
          : '↓'}
      </span>

      <span>
        {displayFeature(
          reason.feature,
        )}
      </span>

      <span className="opacity-40">
        {Math.abs(
          reason.impact,
        ).toFixed(3)}
      </span>
    </span>
  )
}

export function ChurnTable({
  rows,
}: {
  rows: ChurnScore[]
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1100px] text-sm">
        <thead>
          <tr className="border-b text-left text-xs uppercase tracking-wide opacity-50">
            <th className="px-4 py-3">
              User
            </th>

            <th className="px-3 py-3">
              Risk
            </th>

            <th className="px-3 py-3">
              Probability
            </th>

            <th className="px-3 py-3">
              Channel
            </th>

            <th className="px-3 py-3">
              Device
            </th>

            <th className="px-3 py-3">
              Local drivers
            </th>

            <th className="px-3 py-3">
              Snapshot
            </th>
          </tr>
        </thead>

        <tbody>
          {rows.map((row) => (
            <tr
              key={`${row.user_id}-${row.model_version}`}
              className="border-b last:border-0 hover:bg-muted/30"
            >
              <td className="px-4 py-4">
                <p className="font-medium">
                  {row.external_id}
                </p>

                <p className="mt-0.5 max-w-[170px] truncate font-mono text-[10px] opacity-40">
                  {row.user_id}
                </p>
              </td>

              <td className="px-3 py-4">
                <RiskBadge
                  risk={
                    row.risk_band
                  }
                />
              </td>

              <td className="px-3 py-4 font-medium tabular-nums">
                {percentageFormatter.format(
                  row.score,
                )}
              </td>

              <td className="px-3 py-4">
                {displayValue(
                  row.acquisition_channel,
                )}
              </td>

              <td className="px-3 py-4">
                {displayValue(
                  row.device_type,
                )}
              </td>

              <td className="max-w-[420px] px-3 py-4">
                <div className="flex flex-wrap gap-1.5">
                  {row.reasons.map(
                    (
                      reason,
                      index,
                    ) => (
                      <ReasonChip
                        key={
                          `${reason.feature}-${index}`
                        }
                        reason={
                          reason
                        }
                      />
                    ),
                  )}
                </div>
              </td>

              <td className="px-3 py-4 text-xs opacity-60">
                {row.snapshot_date}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}