import {api} from './api';export const systemApi={info:async()=>(await api.get('/system/info')).data,ready:async()=>(await api.get('/health/ready')).data}
