import { useQuery } from '@tanstack/react-query';
import { ExternalLink, Github, Layers3, UserRound } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { BRAND } from '@/config/brand';
import { systemApi } from '@/services/systemApi';

const capabilities = [
  'Product Analytics',
  'Cohort Retention',
  'Funnel Diagnostics',
  'Churn ML',
  'A/B Experimentation',
  'Observability',
  'AWS-ready Infrastructure',
];

export default function Settings() {
  const q = useQuery({ queryKey: ['system-info'], queryFn: systemApi.info });

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm opacity-55">Workspace configuration and engineering metadata</p>
        <h2 className="text-2xl font-semibold">Settings</h2>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <Layers3 className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">About this project</h3>
          </div>
          <p className="max-w-3xl text-sm leading-6 opacity-70">{BRAND.projectDescription}</p>
          <p className="mt-3 text-sm font-medium">{BRAND.projectScale}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {capabilities.map((item) => (
              <span key={item} className="rounded-full border bg-muted/30 px-2.5 py-1 text-xs opacity-80">
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
            Built as an end-to-end portfolio system to demonstrate product analytics, statistical experimentation,
            machine learning, backend engineering, frontend delivery, and cloud deployment practices.
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

      <Card className="p-5">
        <h3 className="mb-4 font-semibold">System information</h3>
        <pre className="overflow-auto text-sm">{JSON.stringify(q.data, null, 2)}</pre>
      </Card>

      <p className="text-sm opacity-60">Secrets are intentionally never returned by the system information endpoint.</p>
    </div>
  );
}
