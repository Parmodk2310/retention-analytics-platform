import axios from 'axios';import {useAuthStore} from '@/store/authStore';
const baseURL=import.meta.env.VITE_API_BASE_URL || '/api/v1';
export const api=axios.create({baseURL,withCredentials:true,timeout:15000,headers:{'Content-Type':'application/json'}})
api.interceptors.request.use((config)=>{const token=useAuthStore.getState().accessToken;if(token)config.headers.Authorization=`Bearer ${token}`;return config})
let refreshPromise:Promise<string>|null=null
async function refresh(){if(!refreshPromise){refreshPromise=axios.post(`${baseURL}/auth/refresh`,{}, {withCredentials:true}).then(({data})=>{useAuthStore.getState().setSession(data.access_token,data.account);return data.access_token}).finally(()=>{refreshPromise=null})}return refreshPromise}
api.interceptors.response.use((r)=>r,async(error)=>{const original=error.config;if(error.response?.status===401&&!original?._retry&&!original?.url?.includes('/auth/')){original._retry=true;try{original.headers.Authorization=`Bearer ${await refresh()}`;return api(original)}catch{useAuthStore.getState().clear()}}return Promise.reject(error)})
export async function bootstrapSession(){try{const {data}=await axios.post(`${baseURL}/auth/refresh`,{}, {withCredentials:true});useAuthStore.getState().setSession(data.access_token,data.account)}catch{useAuthStore.getState().clear()}}
