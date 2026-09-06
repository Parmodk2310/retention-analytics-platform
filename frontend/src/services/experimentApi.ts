import { api } from './api'
import type { Experiment, ExperimentResults } from '@/types/api'

export const experimentApi = {
  list: async (): Promise<Experiment[]> =>
    (await api.get<Experiment[]>('/experiments')).data,

  create: async (payload: unknown): Promise<Experiment> =>
    (await api.post<Experiment>('/experiments', payload)).data,

  results: async (id: string): Promise<ExperimentResults> =>
    (await api.get<ExperimentResults>(`/experiments/${id}/results`)).data,
}
