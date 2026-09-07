import type {
  ActivityPoint,
  ChannelPerformance,
  CohortCell,
  FunnelStage,
  Overview,
  RevenuePoint,
} from '@/types/api'
import { api } from './api'

type Channel = string | null | undefined

function channelParam(channel: Channel) {
  return channel || undefined
}

export const analyticsApi = {
  overview: async (days = 30, channel?: Channel): Promise<Overview> =>
    (
      await api.get<Overview>('/analytics/overview', {
        params: { days, channel: channelParam(channel) },
      })
    ).data,

  activity: async (days = 30, channel?: Channel): Promise<ActivityPoint[]> =>
    (
      await api.get<ActivityPoint[]>('/analytics/activity', {
        params: { days, channel: channelParam(channel) },
      })
    ).data,

  funnel: async (days = 30, channel?: Channel): Promise<FunnelStage[]> =>
    (
      await api.get<FunnelStage[]>('/analytics/funnel', {
        params: { days, channel: channelParam(channel) },
      })
    ).data,

  retention: async (months = 12, channel?: Channel): Promise<CohortCell[]> =>
    (
      await api.get<CohortCell[]>('/analytics/retention', {
        params: { months, channel: channelParam(channel) },
      })
    ).data,

  revenue: async (months = 12, channel?: Channel): Promise<RevenuePoint[]> =>
    (
      await api.get<RevenuePoint[]>('/analytics/revenue', {
        params: { months, channel: channelParam(channel) },
      })
    ).data,

  channels: async (days = 30): Promise<ChannelPerformance[]> =>
    (await api.get<ChannelPerformance[]>('/analytics/channels', { params: { days } })).data,
}
