import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

const pages = [
  { path: 'login', name: 'Login Page', description: 'Authentication with email/password, sign up toggle', complexity: 'Simple' },
  { path: 'sessions', name: 'Sessions Page', description: 'Discovery session list with cards, delete modal, empty state', complexity: 'Medium' },
  { path: 'discovery-config', name: 'Discovery Config', description: 'Two-step form: configure campaign settings, then review & launch', complexity: 'Complex' },
  { path: 'processing', name: 'Processing Page', description: 'Real-time pipeline visualization with 4 stages and activity log', complexity: 'Medium' },
  { path: 'dashboard', name: 'Dashboard Page', description: 'Full results dashboard with tabs, sort, profile cards, detail modal, email composer', complexity: 'Complex' },
  { path: 'error', name: 'Error Page', description: 'Generic 500 error display with retry and home buttons', complexity: 'Simple' },
  { path: 'not-found', name: 'Not Found Page', description: '404 page with home navigation', complexity: 'Simple' },
]

function getComplexityColor(c: string) {
  if (c === 'Complex') return 'warning' as const
  if (c === 'Medium') return 'processing' as const
  return 'done' as const
}

export default function MockGallery() {
  return (
    <div className="min-h-screen bg-apple-bg">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-apple-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <svg className="w-8 h-8 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="font-semibold text-lg text-apple-text">PartnerScout</span>
            </div>
            <Badge variant="info">UI Mockups</Badge>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-apple-text">UI Design Mockups</h1>
          <p className="text-apple-text-secondary mt-1">
            All 7 pages with hardcoded data — visual blueprint for the hackathon rebuild
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {pages.map((page, i) => (
            <Link key={page.path} to={`/mockups/${page.path}`} className="block">
              <Card
                hoverable
                className="h-full animate-slide-up"
                style={{ animationDelay: `${i * 60}ms`, animationFillMode: 'backwards' }}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-apple-text text-lg">{page.name}</h3>
                  <Badge variant={getComplexityColor(page.complexity)}>{page.complexity}</Badge>
                </div>
                <p className="text-sm text-apple-text-secondary">{page.description}</p>
                <div className="mt-4 text-sm text-apple-blue font-medium">
                  View mockup →
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}
