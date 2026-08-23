import { Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { Dashboard } from '@/pages/Dashboard'
import { CohortAnalysis } from '@/pages/CohortAnalysis'
import { FunnelAnalysis } from '@/pages/FunnelAnalysis'
import { ChurnPrediction } from '@/pages/ChurnPrediction'
import { Experiments } from '@/pages/Experiments'

export default function App() {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cohorts" element={<CohortAnalysis />} />
            <Route path="/funnel" element={<FunnelAnalysis />} />
            <Route path="/churn" element={<ChurnPrediction />} />
            <Route path="/experiments" element={<Experiments />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}