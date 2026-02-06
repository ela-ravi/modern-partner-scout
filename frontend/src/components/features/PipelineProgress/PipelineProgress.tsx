/**
 * PipelineProgress Component
 * Shows real-time AI processing pipeline status with 4 stages
 */

import { cn } from '@/lib/utils'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ExploreIcon from '@mui/icons-material/Explore'
import VerifiedIcon from '@mui/icons-material/Verified'
import EmailIcon from '@mui/icons-material/Email'
import PsychologyIcon from '@mui/icons-material/Psychology'
import ErrorIcon from '@mui/icons-material/Error'

export interface PipelineStage {
  id: string
  name: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  description: string
  progress?: number
  stats?: Record<string, number | string>
  error?: string
}

export interface PipelineProgressProps {
  /** Pipeline stages */
  stages: PipelineStage[]
  /** Overall progress percentage (0-100) */
  overallProgress: number
  /** Total profiles being processed */
  totalProfiles?: number
  /** Profiles completed */
  completedProfiles?: number
  /** Estimated time remaining */
  estimatedTime?: string
  /** Additional class names */
  className?: string
}

const stageIcons: Record<string, typeof CheckCircleIcon> = {
  analyzer: PsychologyIcon,
  discovery: ExploreIcon,
  scoring: VerifiedIcon,
  email: EmailIcon,
}

function getStatusBadge(status: PipelineStage['status']) {
  switch (status) {
    case 'completed':
      return (
        <span className="px-2.5 py-1 bg-apple-green/10 text-apple-green text-xs font-medium rounded-full inline-flex items-center gap-1">
          <CheckCircleIcon className="w-3 h-3" />
          Complete
        </span>
      )
    case 'active':
      return (
        <span className="px-2.5 py-1 bg-apple-blue/10 text-apple-blue text-xs font-medium rounded-full animate-pulse">
          Running
        </span>
      )
    case 'failed':
      return (
        <span className="px-2.5 py-1 bg-apple-red/10 text-apple-red text-xs font-medium rounded-full inline-flex items-center gap-1">
          <ErrorIcon className="w-3 h-3" />
          Failed
        </span>
      )
    default:
      return (
        <span className="px-2.5 py-1 bg-gray-100 text-gray-500 text-xs font-medium rounded-full">
          Pending
        </span>
      )
  }
}

function StageCard({ stage }: { stage: PipelineStage }) {
  const Icon = stageIcons[stage.id] || PsychologyIcon
  const isActive = stage.status === 'active'
  const isCompleted = stage.status === 'completed'
  const isFailed = stage.status === 'failed'
  const isPending = stage.status === 'pending'

  return (
    <div
      className={cn(
        'rounded-2xl border p-5 transition-all',
        isActive && 'border-apple-blue shadow-[0_0_0_3px_rgba(0,113,227,0.1)]',
        isCompleted && 'border-apple-green',
        isFailed && 'border-apple-red',
        isPending && 'border-gray-200 opacity-60'
      )}
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div
          className={cn(
            'w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0',
            isCompleted && 'bg-apple-green/10',
            isActive && 'bg-apple-blue/10',
            isFailed && 'bg-apple-red/10',
            isPending && 'bg-gray-100'
          )}
        >
          {isCompleted ? (
            <CheckCircleIcon className="text-apple-green text-xl" />
          ) : (
            <Icon
              className={cn(
                'text-xl',
                isActive && 'text-apple-blue animate-spin',
                isFailed && 'text-apple-red',
                isPending && 'text-gray-400'
              )}
              style={isActive ? { animation: 'spin 2s linear infinite' } : undefined}
            />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3
              className={cn(
                'font-semibold',
                isPending && 'text-gray-500'
              )}
            >
              {stage.name}
            </h3>
            {getStatusBadge(stage.status)}
          </div>

          <p
            className={cn(
              'text-sm mb-3',
              isPending ? 'text-gray-400' : 'text-apple-text-secondary'
            )}
          >
            {isFailed && stage.error ? stage.error : stage.description}
          </p>

          {/* Progress bar for active stages */}
          {isActive && typeof stage.progress === 'number' && (
            <div className="mb-3">
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-apple-blue to-blue-400 rounded-full transition-all duration-500"
                  style={{ width: `${stage.progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Stats */}
          {stage.stats && Object.keys(stage.stats).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {Object.entries(stage.stats).map(([key, value]) => (
                <span
                  key={key}
                  className="px-2.5 py-1 bg-gray-100 text-apple-text-secondary text-xs rounded-lg"
                >
                  {value} {key}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Connector({ from, to }: { from: PipelineStage['status']; to: PipelineStage['status'] }) {
  const fromColor = from === 'completed' ? 'from-apple-green' : from === 'active' ? 'from-apple-blue' : 'from-gray-200'
  const toColor = to === 'completed' ? 'to-apple-green' : to === 'active' ? 'to-apple-blue' : 'to-gray-200'

  return (
    <div className="flex justify-center py-1">
      <div className={cn('w-0.5 h-6 bg-gradient-to-b', fromColor, toColor)} />
    </div>
  )
}

export function PipelineProgress({
  stages,
  overallProgress,
  totalProfiles,
  completedProfiles,
  estimatedTime,
  className,
}: PipelineProgressProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Overall Progress Card */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-6 mb-5">
          <div>
            <p className="text-apple-text-secondary text-sm mb-1">Overall Progress</p>
            {totalProfiles && completedProfiles !== undefined && (
              <p className="text-3xl font-semibold tracking-tight">
                {completedProfiles} of {totalProfiles} profiles
              </p>
            )}
          </div>
        </div>

        {/* Progress Bar with ARIA */}
        <div
          role="progressbar"
          aria-label="Overall progress"
          aria-valuenow={overallProgress}
          aria-valuemin={0}
          aria-valuemax={100}
          className="h-2 bg-gray-100 rounded-full overflow-hidden"
        >
          <div
            className="h-full bg-gradient-to-r from-apple-blue to-blue-400 rounded-full transition-all duration-500"
            style={{ width: `${overallProgress}%` }}
          />
        </div>

        {estimatedTime && (
          <p className="text-apple-text-tertiary text-sm mt-3">
            ~{estimatedTime} remaining
          </p>
        )}
      </div>

      {/* Pipeline Stages */}
      <div>
        <h2 className="font-semibold text-lg mb-4">Agent Pipeline</h2>
        <div className="space-y-0">
          {stages.map((stage, index) => (
            <div key={stage.id}>
              <StageCard stage={stage} />
              {index < stages.length - 1 && (
                <Connector from={stage.status} to={stages[index + 1].status} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
