/**
 * Generic Error Page (500)
 * Displayed when an unexpected server error occurs
 */

import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import HomeIcon from '@mui/icons-material/Home'
import RefreshIcon from '@mui/icons-material/Refresh'

interface ErrorPageProps {
  /** Custom title */
  title?: string
  /** Custom message */
  message?: string
  /** Whether to show refresh button */
  showRefresh?: boolean
}

export default function ErrorPage({
  title = 'Something went wrong',
  message = 'We encountered an unexpected error. Please try again later.',
  showRefresh = true,
}: ErrorPageProps) {
  const handleRefresh = () => {
    window.location.reload()
  }

  return (
    <div className="min-h-screen bg-apple-bg flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <div className="w-24 h-24 bg-apple-red/10 rounded-full flex items-center justify-center mx-auto mb-6">
          <ErrorOutlineIcon className="text-apple-red w-12 h-12" />
        </div>

        <h1 className="text-4xl font-bold text-apple-text mb-2">500</h1>
        <h2 className="text-xl font-semibold text-apple-text mb-4">{title}</h2>
        <p className="text-apple-text-secondary mb-8">{message}</p>

        <div className="flex justify-center gap-3">
          <Link to="/dashboard">
            <Button variant="secondary" leftIcon={<HomeIcon />}>
              Go Home
            </Button>
          </Link>
          {showRefresh && (
            <Button onClick={handleRefresh} leftIcon={<RefreshIcon />}>
              Refresh
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
