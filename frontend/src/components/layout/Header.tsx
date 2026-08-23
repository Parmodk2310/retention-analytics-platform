import { Bell, Search, User } from 'lucide-react'

export function Header() {
  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur flex items-center justify-between px-6">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search metrics, users, experiments..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-muted text-sm border border-transparent focus:border-primary focus:outline-none transition-colors placeholder:text-muted-foreground"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative p-2 rounded-lg hover:bg-accent transition-colors">
          <Bell className="w-5 h-5 text-muted-foreground" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-destructive rounded-full" />
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium">Data Scientist</p>
            <p className="text-xs text-muted-foreground">Product Team</p>
          </div>
        </div>
      </div>
    </header>
  )
}