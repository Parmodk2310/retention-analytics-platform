import {create} from 'zustand';
type Filters={days:number;channel:string|null;setDays:(n:number)=>void;setChannel:(s:string|null)=>void}
export const useUIStore=create<Filters>((set)=>({days:30,channel:null,setDays:(days)=>set({days}),setChannel:(channel)=>set({channel})}))
