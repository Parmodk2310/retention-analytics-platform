import {create} from 'zustand';import type {Account} from '@/types/api';
type State={accessToken:string|null;account:Account|null;setSession:(token:string,account:Account)=>void;clear:()=>void}
export const useAuthStore=create<State>((set)=>({accessToken:null,account:null,setSession:(accessToken,account)=>set({accessToken,account}),clear:()=>set({accessToken:null,account:null})}))
