import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Database,
  ExternalLink,
  Gauge,
  Github,
  Layers3,
  RadioTower,
  ServerCog,
  UserRound,
} from "lucide-react";

import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Skeleton } from "@/components/ui/Skeleton";
import { BRAND } from "@/config/brand";
import { systemKeys } from "@/lib/queryKeys";
import { systemApi } from "@/services/systemApi";

import type { EventPipelineStatus } from "@/types/api";

const capabilities = [
  "Product Analytics",
  "Cohort Retention",
  "Funnel Diagnostics",
  "Churn ML",
  "A/B Experimentation",
  "Redis Streams",
  "Observability",
  "AWS-ready Infrastructure",
];

const platformComponents = [
  {
    name: "PostgreSQL",
    description: "Primary source of truth for product, experiment, and ML data",
  },
  {
    name: "Redis Streams",
    description:
      "Durable event ingestion, consumer groups, retry, and recovery",
  },
  {
    name: "Prometheus",
    description: "Application and event-pipeline metrics collection",
  },
  {
    name: "Grafana",
    description: "Operational dashboards and pipeline visibility",
  },
  {
    name: "Alertmanager",
    description: "Routing for API and event-pipeline alerts",
  },
  {
    name: "Sentry",
    description: "Optional application error-tracing integration",
  },
];

function formatFreshness(seconds: number | null): string {
  if (seconds === null) return "Unknown";
  if (seconds < 1) return "< 1 s";
  if (seconds < 60) return `${seconds.toFixed(1)} s`;

  const minutes = seconds / 60;
  if (minutes < 60) return `${minutes.toFixed(1)} min`;

  return `${(minutes / 60).toFixed(1)} hr`;
}

function formatDateTime(value: string | null): string {
  if (!value) return "Not available";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not available";

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

function PipelineStatusBadge({
  status,
}: {
  status: EventPipelineStatus["status"];
}) {
  const styles = {
    fresh:
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    stale:
      "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400",
    unknown: "border-border bg-muted/40",
  };

  const labels = {
    fresh: "Fresh",
    stale: "Stale",
    unknown: "Unknown",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${styles[status]}`}
    >
      {labels[status]}
    </span>
  );
}

function MetricRow({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b py-2.5 last:border-b-0">
      <span className="text-sm opacity-60">{label}</span>
      <span className="text-right text-sm font-medium">{value}</span>
    </div>
  );
}

function SystemInfoSkeleton() {
  return (
    <Card className="p-5">
      <Skeleton className="mb-4 h-6 w-40" />
      <Skeleton className="mb-3 h-8 w-24" />
      <Skeleton className="mb-2 h-5 w-full" />
      <Skeleton className="h-5 w-2/3" />
    </Card>
  );
}

export default function Settings() {
  const infoQuery = useQuery({
    queryKey: systemKeys.info(),
    queryFn: systemApi.info,
    staleTime: 5 * 60 * 1000,
  });

  const pipelineQuery = useQuery({
    queryKey: systemKeys.eventPipeline(),
    queryFn: systemApi.eventPipeline,
    refetchInterval: 15_000,
    refetchIntervalInBackground: false,
  });

  const pipeline = pipelineQuery.data;

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm opacity-55">
          Workspace configuration, runtime health, and engineering metadata
        </p>
        <h2 className="text-2xl font-semibold">Settings</h2>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <Layers3 className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">About this project</h3>
          </div>

          <p className="max-w-3xl text-sm leading-6 opacity-70">
            {BRAND.projectDescription}
          </p>

          <p className="mt-3 text-sm font-medium">{BRAND.projectScale}</p>

          <div className="mt-4 flex flex-wrap gap-2">
            {capabilities.map((item) => (
              <span
                key={item}
                className="rounded-full border bg-muted/30 px-2.5 py-1 text-xs opacity-80"
              >
                {item}
              </span>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <UserRound className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Engineer</h3>
          </div>

          <p className="text-lg font-semibold">{BRAND.ownerName}</p>

          <p className="text-sm opacity-60">{BRAND.ownerTitle}</p>

          <p className="mt-3 text-sm leading-6 opacity-65">
            End-to-end product data science system covering analytics,
            experimentation, machine learning, backend engineering,
            observability, and cloud-ready infrastructure.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <a
              href={BRAND.portfolioUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition hover:bg-muted"
            >
              Portfolio
              <ExternalLink className="h-3.5 w-3.5" />
            </a>

            <a
              href={BRAND.repositoryUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition hover:bg-muted"
            >
              <Github className="h-4 w-4" />
              Source
            </a>
          </div>
        </Card>
      </div>

      <div>
        <div className="mb-3">
          <p className="text-sm opacity-55">Runtime observability</p>
          <h3 className="text-lg font-semibold">System Health</h3>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {infoQuery.isPending ? (
            <SystemInfoSkeleton />
          ) : infoQuery.isError ? (
            <ErrorState
              message="Could not load system information"
              onRetry={() => void infoQuery.refetch()}
            />
          ) : (
            <Card className="p-5">
              <div className="mb-4 flex items-start justify-between gap-4">
                <div className="flex items-center gap-2">
                  <ServerCog className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">Application</h3>
                </div>

                <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                  Available
                </span>
              </div>

              <MetricRow label="Version" value={infoQuery.data.version} />

              <MetricRow
                label="Environment"
                value={infoQuery.data.environment}
              />

              <MetricRow
                label="Realtime ingestion"
                value={
                  infoQuery.data.features.realtime ? "Enabled" : "Disabled"
                }
              />

              <MetricRow
                label="Churn ML"
                value={
                  infoQuery.data.features.churn_ml ? "Enabled" : "Disabled"
                }
              />

              <MetricRow
                label="Experimentation"
                value={
                  infoQuery.data.features.experimentation
                    ? "Enabled"
                    : "Disabled"
                }
              />
            </Card>
          )}

          {pipelineQuery.isPending ? (
            <SystemInfoSkeleton />
          ) : pipelineQuery.isError ? (
            <ErrorState
              message="Could not load event-pipeline health"
              onRetry={() => void pipelineQuery.refetch()}
            />
          ) : pipeline ? (
            <Card className="p-5">
              <div className="mb-4 flex items-start justify-between gap-4">
                <div className="flex items-center gap-2">
                  <RadioTower className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">Event Pipeline</h3>
                </div>

                <PipelineStatusBadge status={pipeline.status} />
              </div>

              <MetricRow
                label="Freshness"
                value={formatFreshness(pipeline.freshness_seconds)}
              />

              <MetricRow
                label="Backlog"
                value={pipeline.backlog.toLocaleString()}
              />

              <MetricRow
                label="Pending"
                value={pipeline.pending.toLocaleString()}
              />

              <MetricRow
                label="Consumer lag"
                value={pipeline.lag.toLocaleString()}
              />

              <MetricRow
                label="Last persisted"
                value={formatDateTime(pipeline.last_persisted_at)}
              />

              <MetricRow
                label="Latest event time"
                value={formatDateTime(pipeline.latest_event_time)}
              />

              <MetricRow
                label="Stream checkpoint"
                value={pipeline.last_stream_id ?? "Not available"}
              />

              <p className="mt-4 text-xs leading-5 opacity-55">
                Pipeline health refreshes every 15 seconds from the protected
                system-status API.
              </p>
            </Card>
          ) : null}
        </div>
      </div>

      <Card className="p-5">
        <div className="mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Platform Architecture</h3>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {platformComponents.map((component) => (
            <div
              key={component.name}
              className="rounded-xl border bg-muted/20 p-4"
            >
              <p className="text-sm font-semibold">{component.name}</p>

              <p className="mt-1 text-xs leading-5 opacity-60">
                {component.description}
              </p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <Gauge className="mt-0.5 h-5 w-5 text-primary" />

          <div>
            <h3 className="font-semibold">Observability Boundary</h3>

            <p className="mt-1 max-w-4xl text-sm leading-6 opacity-65">
              Prometheus collects API and worker metrics, Grafana provides
              operational dashboards, and Alertmanager evaluates configured
              reliability alerts. PostgreSQL remains the application source of
              truth while Redis Streams provides durable event ingestion.
            </p>
          </div>
        </div>
      </Card>

      <div className="flex items-center gap-2 text-xs opacity-55">
        <Activity className="h-3.5 w-3.5" />
        Secrets and infrastructure credentials are intentionally excluded from
        system-health responses.
      </div>
    </div>
  );
}
