export const compact=(v:number)=>new Intl.NumberFormat('en',{notation:'compact',maximumFractionDigits:1}).format(v)
export const percent=(v:number)=>new Intl.NumberFormat('en',{style:'percent',maximumFractionDigits:1}).format(v)
export const money=(v:number)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(v)
export const dateLabel=(v:string)=>new Intl.DateTimeFormat('en',{dateStyle:'medium'}).format(new Date(v))
