import {useQuery} from '@tanstack/react-query';import {experimentApi} from '@/services/experimentApi';export const useExperiments=()=>useQuery({queryKey:['experiments'],queryFn:experimentApi.list})
