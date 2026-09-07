import { useQuery } from '@tanstack/react-query'
import { experimentApi } from '@/services/experimentApi'

export function useExperiments() {
  return useQuery({
    queryKey: ['experiments'],
    queryFn: experimentApi.list,
    staleTime: 60_000,
  })
}
