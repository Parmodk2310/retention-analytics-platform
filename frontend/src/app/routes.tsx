import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { AppShell } from '@/components/layout/AppShell'
import ChurnPrediction from '@/pages/ChurnPrediction'
import CohortAnalysis from '@/pages/CohortAnalysis'
import Dashboard from '@/pages/Dashboard'
import ExperimentDetail from '@/pages/ExperimentDetail'
import Experiments from '@/pages/Experiments'
import FunnelAnalysis from '@/pages/FunnelAnalysis'
import Login from '@/pages/Login'
import ModelHealth from '@/pages/ModelHealth'
import ProductMetrics from '@/pages/ProductMetrics'
import Settings from '@/pages/Settings'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <Dashboard /> },
          { path: '/metrics', element: <ProductMetrics /> },
          { path: '/funnel', element: <FunnelAnalysis /> },
          { path: '/cohorts', element: <CohortAnalysis /> },
          { path: '/churn', element: <ChurnPrediction /> },
          { path: '/experiments', element: <Experiments /> },
          { path: '/experiments/:id', element: <ExperimentDetail /> },
          { path: '/model-health', element: <ModelHealth /> },
          { path: '/settings', element: <Settings /> },
        ],
      },
    ],
  },
])
