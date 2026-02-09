import { Outlet } from 'react-router-dom'
import { SkipLink } from '@/components/ui/SkipLink'
import { UserMenu } from '@/components/composite/UserMenu'
import { cn } from '@/lib/utils'
import ListAltIcon from '@mui/icons-material/ListAlt'
import { Link, useLocation } from 'react-router-dom'

export function DashboardLayout() {
  const location = useLocation()

  const navItems = [
    { path: '/sessions', label: 'Sessions', icon: <ListAltIcon /> },
  ]

  return (
    <div className="min-h-screen bg-apple-bg flex flex-col">
      <SkipLink />

      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-apple-border">
        <nav
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
          aria-label="Main navigation"
        >
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link
              to="/sessions"
              className="flex items-center gap-2 text-apple-text font-semibold text-lg"
              aria-label="PartnerScout home"
            >
              <svg
                className="w-8 h-8 text-apple-blue"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <span className="hidden sm:inline">PartnerScout</span>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    location.pathname === item.path
                      ? 'bg-apple-blue/10 text-apple-blue'
                      : 'text-apple-text-secondary hover:bg-apple-gray'
                  )}
                >
                  <span className="text-xl" aria-hidden="true">
                    {item.icon}
                  </span>
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              ))}
            </div>

            {/* User Menu */}
            <UserMenu />
          </div>
        </nav>
      </header>

      {/* Main Content - flex-1 ensures footer stays at bottom */}
      <main id="main-content" className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-apple-border mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-sm text-apple-text-tertiary text-center">
            PartnerScout AI • AI-powered partner discovery
          </p>
        </div>
      </footer>
    </div>
  )
}
