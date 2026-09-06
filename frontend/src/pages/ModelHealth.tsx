import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { mlApi } from '@/services/mlApi'

export default function ModelHealth() {
  const query = useQuery({
    queryKey: ['model-health'],
    queryFn: mlApi.modelHealth,
  })

  if (!query.isLoading && !query.data) {
    return (
      <EmptyState
        title="No trained model"
        description="Run the training pipeline after you have at least several months of seeded events."
      />
    )
  }

  const model = query.data

  if (!model) {
    return <p>Loading…</p>
  }

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Model health</h2>

      <Card className="p-5">
        <div className="grid gap-5 md:grid-cols-3">
          <div>
            <p className="text-sm opacity-60">Version</p>
            <p className="font-semibold">{model.model_version}</p>
          </div>
          <div>
            <p className="text-sm opacity-60">Algorithm</p>
            <p className="font-semibold">{model.algorithm}</p>
          </div>
          <div>
            <p className="text-sm opacity-60">Trained</p>
            <p className="font-semibold">{new Date(model.trained_at).toLocaleString()}</p>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(model.metrics).map(([key, value]) => (
          <Card key={key} className="p-5">
            <p className="text-sm opacity-60">{key.replaceAll('_', ' ')}</p>
            <p className="mt-2 text-2xl font-semibold">
              {value <= 3 ? value.toFixed(3) : String(value)}
            </p>
          </Card>
        ))}
      </div>
    </div>
  )
}
