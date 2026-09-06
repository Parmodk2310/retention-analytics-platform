import { api } from './api'
import type {
  ActivityPoint,
  ChannelPerformance,
  CohortCell,
  FunnelStage,
  Overview,
} from '@/types/api'

export const analyticsApi = {
  overview: async (days = 30): Promise<Overview> =>
    (await api.get<Overview>('/analytics/overview', { params: { days } })).data,

  activity: async (days = 30): Promise<ActivityPoint[]> =>
    (await api.get<ActivityPoint[]>('/analytics/activity', { params: { days } })).data,

  funnel: async (days = 30, channel?: string | null): Promise<FunnelStage[]> =>
    (
      await api.get<FunnelStage[]>('/analytics/funnel', {
        params: { days, channel: channel || undefined },
      })
    ).data,

  retention: async (months = 12, channel?: string | null): Promise<CohortCell[]> =>
    (
      await api.get<CohortCell[]>('/analytics/retention', {
        params: { months, channel: channel || undefined },
      })
    ).data,

  revenue: async (months = 12): Promise<unknown> =>
    (await api.get('/analytics/revenue', { params: { months } })).data,

  channels: async (days = 30): Promise<ChannelPerformance[]> =>
    (await api.get<ChannelPerformance[]>('/analytics/channels', { params: { days } })).data,
}
