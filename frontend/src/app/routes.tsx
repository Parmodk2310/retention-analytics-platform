import { lazy, Suspense, type ComponentType } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { AppShell } from '@/components/layout/AppShell'
import { Skeleton } from '@/components/ui/Skeleton'
import Login from '@/pages/Login'

const Dashboard = lazy(() => import('@/pages/Dashboard'))
const ProductMetrics = lazy(() => import('@/pages/ProductMetrics'))
const FunnelAnalysis = lazy(() => import('@/pages/FunnelAnalysis'))
const CohortAnalysis = lazy(() => import('@/pages/CohortAnalysis'))
const ChurnPrediction = lazy(() => import('@/pages/ChurnPrediction'))
const Experiments = lazy(() => import('@/pages/Experiments'))
const ExperimentDetail = lazy(() => import('@/pages/ExperimentDetail'))
const ModelHealth = lazy(() => import('@/pages/ModelHealth'))
const Settings = lazy(() => import('@/pages/Settings'))

function page(Component: ComponentType) {
  return (
    <Suspense fallback={<Skeleton className="h-[520px]" />}>
      <Component />
    </Suspense>
  )
}

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
          { index: true, element: page(Dashboard) },
          { path: '/metrics', element: page(ProductMetrics) },
          { path: '/funnel', element: page(FunnelAnalysis) },
          { path: '/cohorts', element: page(CohortAnalysis) },
          { path: '/churn', element: page(ChurnPrediction) },
          { path: '/experiments', element: page(Experiments) },
          { path: '/experiments/:id', element: page(ExperimentDetail) },
          { path: '/model-health', element: page(ModelHealth) },
          { path: '/settings', element: page(Settings) },
        ],
      },
    ],
  },
])
