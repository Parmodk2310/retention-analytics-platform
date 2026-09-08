import { api } from './api'
import type { Experiment, ExperimentResults } from '@/types/api'
import type { ExperimentIntelligenceResult } from "../types/experimentIntelligence";


export const experimentApi = {
  list: async (): Promise<Experiment[]> =>
    (await api.get<Experiment[]>('/experiments')).data,

  create: async (payload: unknown): Promise<Experiment> =>
    (await api.post<Experiment>('/experiments', payload)).data,

  results: async (id: string): Promise<ExperimentResults> =>
    (await api.get<ExperimentResults>(`/experiments/${id}/results`)).data,
}

export async function getExperimentResults(
  experimentId: string,
): Promise<ExperimentIntelligenceResult> {
  const { data } = await api.get<ExperimentIntelligenceResult>(
    `/experiments/${experimentId}/results`,
  );

  return data;
}