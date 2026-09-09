import { api } from './api'

import type {
  EventPipelineStatus,
  SystemInfo,
} from '@/types/api'


export const systemApi = {
  info: async (): Promise<SystemInfo> =>
    (await api.get<SystemInfo>('/system/info')).data,

  ready: async () =>
    (await api.get('/health/ready')).data,

  eventPipeline: async (): Promise<EventPipelineStatus> =>
    (await api.get<EventPipelineStatus>('/system/event-pipeline')).data,
}