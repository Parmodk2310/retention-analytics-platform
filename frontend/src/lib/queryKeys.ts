import type {
  RiskBand,
} from '@/types/api'

export const analyticsKeys = {
  all: ['analytics'] as const,

  overview: (
    days: number,
    channel: string | null,
  ) =>
    [
      ...analyticsKeys.all,
      'overview',
      days,
      channel,
    ] as const,

  activity: (
    days: number,
    channel: string | null,
  ) =>
    [
      ...analyticsKeys.all,
      'activity',
      days,
      channel,
    ] as const,

  funnel: (
    days: number,
    channel: string | null,
  ) =>
    [
      ...analyticsKeys.all,
      'funnel',
      days,
      channel,
    ] as const,

  retention: (
    months: number,
    channel: string | null,
  ) =>
    [
      ...analyticsKeys.all,
      'retention',
      months,
      channel,
    ] as const,

  revenue: (
    months: number,
    channel: string | null,
  ) =>
    [
      ...analyticsKeys.all,
      'revenue',
      months,
      channel,
    ] as const,

  channels: (days: number) =>
    [
      ...analyticsKeys.all,
      'channels',
      days,
    ] as const,
}

export const churnKeys = {
  all: ['churn'] as const,

  summary: () =>
    [
      ...churnKeys.all,
      'summary',
    ] as const,

  modelHealth: () =>
    [
      ...churnKeys.all,
      'model-health',
    ] as const,

  scores: (
    limit: number,
    offset: number,
    riskBand: RiskBand | null,
    acquisitionChannel: string,
    deviceType: string,
  ) =>
    [
      ...churnKeys.all,
      'scores',
      limit,
      offset,
      riskBand,
      acquisitionChannel,
      deviceType,
    ] as const,
}

export const systemKeys = {
  all: ['system'] as const,

  info: () =>
    [
      ...systemKeys.all,
      'info',
    ] as const,

  eventPipeline: () =>
    [
      ...systemKeys.all,
      'event-pipeline',
    ] as const,
}