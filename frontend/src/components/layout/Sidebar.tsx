import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  Filter, 
  BrainCircuit, 
  FlaskConical, 
  TrendingUp 
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/cohorts', label: 'Cohorts', icon: Users },
  { path: '/funnel', label: 'Funnel', icon: Filter },
  { path: '/churn', label: 'Churn ML', icon: BrainCircuit },
  { path: '/experiments', label: 'A/B Tests', icon: FlaskConical },
]

export function Sidebar() {
  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="font-semibold text-sm tracking-tight">Retention</h1>
            <p className="text-xs text-muted-foreground">Analytics Platform</p>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )
            }
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-border">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-xs font-medium text-muted-foreground mb-1">System Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-emerald-500">Operational</span>
          </div>
        </div>
      </div>
    </aside>
  )
}