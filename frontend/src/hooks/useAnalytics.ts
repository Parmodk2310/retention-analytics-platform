import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/analyticsApi'

export function useMetrics(date?: string) {
  return useQuery({
    queryKey: ['metrics', date],
    queryFn: () => analyticsApi.getMetrics(date),
    staleTime: 5 * 60 * 1000,
  })
}

export function useFunnel(days = 30) {
  return useQuery({
    queryKey: ['funnel', days],
    queryFn: () => analyticsApi.getFunnel(days),
    staleTime: 5 * 60 * 1000,
  })
}

export function useCohortRetention(months = 12) {
  return useQuery({
    queryKey: ['cohorts', months],
    queryFn: () => analyticsApi.getCohortRetention(months),
    staleTime: 10 * 60 * 1000,
  })
}