import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useStartDemo } from '@/hooks/jobs'
import { useToast } from '@/components/ui/Toast'
import AddIcon from '@mui/icons-material/Add'
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline'
import SearchIcon from '@mui/icons-material/Search'

export interface EmptyStateProps {
  /** Custom title */
  title?: string
  /** Custom description */
  description?: string
  /** Hide the demo button */
  hideDemo?: boolean
}

export function EmptyState({
  title = 'No discovery sessions yet',
  description = 'Start finding the perfect partners for your brand by creating a new discovery session or watch a demo to see how it works.',
  hideDemo = false,
}: EmptyStateProps) {
  const navigate = useNavigate()
  const toast = useToast()
  const startDemo = useStartDemo()

  const handleStartDemo = async () => {
    try {
      const result = await startDemo.mutateAsync()
      toast.success('Demo started! Redirecting to dashboard...')
      navigate(`/jobs/${result.job_id}`)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to start demo')
    }
  }

  return (
    <Card className="text-center py-16 px-8 max-w-lg mx-auto">
      {/* Illustration */}
      <div className="w-24 h-24 bg-apple-blue/10 rounded-full flex items-center justify-center mx-auto mb-6">
        <SearchIcon className="w-12 h-12 text-apple-blue" />
      </div>

      {/* Content */}
      <h2 className="text-2xl font-bold text-apple-text mb-3">{title}</h2>
      <p className="text-apple-text-secondary mb-8 max-w-md mx-auto">{description}</p>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Button
          onClick={() => navigate('/new-session')}
          leftIcon={<AddIcon />}
          size="lg"
        >
          Start New Discovery
        </Button>

        {!hideDemo && (
          <Button
            variant="secondary"
            onClick={handleStartDemo}
            leftIcon={<PlayCircleOutlineIcon />}
            loading={startDemo.isPending}
            size="lg"
          >
            Watch Demo
          </Button>
        )}
      </div>

      {/* Help text */}
      <p className="text-sm text-apple-text-tertiary mt-8">
        The demo will create a sample discovery session with example profiles.
      </p>
    </Card>
  )
}
