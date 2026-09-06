import { ExternalLink, Github, LogOut, Moon, Sun, UserRound } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { GlobalFilters } from '@/components/filters/GlobalFilters';
import { BRAND } from '@/config/brand';
import { authApi } from '@/services/authApi';
import { useAuthStore } from '@/store/authStore';

export function Header() {
  const loc = useLocation();
  const clear = useAuthStore((s) => s.clear);
  const account = useAuthStore((s) => s.account);
  const [dark, setDark] = useState(
    () =>
      localStorage.theme === 'dark' ||
      (!('theme' in localStorage) && matchMedia('(prefers-color-scheme: dark)').matches),
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.theme = dark ? 'dark' : 'light';
  }, [dark]);

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      clear();
    }
  };

  const title = loc.pathname === '/' ? 'Overview' : loc.pathname.split('/').filter(Boolean).join(' / ');

  return (
    <header className="sticky top-0 z-20 border-b bg-background/90 px-5 py-4 backdrop-blur">
      <div className="mb-3 flex items-center justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-xl font-semibold">{title}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-x-2 text-xs opacity-55">
            <UserRound className="h-3.5 w-3.5" />
            <span className="font-medium">{account?.full_name || BRAND.ownerName}</span>
            {account?.email && <span>· {account.email}</span>}
          </div>
        </div>

        <div className="flex shrink-0 gap-2">
          <a
            href={BRAND.portfolioUrl}
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-2 rounded-xl border bg-card px-3 py-2 text-sm transition hover:bg-muted md:flex"
            aria-label="Open Parmod K portfolio"
          >
            Portfolio
            <ExternalLink className="h-3.5 w-3.5 opacity-60" />
          </a>
          <a
            href={BRAND.repositoryUrl}
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-2 rounded-xl border bg-card px-3 py-2 text-sm transition hover:bg-muted sm:flex"
            aria-label="Open GitHub repository"
          >
            <Github className="h-4 w-4" />
            Source
            <ExternalLink className="h-3.5 w-3.5 opacity-60" />
          </a>
          <button
            className="rounded-xl border bg-card p-2"
            onClick={() => setDark((value) => !value)}
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <button className="rounded-xl border bg-card p-2" onClick={logout} aria-label="Sign out">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
      <GlobalFilters />
    </header>
  );
}
