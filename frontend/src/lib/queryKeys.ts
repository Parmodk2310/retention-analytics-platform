export const analyticsKeys = {
  all: ['analytics'] as const,
  overview: (days: number, channel: string | null) =>
    [...analyticsKeys.all, 'overview', days, channel] as const,
  activity: (days: number, channel: string | null) =>
    [...analyticsKeys.all, 'activity', days, channel] as const,
  funnel: (days: number, channel: string | null) =>
    [...analyticsKeys.all, 'funnel', days, channel] as const,
  retention: (months: number, channel: string | null) =>
    [...analyticsKeys.all, 'retention', months, channel] as const,
  revenue: (months: number, channel: string | null) =>
    [...analyticsKeys.all, 'revenue', months, channel] as const,
  channels: (days: number) => [...analyticsKeys.all, 'channels', days] as const,
}
