import {
  Activity,
  BrainCircuit,
  CalendarClock,
  CheckCircle2,
  Database,
  Gauge,
  GitBranch,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Target,
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { mlApi } from '@/services/mlApi'
import type { ModelHealth as ModelHealthType } from '@/types/api'

const percent = new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})
const number = new Intl.NumberFormat('en-US')

function metric(metrics: Record<string, number>, key: string): number | null {
  const value = metrics[key]
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function fixed(value: number | null, digits = 3): string {
  return value === null ? '—' : value.toFixed(digits)
}

function percentage(value: number | null): string {
  return value === null ? '—' : percent.format(value)
}

function displayAlgorithm(value: string): string {
  return value.replaceAll('_', ' ').toUpperCase()
}

function Metric({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint?: string
}) {
  return (
    <div className="rounded-xl border bg-background/40 p-4">
      <p className="text-xs font-medium uppercase tracking-wide opacity-50">{label}</p>
      <p className="mt-2 text-xl font-semibold tabular-nums">{value}</p>
      {hint && <p className="mt-1 text-xs leading-relaxed opacity-50">{hint}</p>}
    </div>
  )
}

function SectionHeader({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Activity
  title: string
  description: string
}) {
  return (
    <div className="mb-5">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-primary" />
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="mt-1 text-xs leading-relaxed opacity-50">{description}</p>
    </div>
  )
}

function StatusBadge({ model }: { model: ModelHealthType }) {
  const brierSkill = metric(model.metrics, 'brier_skill_score')
  const rocAuc = metric(model.metrics, 'roc_auc')
  const healthy = brierSkill !== null && brierSkill > 0 && rocAuc !== null && rocAuc >= 0.7
  const Icon = healthy ? CheckCircle2 : ShieldAlert

  return (
    <span
      className={
        healthy
          ? 'inline-flex items-center gap-1.5 rounded-full bg-success/10 px-3 py-1 text-xs font-semibold text-success'
          : 'inline-flex items-center gap-1.5 rounded-full bg-warning/10 px-3 py-1 text-xs font-semibold text-warning'
      }
    >
      <Icon className="h-3.5 w-3.5" />
      {healthy ? 'Healthy' : 'Review required'}
    </span>
  )
}

function ModelOverview({ model }: { model: ModelHealthType }) {
  const threshold = metric(model.metrics, 'threshold')

  return (
    <Card className="p-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <div className="flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-primary" />
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
              Production model
            </p>
          </div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight">Churn model health</h2>
          <p className="mt-1 max-w-3xl text-sm opacity-60">
            Temporal evaluation, calibration quality, ranking performance and production decision
            policy for the future inactivity model.
          </p>
        </div>
        <StatusBadge model={model} />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Metric label="Model version" value={model.model_version} />
        <Metric
          label="Algorithm"
          value={displayAlgorithm(model.algorithm)}
          hint={model.calibration ? 'Sigmoid-calibrated probabilities' : 'Calibration unavailable'}
        />
        <Metric
          label="Target"
          value={
            model.dataset
              ? `${model.dataset.label_window_days}-day inactivity`
              : 'Inactivity target'
          }
        />
        <Metric
          label="Decision threshold"
          value={fixed(threshold, 2)}
          hint="Selected on validation data"
        />
        <Metric
          label="Trained"
          value={new Date(model.trained_at).toLocaleDateString()}
          hint={new Date(model.trained_at).toLocaleTimeString()}
        />
      </div>
    </Card>
  )
}

function Discrimination({ model }: { model: ModelHealthType }) {
  const metrics = model.metrics

  return (
    <Card className="p-5">
      <SectionHeader
        icon={Target}
        title="Discrimination and ranking"
        description="How well the model ranks future inactive users above active users."
      />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <Metric
          label="ROC-AUC"
          value={fixed(metric(metrics, 'roc_auc'))}
          hint="Threshold-independent ranking"
        />
        <Metric label="PR-AUC" value={fixed(metric(metrics, 'pr_auc'))} />
        <Metric
          label="PR baseline"
          value={fixed(metric(metrics, 'pr_auc_baseline'))}
          hint="Positive-class prevalence"
        />
        <Metric
          label="Normalized PR-AUC"
          value={fixed(metric(metrics, 'normalized_pr_auc'))}
          hint="Improvement above prevalence"
        />
        <Metric
          label="Lift at top 10%"
          value={
            metric(metrics, 'lift_at_10pct') === null
              ? '—'
              : `${fixed(metric(metrics, 'lift_at_10pct'))}×`
          }
        />
        <Metric
          label="Recall at top 10%"
          value={percentage(metric(metrics, 'recall_at_10pct'))}
        />
      </div>
    </Card>
  )
}

function CalibrationQuality({ model }: { model: ModelHealthType }) {
  const metrics = model.metrics

  return (
    <Card className="p-5">
      <SectionHeader
        icon={Gauge}
        title="Calibration and decision quality"
        description="Probability quality and thresholded performance on the untouched test set."
      />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="Brier score"
          value={fixed(metric(metrics, 'brier'))}
          hint="Lower is better"
        />
        <Metric label="Brier baseline" value={fixed(metric(metrics, 'brier_baseline'))} />
        <Metric
          label="Brier skill"
          value={percentage(metric(metrics, 'brier_skill_score'))}
          hint="Improvement over baseline"
        />
        <Metric
          label="Balanced accuracy"
          value={fixed(metric(metrics, 'balanced_accuracy'))}
        />
        <Metric
          label="MCC"
          value={fixed(metric(metrics, 'mcc'))}
          hint="Robust under class imbalance"
        />
        <Metric label="Precision" value={percentage(metric(metrics, 'precision'))} />
        <Metric label="Recall" value={percentage(metric(metrics, 'recall'))} />
        <Metric label="Specificity" value={percentage(metric(metrics, 'specificity'))} />
      </div>
    </Card>
  )
}

function ConfusionMatrix({ model }: { model: ModelHealthType }) {
  const metrics = model.metrics
  const cells = [
    ['True negative', metric(metrics, 'true_negative')],
    ['False positive', metric(metrics, 'false_positive')],
    ['False negative', metric(metrics, 'false_negative')],
    ['True positive', metric(metrics, 'true_positive')],
  ] as const

  return (
    <Card className="p-5">
      <SectionHeader
        icon={Scale}
        title="Confusion matrix"
        description="Test-set decisions using the validation-selected threshold."
      />
      <div className="grid grid-cols-2 gap-3">
        {cells.map(([label, value]) => (
          <Metric key={label} label={label} value={value === null ? '—' : number.format(value)} />
        ))}
      </div>
    </Card>
  )
}

function TemporalGeneralization({ model }: { model: ModelHealthType }) {
  const splits = model.splits
  const drift = model.label_drift
  if (!splits || !drift) return null

  return (
    <Card className="p-5">
      <SectionHeader
        icon={GitBranch}
        title="Temporal generalization"
        description="Whole snapshot dates remain separated across fit, validation and test periods."
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="Train prevalence"
          value={percentage(drift.train_prevalence)}
          hint={`${splits.train.start} → ${splits.train.end}`}
        />
        <Metric
          label="Validation prevalence"
          value={percentage(drift.validation_prevalence)}
          hint={`${splits.validation.start} → ${splits.validation.end}`}
        />
        <Metric
          label="Test prevalence"
          value={percentage(drift.test_prevalence)}
          hint={`${splits.test.start} → ${splits.test.end}`}
        />
        <Metric
          label="Train to test drift"
          value={`${drift.train_to_test_pp >= 0 ? '+' : ''}${drift.train_to_test_pp.toFixed(2)} pp`}
          hint="Label prevalence shift"
        />
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[700px] text-sm">
          <thead>
            <tr className="border-b text-left text-xs uppercase tracking-wide opacity-50">
              <th className="py-3">Split</th>
              <th className="py-3">Rows</th>
              <th className="py-3">Snapshots</th>
              <th className="py-3">Start</th>
              <th className="py-3">End</th>
              <th className="py-3">Churn prevalence</th>
            </tr>
          </thead>
          <tbody>
            {(['train', 'validation', 'test'] as const).map((name) => {
              const split = splits[name]
              return (
                <tr key={name} className="border-b last:border-0">
                  <td className="py-3 font-medium capitalize">{name}</td>
                  <td className="py-3 tabular-nums">{number.format(split.rows)}</td>
                  <td className="py-3 tabular-nums">{split.snapshot_count}</td>
                  <td className="py-3">{split.start}</td>
                  <td className="py-3">{split.end}</td>
                  <td className="py-3">{percentage(split.churn_rate)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function CalibrationPolicy({ model }: { model: ModelHealthType }) {
  const calibration = model.calibration
  const riskBands = model.risk_bands
  if (!calibration && !riskBands) return null

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <Card className="p-5">
        <SectionHeader
          icon={ShieldCheck}
          title="Calibration policy"
          description="Calibration is fitted after the base classifier without using validation or test labels."
        />
        {calibration ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric label="Method" value={calibration.method.replaceAll('_', ' ')} />
            <Metric label="Calibration snapshot" value={calibration.calibration_snapshot} />
            <Metric label="Base fit rows" value={number.format(calibration.fit_rows)} />
            <Metric
              label="Calibration rows"
              value={number.format(calibration.calibration_rows)}
            />
          </div>
        ) : (
          <p className="text-sm opacity-50">Calibration metadata is unavailable.</p>
        )}
      </Card>

      <Card className="p-5">
        <SectionHeader
          icon={Activity}
          title="Risk policy"
          description="Risk bands use validation-score quantiles instead of arbitrary cutoffs."
        />
        {riskBands ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric label="Critical" value={`≥ ${riskBands.thresholds.critical.toFixed(4)}`} />
            <Metric label="High" value={`≥ ${riskBands.thresholds.high.toFixed(4)}`} />
            <Metric label="Medium" value={`≥ ${riskBands.thresholds.medium.toFixed(4)}`} />
            <Metric label="Low" value={`< ${riskBands.thresholds.medium.toFixed(4)}`} />
          </div>
        ) : (
          <p className="text-sm opacity-50">Risk-band metadata is unavailable.</p>
        )}
      </Card>
    </div>
  )
}

function DatasetCoverage({ model }: { model: ModelHealthType }) {
  if (!model.dataset) return null

  return (
    <Card className="p-5">
      <SectionHeader
        icon={Database}
        title="Dataset contract"
        description="Feature and target windows used by the leakage-safe training dataset."
      />
      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Feature window" value={`${model.dataset.feature_window_days} days`} />
        <Metric label="Label window" value={`${model.dataset.label_window_days} days`} />
        <Metric label="Training snapshots" value={String(model.dataset.snapshot_count)} />
      </div>
    </Card>
  )
}

export default function ModelHealth() {
  const query = useQuery({
    queryKey: ['model-health'],
    queryFn: mlApi.modelHealth,
  })

  if (query.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-80" />
      </div>
    )
  }

  if (query.isError) {
    return (
      <ErrorState
        message="Model health is unavailable"
        onRetry={() => query.refetch()}
      />
    )
  }

  if (!query.data) {
    return (
      <EmptyState
        title="No trained model"
        description="Run the training pipeline after you have sufficient historical event coverage."
      />
    )
  }

  const model = query.data
  const testSplit = model.splits?.test

  return (
    <div className="space-y-5">
      <ModelOverview model={model} />

      <div className="grid gap-4 xl:grid-cols-2">
        <Discrimination model={model} />
        <CalibrationQuality model={model} />
      </div>

      <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <TemporalGeneralization model={model} />
        <ConfusionMatrix model={model} />
      </div>

      <CalibrationPolicy model={model} />
      <DatasetCoverage model={model} />

      <Card className="p-4">
        <div className="flex items-start gap-3">
          <CalendarClock className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <p className="text-xs leading-relaxed opacity-60">
            Final metrics are reported on the untouched temporal test period
            {testSplit ? ` from ${testSplit.start} through ${testSplit.end}` : ''}. Model
            selection, calibration and threshold selection use earlier snapshots. Plain accuracy
            is intentionally omitted because the inactivity target is imbalanced.
          </p>
        </div>
      </Card>
    </div>
  )
}