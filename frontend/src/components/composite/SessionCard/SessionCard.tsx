import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Badge, type BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'
import DeleteIcon from '@mui/icons-material/Delete'
import PeopleIcon from '@mui/icons-material/People'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import type { Job, JobStatus } from '@/types/api/job'
import { format } from 'date-fns'

export interface SessionCardProps {
  /** Job data */
  job: Job
  /** Called when delete is clicked */
  onDelete?: (job: Job) => void
  /** Additional class names */
  className?: string
}

// Map JobStatus to BadgeVariant
function getStatusVariant(status: JobStatus): BadgeVariant {
  switch (status) {
    case 'pending':
      return 'new'
    case 'analyzing':
    case 'discovering':
    case 'scoring':
      return 'processing'
    case 'completed':
      return 'done'
    case 'failed':
      return 'failed'
    case 'cancelled':
      return 'cancelled'
    default:
      return 'default'
  }
}

function getStatusLabel(status: JobStatus): string {
  switch (status) {
    case 'pending':
      return 'Pending'
    case 'analyzing':
      return 'Analyzing'
    case 'discovering':
      return 'Discovering'
    case 'scoring':
      return 'Scoring'
    case 'completed':
      return 'Completed'
    case 'failed':
      return 'Failed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return status
  }
}

export function SessionCard({ job, onDelete, className }: SessionCardProps) {
  const formattedDate = format(new Date(job.created_at), 'MMM d, yyyy')
  const isInProgress = ['pending', 'analyzing', 'discovering', 'scoring'].includes(job.status)
  const linkTarget = isInProgress ? `/jobs/${job.id}/processing` : `/jobs/${job.id}`

  return (
    <Card
      hoverable
      className={cn('relative group', className)}
    >
      <Link
        to={linkTarget}
        className="block cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2 rounded-lg -m-6 p-6"
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <h3 className="font-semibold text-apple-text text-lg line-clamp-2 pr-4">
            {job.name}
          </h3>
          <Badge variant={getStatusVariant(job.status)}>
            {getStatusLabel(job.status)}
          </Badge>
        </div>

        {/* Stats */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2 text-apple-text-secondary">
            <PeopleIcon className="w-4 h-4" />
            <span>Discovered: </span>
            <span className="font-medium text-apple-text">{job.profiles_discovered}</span>
          </div>

          <div className="flex items-center gap-2 text-apple-text-secondary">
            <CheckCircleIcon className="w-4 h-4" />
            <span>Scored: </span>
            <span className="font-medium text-apple-text">{job.profiles_scored}</span>
          </div>

          <div className="flex items-center gap-2 text-apple-text-secondary">
            <CalendarTodayIcon className="w-4 h-4" />
            <span>Created: </span>
            <span className="font-medium text-apple-text">{formattedDate}</span>
          </div>
        </div>
      </Link>

      {/* Delete button - visible on hover */}
      {onDelete && (
        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              onDelete(job)
            }}
            aria-label={`Delete ${job.name}`}
            className="text-apple-text-tertiary hover:text-apple-red hover:bg-red-50"
          >
            <DeleteIcon className="w-4 h-4" />
          </Button>
        </div>
      )}
    </Card>
  )
}
