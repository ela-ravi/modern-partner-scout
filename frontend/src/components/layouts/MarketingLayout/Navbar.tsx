import { useState, useEffect, useCallback } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/contexts/AuthContext'
import MenuIcon from '@mui/icons-material/Menu'
import CloseIcon from '@mui/icons-material/Close'

const navLinks = [
  { path: '/#features', label: 'Features' },
  { path: '/#pricing', label: 'Pricing' },
  { path: '/docs', label: 'Docs' },
  { path: '/contact', label: 'Contact' },
]

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const closeMobile = useCallback(() => setMobileOpen(false), [])

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled
          ? 'glass border-b border-apple-border shadow-sm'
          : 'bg-transparent'
      )}
    >
      <nav
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
        aria-label="Main navigation"
      >
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2 text-apple-text font-semibold text-lg"
            aria-label="PartnerScout home"
            onClick={closeMobile}
          >
            <svg
              className="w-8 h-8 text-brand-primary"
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
            <span>PartnerScout</span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={cn(
                  'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                  location.pathname === link.path
                    ? 'text-brand-primary'
                    : 'text-apple-text-secondary hover:text-apple-text hover:bg-apple-gray'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Desktop CTAs */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <Button variant="primary" size="sm" asChild>
                <Link to="/sessions">Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/login">Log in</Link>
                </Button>
                <Button variant="primary" size="sm" asChild>
                  <Link to="/login">Get Started</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-xl text-apple-text-secondary hover:bg-apple-gray transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-expanded={mobileOpen}
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          >
            {mobileOpen ? (
              <CloseIcon className="w-6 h-6" />
            ) : (
              <MenuIcon className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden pb-4 border-t border-apple-border mt-2 pt-4">
            <div className="flex flex-col gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={closeMobile}
                  className={cn(
                    'px-4 py-3 rounded-xl text-sm font-medium transition-colors',
                    location.pathname === link.path
                      ? 'bg-brand-primary/10 text-brand-primary'
                      : 'text-apple-text-secondary hover:bg-apple-gray'
                  )}
                >
                  {link.label}
                </Link>
              ))}
              <div className="flex flex-col gap-2 mt-3 px-4">
                {isAuthenticated ? (
                  <Button variant="primary" size="md" asChild>
                    <Link to="/sessions" onClick={closeMobile}>Dashboard</Link>
                  </Button>
                ) : (
                  <>
                    <Button variant="secondary" size="md" asChild>
                      <Link to="/login" onClick={closeMobile}>Log in</Link>
                    </Button>
                    <Button variant="primary" size="md" asChild>
                      <Link to="/login" onClick={closeMobile}>Get Started</Link>
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}
