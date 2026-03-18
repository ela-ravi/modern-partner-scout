import type { ReactNode } from 'react'
import { SkipLink } from '@/components/ui/SkipLink'

interface AuthLayoutProps {
  children: ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-apple-bg to-gray-100 flex items-center justify-center p-4">
      <SkipLink />

      <main id="main-content" className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-apple-blue/10 rounded-2xl mb-4">
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
          </div>
          <h1 className="text-2xl font-bold text-apple-text">PartnerScout AI</h1>
          <p className="text-apple-text-secondary mt-1">
            AI-powered partner discovery
          </p>
        </div>

        {children}
      </main>
    </div>
  )
}
