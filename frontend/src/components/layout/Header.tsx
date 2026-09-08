import { ExternalLink, Github, LogOut, Moon, Sun, UserRound } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

import { GlobalFilters } from '@/components/filters/GlobalFilters';
import { BRAND } from '@/config/brand';
import { pageTitle } from '@/lib/pageTitle';
import { authApi } from '@/services/authApi';
import { useAuthStore } from '@/store/authStore';

const ANALYTICS_FILTER_PATHS = new Set([
  '/',
  '/metrics',
  '/funnel',
  '/cohorts',
])

export function Header() {
  const location = useLocation()

  const clear = useAuthStore((state) => state.clear)
  const account = useAuthStore((state) => state.account)

  const [dark, setDark] = useState(
    () =>
      localStorage.theme === 'dark' ||
      (!('theme' in localStorage) &&
        matchMedia('(prefers-color-scheme: dark)').matches),
  )

  const title = pageTitle(location.pathname)

  const showGlobalFilters = ANALYTICS_FILTER_PATHS.has(location.pathname)

  const filterMode =
    location.pathname === '/cohorts'
      ? 'months'
      : 'days'

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.theme = dark ? 'dark' : 'light'
  }, [dark])

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clear()
    }
  }

  return (
    <header className="sticky top-0 z-20 border-b bg-background/90 px-5 py-4 backdrop-blur">
      <div
        className={
          showGlobalFilters
            ? 'mb-3 flex items-center justify-between gap-4'
            : 'flex items-center justify-between gap-4'
        }
      >
        <div className="min-w-0">
          <h1 className="text-xl font-semibold">{title}</h1>

          <div className="mt-1 flex flex-wrap items-center gap-x-2 text-xs opacity-55">
            <UserRound className="h-3.5 w-3.5" />

            <span className="font-medium">
              {account?.full_name || BRAND.ownerName}
            </span>

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
            type="button"
            className="rounded-xl border bg-card p-2"
            onClick={() => setDark((value) => !value)}
            aria-label="Toggle theme"
          >
            {dark ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </button>

          <button
            type="button"
            className="rounded-xl border bg-card p-2"
            onClick={() => {
              void logout()
            }}
            aria-label="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>

      {showGlobalFilters && (
        <GlobalFilters timeMode={filterMode} />
      )}
    </header>
  )
}
