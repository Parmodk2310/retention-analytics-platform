import {
  Activity,
  Beaker,
  BrainCircuit,
  ChartNoAxesCombined,
  ExternalLink,
  Filter,
  Fingerprint,
  Gauge,
  Github,
  Settings,
  UsersRound,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { BRAND } from '@/config/brand';
import { cn } from '@/lib/utils';

const items = [
  ['Overview', '/', Gauge],
  ['Product Metrics', '/metrics', Activity],
  ['Funnel', '/funnel', Filter],
  ['Cohorts', '/cohorts', UsersRound],
  ['Churn', '/churn', BrainCircuit],
  ['Experiments', '/experiments', Beaker],
  ['Model Health', '/model-health', Fingerprint],
  ['Settings', '/settings', Settings],
] as const;

export function Sidebar() {
  return (
    <aside className="hidden h-screen w-64 shrink-0 flex-col border-r bg-card/70 p-4 lg:flex">
      <div className="mb-7 flex items-center gap-2 px-2">
        <div className="rounded-xl bg-primary p-2 text-white">
          <ChartNoAxesCombined className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="font-semibold">{BRAND.productName}</p>
          <p className="truncate text-xs opacity-50">{BRAND.productTagline}</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {items.map(([label, to, Icon]) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition hover:bg-muted',
                isActive && 'bg-primary text-white hover:bg-primary',
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-6 border-t pt-4">
        <p className="px-2 text-[10px] font-medium uppercase tracking-[0.18em] opacity-40">
          Engineering portfolio
        </p>
        <p className="mt-2 px-2 text-sm font-semibold">{BRAND.ownerName}</p>
        <p className="px-2 text-xs opacity-50">{BRAND.ownerTitle}</p>

        <div className="mt-3 grid grid-cols-2 gap-2">
          <a
            href={BRAND.portfolioUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center gap-1.5 rounded-xl border px-2 py-2 text-xs transition hover:bg-muted"
          >
            Portfolio
            <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href={BRAND.repositoryUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center gap-1.5 rounded-xl border px-2 py-2 text-xs transition hover:bg-muted"
          >
            <Github className="h-3.5 w-3.5" />
            GitHub
          </a>
        </div>
      </div>
    </aside>
  );
}
