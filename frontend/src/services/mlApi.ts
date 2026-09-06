import { api } from './api'
import type { ChurnScore, ModelHealth } from '@/types/api'

type ChurnScoreParams = {
  limit?: number
  offset?: number
  risk_band?: string
}

export const mlApi = {
  scores: async (params?: ChurnScoreParams): Promise<ChurnScore[]> =>
    (await api.get<ChurnScore[]>('/churn/scores', { params })).data,

  modelHealth: async (): Promise<ModelHealth | null> =>
    (await api.get<ModelHealth | null>('/churn/model-health')).data,
}
