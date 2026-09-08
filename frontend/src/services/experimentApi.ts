import type {
  AssignmentResponse,
  Experiment,
  ExperimentCreatePayload,
  ExperimentResults,
  ExposureResponse,
} from '@/types/api'
import { api } from './api'

export const experimentApi = {
  list: async (): Promise<Experiment[]> =>
    (await api.get<Experiment[]>('/experiments')).data,

  create: async (payload: ExperimentCreatePayload): Promise<Experiment> =>
    (await api.post<Experiment>('/experiments', payload)).data,

  assign: async (
    experimentId: string,
    userId: string,
  ): Promise<AssignmentResponse> =>
    (
      await api.post<AssignmentResponse>(
        `/experiments/${experimentId}/assign/${userId}`,
      )
    ).data,

  expose: async (
    experimentId: string,
    userId: string,
  ): Promise<ExposureResponse> =>
    (
      await api.post<ExposureResponse>(
        `/experiments/${experimentId}/expose/${userId}`,
      )
    ).data,

  results: async (experimentId: string): Promise<ExperimentResults> =>
    (
      await api.get<ExperimentResults>(
        `/experiments/${experimentId}/results`,
      )
    ).data,
}