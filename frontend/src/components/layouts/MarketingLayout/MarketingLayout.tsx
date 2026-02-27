import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { SkipLink } from '@/components/ui/SkipLink'
import { Navbar } from './Navbar'
import { Footer } from './Footer'

export function MarketingLayout() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [pathname])

  return (
    <div className="min-h-screen bg-apple-bg">
      <SkipLink />
      <Navbar />
      <main id="main-content">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
