import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import ListAltIcon from '@mui/icons-material/ListAlt'
import AddIcon from '@mui/icons-material/Add'

interface MockDashboardLayoutProps {
  children: ReactNode
  activePath?: string
}

const navItems = [
  { path: '/mockups/sessions', label: 'Sessions', icon: <ListAltIcon /> },
  { path: '/mockups/discovery-config', label: 'New Session', icon: <AddIcon /> },
]

export function MockDashboardLayout({ children, activePath }: MockDashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-apple-bg">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-apple-border">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/mockups" className="flex items-center gap-2 text-apple-text font-semibold text-lg" aria-label="PartnerScout home">
              <svg className="w-8 h-8 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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
                    activePath === item.path
                      ? 'bg-apple-blue/10 text-apple-blue'
                      : 'text-apple-text-secondary hover:bg-apple-gray'
                  )}
                >
                  <span className="text-xl" aria-hidden="true">{item.icon}</span>
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              ))}
            </div>

            {/* Static User Menu */}
            <div className="flex items-center gap-3">
              <Badge variant="info" className="text-xs">MOCKUP</Badge>
              <div className="flex items-center gap-2">
                <Avatar name="Demo User" alt="Demo User avatar" size="sm" />
                <span className="hidden sm:inline text-sm text-apple-text-secondary">Demo User</span>
              </div>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-apple-border mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-sm text-apple-text-tertiary text-center">
            PartnerScout AI • UI Design Mockup
          </p>
        </div>
      </footer>
    </div>
  )
}
