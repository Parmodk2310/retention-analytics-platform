import { create } from 'zustand'

type Filters = {
  days: number
  cohortMonths: number
  channel: string | null
  setDays: (days: number) => void
  setCohortMonths: (months: number) => void
  setChannel: (channel: string | null) => void
}

export const useUIStore = create<Filters>((set) => ({
  days: 30,
  cohortMonths: 12,
  channel: null,

  setDays: (days) => set({ days }),
  setCohortMonths: (cohortMonths) => set({ cohortMonths }),
  setChannel: (channel) => set({ channel }),
}))
