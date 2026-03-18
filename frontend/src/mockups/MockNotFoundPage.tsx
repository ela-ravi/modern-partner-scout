import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import HomeIcon from '@mui/icons-material/Home'

export default function MockNotFoundPage() {
  return (
    <div className="min-h-screen bg-apple-bg flex items-center justify-center p-4">
      <div className="text-center max-w-md animate-fade-in">
        <div className="w-24 h-24 bg-apple-gray rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-4xl">&#128269;</span>
        </div>

        <h1 className="text-4xl font-bold text-apple-text mb-2">404</h1>
        <h2 className="text-xl font-semibold text-apple-text mb-4">Page not found</h2>
        <p className="text-apple-text-secondary mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>

        <Link to="/mockups">
          <Button leftIcon={<HomeIcon />}>Back to Gallery</Button>
        </Link>
      </div>
    </div>
  )
}
