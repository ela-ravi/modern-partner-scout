/**
 * ProcessingPage
 * Shows real-time AI pipeline processing status
 */

import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { PipelineProgress, type PipelineStage } from '@/components/features/PipelineProgress'
import { ActivityLog, type LogEntry } from '@/components/composite/ActivityLog'
import { useJob, useCancelJob, useStartJob, useRetryJob } from '@/hooks/jobs'
import { useJobAnalytics } from '@/hooks/profiles'
import { useRealtimeJobStatus } from '@/hooks/realtime'
import { useToast } from '@/components/ui/Toast'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import StopCircleIcon from '@mui/icons-material/StopCircle'
import DashboardIcon from '@mui/icons-material/Dashboard'
import RefreshIcon from '@mui/icons-material/Refresh'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import type { JobStatus } from '@/types/api/job'

// Map job status to pipeline stages
function getStagesFromJobStatus(status: JobStatus, analytics?: {
  total_discovered?: number
  total_scored?: number
  emails_found?: number
}): PipelineStage[] {
  const stages: PipelineStage[] = [
    {
      id: 'analyzer',
      name: 'Brand Analyzer',
      status: 'pending',
      description: 'Extracting brand DNA from reference profiles',
    },
    {
      id: 'discovery',
      name: 'Discovery Engine',
      status: 'pending',
      description: 'Scanning Instagram for matching profiles',
      stats: analytics?.total_discovered ? { discovered: analytics.total_discovered } : undefined,
    },
    {
      id: 'scoring',
      name: 'Scoring Agent',
      status: 'pending',
      description: 'Analyzing profiles against brand DNA',
      stats: analytics?.total_scored ? { scored: analytics.total_scored } : undefined,
    },
    {
      id: 'email',
      name: 'Email Extractor',
      status: 'pending',
      description: 'Extracting contact emails from scored profiles',
      stats: analytics?.emails_found ? { emails: analytics.emails_found } : undefined,
    },
  ]

  // Update stages based on job status
  switch (status) {
    case 'completed':
      stages.forEach((s) => (s.status = 'completed'))
      break
    case 'analyzing':
      stages[0].status = 'active'
      stages[0].progress = 50
      break
    case 'discovering':
      stages[0].status = 'completed'
      stages[1].status = 'active'
      stages[1].progress = 60
      break
    case 'scoring':
      stages[0].status = 'completed'
      stages[1].status = 'completed'
      stages[2].status = 'active'
      stages[2].progress = 40
      stages[3].status = 'active'
      stages[3].progress = 20
      break
    case 'failed':
    case 'cancelled':
      // Determine which stages completed before failure/cancellation based on analytics
      // If we have discovered profiles, Brand Analyzer and Discovery completed
      if (analytics?.total_discovered && analytics.total_discovered > 0) {
        stages[0].status = 'completed' // Brand Analyzer
        stages[1].status = 'completed' // Discovery Engine
        
        // If we have scored profiles, Scoring was in progress
        if (analytics?.total_scored && analytics.total_scored > 0) {
          stages[2].status = status === 'failed' ? 'failed' : 'cancelled'
          stages[2].error = status === 'failed' ? 'Processing failed' : 'Cancelled by user'
          stages[3].status = status === 'failed' ? 'failed' : 'cancelled'
        } else {
          // Scoring hadn't started yet
          stages[2].status = status === 'failed' ? 'failed' : 'cancelled'
          stages[2].error = status === 'failed' ? 'Processing failed' : 'Cancelled by user'
        }
      } else {
        // Failed/cancelled during Brand Analysis or Discovery
        stages[0].status = status === 'failed' ? 'failed' : 'cancelled'
        stages[0].error = status === 'failed' ? 'Processing failed' : 'Cancelled by user'
      }
      break
  }

  return stages
}

function getOverallProgress(status: JobStatus, analytics?: {
  total_discovered?: number
  total_scored?: number
  profiles_target?: number
}): number {
  if (status === 'completed') return 100
  if (status === 'pending') return 0
  if (status === 'analyzing') return 15
  if (status === 'discovering') return 35
  if (status === 'scoring') {
    const target = analytics?.profiles_target || 50
    const scored = analytics?.total_scored || 0
    return Math.min(50 + (scored / target) * 50, 99)
  }
  return 0
}

export default function ProcessingPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const cancelJob = useCancelJob()
  const startJob = useStartJob()
  const retryJob = useRetryJob()

  const [showCancelModal, setShowCancelModal] = useState(false)
  const [activityLog, setActivityLog] = useState<LogEntry[]>([])

  // Determine if job is in a running state (for real-time subscription)
  // We compute this before useJob to enable polling
  const [isRunning, setIsRunning] = useState(true) // Initially assume running

  // Fetch job details with polling fallback when running
  const { data: job, isLoading: jobLoading } = useJob(jobId, { 
    enablePolling: isRunning,
    pollingInterval: 3000, // Poll every 3 seconds
  })
  const { data: analytics } = useJobAnalytics(jobId)

  // Subscribe to real-time job status updates
  useRealtimeJobStatus({
    jobId: jobId!,
    enabled: isRunning && !!jobId,
    onStatusChange: (newStatus, previousStatus) => {
      // Add log entry when status changes
      const now = new Date()
      const timestamp = now.toTimeString().slice(0, 8)
      const statusMessages: Record<string, string> = {
        analyzing: 'Brand Analyzer started',
        discovering: 'Discovery Engine started',
        scoring: 'Scoring Agent started',
        completed: 'All agents completed successfully!',
        failed: 'Pipeline encountered an error',
        cancelled: 'Discovery was cancelled',
      }
      
      const message = statusMessages[newStatus] || `Status changed to ${newStatus}`
      const type = newStatus === 'completed' ? 'success' : 
                   newStatus === 'failed' ? 'error' : 
                   newStatus === 'cancelled' ? 'warning' : 'info'
      
      setActivityLog((prev) => [...prev.slice(-49), {
        id: `status-${Date.now()}`,
        timestamp,
        type,
        message,
      }])
      
      // Show toast for important status changes
      if (newStatus === 'completed') {
        toast.success('Discovery completed successfully!')
      } else if (newStatus === 'failed') {
        toast.error('Discovery failed. Check the activity log for details.')
      }
    },
  })

  // Update isRunning state when job data changes
  // Note: 'pending' is NOT considered running - it means not yet started
  useEffect(() => {
    if (job) {
      const running = ['analyzing', 'discovering', 'scoring'].includes(job.status)
      setIsRunning(running)
    }
  }, [job?.status])

  // Populate initial activity log based on current job status
  // This ensures we show past events even if page was opened after they happened
  useEffect(() => {
    if (!job || activityLog.length > 0) return // Only populate once, on initial load

    const initialEntries: LogEntry[] = []
    const timestamp = new Date(job.created_at).toTimeString().slice(0, 8)

    // Add entries for completed stages based on current status
    const statusOrder = ['pending', 'analyzing', 'discovering', 'scoring', 'completed', 'failed', 'cancelled']
    const currentIndex = statusOrder.indexOf(job.status)

    if (currentIndex >= 1) {
      initialEntries.push({
        id: 'init-analyzing',
        timestamp,
        type: 'info',
        message: 'Brand Analyzer started',
      })
    }

    if (currentIndex >= 2) {
      initialEntries.push({
        id: 'init-analyzing-done',
        timestamp,
        type: 'success',
        message: 'Brand DNA extracted successfully',
      })
      initialEntries.push({
        id: 'init-discovering',
        timestamp,
        type: 'info',
        message: 'Discovery Engine started',
      })
    }

    if (currentIndex >= 3) {
      initialEntries.push({
        id: 'init-discovering-done',
        timestamp,
        type: 'success',
        message: `Discovered ${job.profiles_discovered || 0} profiles`,
      })
      initialEntries.push({
        id: 'init-scoring',
        timestamp,
        type: 'info',
        message: 'Scoring Agent started',
      })
    }

    if (job.status === 'completed') {
      initialEntries.push({
        id: 'init-completed',
        timestamp: new Date().toTimeString().slice(0, 8),
        type: 'success',
        message: 'All agents completed successfully!',
      })
    } else if (job.status === 'failed') {
      initialEntries.push({
        id: 'init-failed',
        timestamp: new Date().toTimeString().slice(0, 8),
        type: 'error',
        message: job.error_message || 'Pipeline encountered an error',
      })
    } else if (job.status === 'cancelled') {
      initialEntries.push({
        id: 'init-cancelled',
        timestamp: new Date().toTimeString().slice(0, 8),
        type: 'warning',
        message: 'Discovery was cancelled',
      })
    }

    if (initialEntries.length > 0) {
      setActivityLog(initialEntries)
    }
  }, [job, activityLog.length])


  const handleCancel = async () => {
    if (!jobId) return
    try {
      await cancelJob.mutateAsync(jobId)
      toast.success('Job cancelled successfully')
      setShowCancelModal(false)
    } catch {
      toast.error('Failed to cancel job')
    }
  }

  const handleStartJob = async () => {
    if (!jobId) return
    try {
      await startJob.mutateAsync(jobId)
      toast.success('Discovery started!')
    } catch {
      toast.error('Failed to start discovery')
    }
  }

  const handleRetryJob = async () => {
    if (!jobId) return
    try {
      // First reset the job to pending
      await retryJob.mutateAsync(jobId)
      // Then start it
      await startJob.mutateAsync(jobId)
      toast.success('Discovery restarted!')
    } catch {
      toast.error('Failed to restart discovery')
    }
  }

  const handleViewDashboard = () => {
    navigate(`/jobs/${jobId}`)
  }

  if (jobLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 w-64 bg-gray-200 rounded" />
        <div className="h-40 bg-gray-200 rounded-2xl" />
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-2xl" />
            ))}
          </div>
          <div className="h-[500px] bg-gray-200 rounded-2xl" />
        </div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <p className="text-apple-text-secondary">Job not found</p>
        <Button variant="secondary" onClick={() => navigate('/sessions')} className="mt-4">
          Back to Sessions
        </Button>
      </div>
    )
  }

  const stages = getStagesFromJobStatus(job.status, analytics)
  const progress = getOverallProgress(job.status, analytics)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/sessions')}
            aria-label="Back to sessions"
          >
            <ArrowBackIcon className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-apple-text">Processing Pipeline</h1>
            <p className="text-sm text-apple-text-secondary mt-0.5">
              {job.name} • Started {new Date(job.created_at).toLocaleTimeString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Pending indicator */}
          {job.status === 'pending' && (
            <Badge variant="new">Ready to Start</Badge>
          )}

          {/* Cancelled indicator */}
          {job.status === 'cancelled' && (
            <Badge variant="cancelled">Cancelled</Badge>
          )}

          {/* Failed indicator */}
          {job.status === 'failed' && (
            <Badge variant="failed">Failed</Badge>
          )}

          {/* Completed indicator */}
          {job.status === 'completed' && (
            <Badge variant="done">Completed</Badge>
          )}

          {/* Running indicator */}
          {isRunning && (
            <Badge variant="processing" className="gap-2">
              <span className="w-2 h-2 bg-apple-blue rounded-full animate-pulse" />
              Discovery Running
            </Badge>
          )}

          {/* Cancel button */}
          {isRunning && (
            <Button
              variant="secondary"
              leftIcon={<StopCircleIcon />}
              onClick={() => setShowCancelModal(true)}
            >
              Stop
            </Button>
          )}

          {/* Restart button (shown when failed or cancelled) */}
          {(job.status === 'failed' || job.status === 'cancelled') && (
            <Button
              variant="secondary"
              leftIcon={<RefreshIcon />}
              onClick={handleRetryJob}
              loading={retryJob.isPending || startJob.isPending}
              className="text-apple-orange hover:text-apple-orange"
            >
              Restart
            </Button>
          )}

          {/* Start button (shown when pending) */}
          {job.status === 'pending' && (
            <Button
              variant="primary"
              leftIcon={<PlayArrowIcon />}
              onClick={handleStartJob}
              loading={startJob.isPending}
            >
              Start Discovery
            </Button>
          )}

          {/* View Profiles button */}
          <Button
            variant="primary"
            leftIcon={<DashboardIcon />}
            onClick={handleViewDashboard}
          >
            View Profiles
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Pipeline Progress */}
        <div className="lg:col-span-2">
          <PipelineProgress
            stages={stages}
            overallProgress={progress}
            totalProfiles={50}
            completedProfiles={job.profiles_scored}
            estimatedTime={isRunning ? '2 minutes' : undefined}
          />
        </div>

        {/* Activity Log */}
        <div className="lg:col-span-1">
          <ActivityLog entries={activityLog} maxHeight="500px" />
        </div>
      </div>

      {/* Cancel Confirmation Modal */}
      <Modal
        open={showCancelModal}
        onOpenChange={(open) => setShowCancelModal(open)}
        title="Cancel Discovery"
      >
        <div className="space-y-4">
          <p className="text-apple-text-secondary">
            Are you sure you want to cancel this discovery? This action cannot be undone.
          </p>
          <p className="text-apple-text-secondary">
            Progress so far: {job.profiles_discovered} profiles discovered, {job.profiles_scored} scored.
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowCancelModal(false)}>
              Keep Running
            </Button>
            <Button
              variant="danger"
              onClick={handleCancel}
              loading={cancelJob.isPending}
            >
              Cancel Job
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
