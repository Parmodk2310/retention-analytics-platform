import { useQuery } from '@tanstack/react-query'

import { analyticsKeys } from '@/lib/queryKeys'
import { analyticsApi } from '@/services/analyticsApi'
import { useUIStore } from '@/store/uiStore'

const STALE_TIME = 15_000
const REFETCH_INTERVAL = 30_000

export function monthsForDays(days: number) {
  if (days <= 30) return 1
  if (days <= 90) return 3
  return 12
}

export function useOverview() {
  const days = useUIStore((state) => state.days)
  const channel = useUIStore((state) => state.channel)

  return useQuery({
    queryKey: analyticsKeys.overview(days, channel),
    queryFn: () => analyticsApi.overview(days, channel),
    staleTime: STALE_TIME,
    placeholderData: (previous) => previous,
  })
}

export function useActivity() {
  const days = useUIStore((state) => state.days)
  const channel = useUIStore((state) => state.channel)

  return useQuery({
    queryKey: analyticsKeys.activity(days, channel),
    queryFn: () => analyticsApi.activity(days, channel),
    staleTime: STALE_TIME,
    placeholderData: (previous) => previous,
  })
}

export function useFunnel() {
  const days = useUIStore((state) => state.days)
  const channel = useUIStore((state) => state.channel)

  return useQuery({
    queryKey: analyticsKeys.funnel(days, channel),
    queryFn: () => analyticsApi.funnel(days, channel),
    staleTime: STALE_TIME,
    placeholderData: (previous) => previous,
  })
}

export function useRetention() {
  const months = useUIStore((state) => state.cohortMonths)
  const channel = useUIStore((state) => state.channel)

  return useQuery({
    queryKey: analyticsKeys.retention(months, channel),
    queryFn: () => analyticsApi.retention(months, channel),
    staleTime: STALE_TIME,
    placeholderData: (previous) => previous,
  })
}

export function useRevenue() {
  const days = useUIStore((state) => state.days)
  const channel = useUIStore((state) => state.channel)
  const months = monthsForDays(days)

  return useQuery({
    queryKey: analyticsKeys.revenue(months, channel),
    queryFn: () => analyticsApi.revenue(months, channel),
    staleTime: STALE_TIME,
    placeholderData: (previous) => previous,
  })
}

export function useChannels() {
  const days = useUIStore((state) => state.days)

  return useQuery({
    queryKey: analyticsKeys.channels(days),
    queryFn: () => analyticsApi.channels(days),
    staleTime: STALE_TIME,
    refetchInterval: REFETCH_INTERVAL,
    placeholderData: (previous) => previous,
  })
}
