import {
  useQuery,
} from '@tanstack/react-query'

import {
  churnKeys,
} from '@/lib/queryKeys'
import {
  mlApi,
} from '@/services/mlApi'
import type {
  RiskBand,
} from '@/types/api'

const STALE_TIME = 60_000

export type ChurnFilters = {
  limit: number
  offset: number
  riskBand: RiskBand | null
  acquisitionChannel: string
  deviceType: string
}

export function useChurnSummary() {
  return useQuery({
    queryKey:
      churnKeys.summary(),

    queryFn:
      mlApi.summary,

    staleTime:
      STALE_TIME,
  })
}

export function useChurnModelHealth() {
  return useQuery({
    queryKey:
      churnKeys.modelHealth(),

    queryFn:
      mlApi.modelHealth,

    staleTime:
      STALE_TIME,
  })
}

function normalizeDimension(
  value: string,
): string | undefined {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(
      /[\s-]+/g,
      '_',
    )

  return normalized || undefined
}

export function useChurnScores(
  filters: ChurnFilters,
) {
  const acquisitionChannel =
    normalizeDimension(
      filters.acquisitionChannel,
    )

  const deviceType =
    normalizeDimension(
      filters.deviceType,
    )

  return useQuery({
    queryKey:
      churnKeys.scores(
        filters.limit,
        filters.offset,
        filters.riskBand,
        acquisitionChannel ?? '',
        deviceType ?? '',
      ),

    queryFn: () =>
      mlApi.scores({
        limit:
          filters.limit,

        offset:
          filters.offset,

        risk_band:
          filters.riskBand ??
          undefined,

        acquisition_channel:
          acquisitionChannel,

        device_type:
          deviceType,
      }),

    staleTime:
      STALE_TIME,

    placeholderData:
      (previous) =>
        previous,
      })
}