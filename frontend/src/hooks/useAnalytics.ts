import {useQuery} from '@tanstack/react-query';import {analyticsApi} from '@/services/analyticsApi';import {useUIStore} from '@/store/uiStore';
export function useOverview(){const days=useUIStore(s=>s.days);return useQuery({queryKey:['overview',days],queryFn:()=>analyticsApi.overview(days),staleTime:60_000})}
export function useActivity(){const days=useUIStore(s=>s.days);return useQuery({queryKey:['activity',days],queryFn:()=>analyticsApi.activity(days),staleTime:60_000})}
export function useFunnel(){const days=useUIStore(s=>s.days),channel=useUIStore(s=>s.channel);return useQuery({queryKey:['funnel',days,channel],queryFn:()=>analyticsApi.funnel(days,channel)})}
export function useRetention(){const channel=useUIStore(s=>s.channel);return useQuery({queryKey:['retention',channel],queryFn:()=>analyticsApi.retention(12,channel)})}
