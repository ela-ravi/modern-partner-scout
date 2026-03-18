import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import HomeIcon from '@mui/icons-material/Home'
import RefreshIcon from '@mui/icons-material/Refresh'

export default function MockErrorPage() {
  return (
    <div className="min-h-screen bg-apple-bg flex items-center justify-center p-4">
      <div className="text-center max-w-md animate-fade-in">
        <div className="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-4xl">&#9888;&#65039;</span>
        </div>

        <h1 className="text-4xl font-bold text-apple-text mb-2">500</h1>
        <h2 className="text-xl font-semibold text-apple-text mb-4">Something went wrong</h2>
        <p className="text-apple-text-secondary mb-8">
          An unexpected error occurred. Please try again or contact support if the problem persists.
        </p>

        <div className="flex items-center justify-center gap-3">
          <Button
            variant="secondary"
            leftIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
          <Link to="/mockups">
            <Button leftIcon={<HomeIcon />}>Back to Home</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
