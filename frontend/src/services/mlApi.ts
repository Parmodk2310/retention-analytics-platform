import type {
  ChurnScore,
  ChurnSummary,
  ModelHealth,
  RiskBand,
} from '@/types/api'
import { api } from './api'

export type ChurnScoreParams = {
  limit?: number
  offset?: number
  risk_band?: RiskBand
  acquisition_channel?: string
  device_type?: string
}

function cleanParams(
  params?: ChurnScoreParams,
): ChurnScoreParams {
  if (!params) {
    return {}
  }

  return {
    ...params,
    acquisition_channel:
      params.acquisition_channel ||
      undefined,
    device_type:
      params.device_type ||
      undefined,
  }
}

export const mlApi = {
  scores: async (
    params?: ChurnScoreParams,
  ): Promise<ChurnScore[]> =>
    (
      await api.get<ChurnScore[]>(
        '/churn/scores',
        {
          params: cleanParams(params),
        },
      )
    ).data,

  summary: async (): Promise<ChurnSummary> =>
    (
      await api.get<ChurnSummary>(
        '/churn/summary',
      )
    ).data,

  modelHealth:
    async (): Promise<ModelHealth> =>
      (
        await api.get<ModelHealth>(
          '/churn/model-health',
        )
      ).data,
}

export type {
  ChurnScore,
  ChurnSummary,
  ModelHealth,
  RiskBand,
}