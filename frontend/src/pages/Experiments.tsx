import { Link } from 'react-router-dom'
import { useExperiments } from '@/hooks/useExperiments'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'

export default function Experiments() {
  const query = useExperiments()
  const experiments = query.data ?? []

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-semibold">Experiments</h2>
        <p className="text-sm opacity-60">
          Deterministic assignment, exposure logging, SRM and frequentist inference.
        </p>
      </div>

      {!query.isLoading && experiments.length === 0 ? (
        <EmptyState
          title="No experiments running"
          description="The data generator creates a seeded onboarding experiment, or create one through the API."
        />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {experiments.map((experiment) => (
            <Link key={experiment.id} to={`/experiments/${experiment.id}`}>
              <Card className="p-5 transition hover:-translate-y-0.5">
                <div className="flex justify-between">
                  <p className="font-semibold">{experiment.name}</p>
                  <span className="rounded-full bg-muted px-2 py-1 text-xs">
                    {experiment.status}
                  </span>
                </div>
                <p className="mt-2 text-sm opacity-60">{experiment.hypothesis}</p>
                <p className="mt-4 text-xs">
                  Primary metric · {experiment.primary_metric}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
