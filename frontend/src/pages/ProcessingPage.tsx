/**
 * ProcessingPage
 * Shows real-time AI pipeline processing status
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { PipelineProgress, type PipelineStage } from '@/components/features/PipelineProgress'
import { ActivityLog, type LogEntry } from '@/components/composite/ActivityLog'
import { useJob, useCancelJob } from '@/hooks/jobs'
import { jobsService } from '@/services/jobs'
import { useJobAnalytics } from '@/hooks/profiles'
import { useRealtime } from '@/hooks/realtime'
import { useToast } from '@/components/ui/Toast'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import StopCircleIcon from '@mui/icons-material/StopCircle'
import DashboardIcon from '@mui/icons-material/Dashboard'
import RefreshIcon from '@mui/icons-material/Refresh'
import type { JobStatus } from '@/types/api/job'
import type { JobAnalytics } from '@/types/api/profile'

const TERMINAL_STATUSES: JobStatus[] = ['completed', 'failed', 'cancelled']

// Map job status to pipeline stages
function getStagesFromJobStatus(status: JobStatus, analytics?: JobAnalytics): PipelineStage[] {
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
      stats: analytics?.total_profiles ? { discovered: analytics.total_profiles } : undefined,
    },
    {
      id: 'scoring',
      name: 'Scoring Agent',
      status: 'pending',
      description: 'Analyzing profiles against brand DNA',
      stats: analytics?.done_profiles ? { scored: analytics.done_profiles } : undefined,
    },
    {
      id: 'email',
      name: 'Email Extractor',
      status: 'pending',
      description: 'Extracting contact emails from scored profiles',
      stats: analytics?.profiles_with_email ? { emails: analytics.profiles_with_email } : undefined,
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
    case 'failed': {
      const activeIndex = stages.findIndex((s) => s.status === 'active')
      if (activeIndex >= 0) {
        stages[activeIndex].status = 'failed'
        stages[activeIndex].error = 'Processing failed'
      } else {
        stages[0].status = 'failed'
        stages[0].error = 'Processing failed'
      }
      break
    }
    case 'cancelled':
      stages.forEach((s) => {
        if (s.status === 'active') s.status = 'pending'
      })
      break
  }

  return stages
}

function getOverallProgress(status: JobStatus): number {
  if (status === 'completed') return 100
  if (status === 'pending') return 0
  if (status === 'analyzing') return 15
  if (status === 'discovering') return 40
  if (status === 'scoring') return 70
  return 0
}

export default function ProcessingPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const cancelJob = useCancelJob()

  const [showCancelModal, setShowCancelModal] = useState(false)
  const [activityLog, setActivityLog] = useState<LogEntry[]>([])
  const hasAutoNavigated = useRef(false)

  // Fetch job details with polling every 3s while running
  const { data: job, isLoading: jobLoading } = useJob(jobId, {
    refetchInterval: 3000,
  })
  const { data: analytics } = useJobAnalytics(jobId, { refetchInterval: 3000 })

  const isRunning = !!job && !TERMINAL_STATUSES.includes(job.status)

  // Add a log entry helper
  const addLogEntry = useCallback((type: LogEntry['type'], message: string, score?: number) => {
    const now = new Date()
    const entry: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      timestamp: now.toTimeString().slice(0, 8),
      type,
      message,
      score,
    }
    setActivityLog((prev) => [...prev.slice(-49), entry])
  }, [])

  // Subscribe to job status changes via Supabase Realtime
  useRealtime<{ status: string; updated_at: string; error_message?: string }>({
    table: 'discovery_jobs',
    jobId: jobId,
    enabled: !!jobId && isRunning,
    onUpdate: (record) => {
      const statusLabels: Record<string, string> = {
        analyzing: 'Brand analysis started...',
        discovering: 'Profile discovery started...',
        scoring: 'Profile scoring started...',
        completed: 'Pipeline completed successfully!',
        failed: `Pipeline failed: ${record.error_message || 'Unknown error'}`,
        cancelled: 'Pipeline cancelled.',
      }
      const label = statusLabels[record.status] || `Status: ${record.status}`
      const type = record.status === 'failed' ? 'error' : record.status === 'completed' ? 'success' : 'info'
      addLogEntry(type, label)
    },
  })

  // Subscribe to new profile discoveries
  useRealtime<{ id: string; username: string; followers_count: number }>({
    table: 'discovered_profiles',
    jobId: jobId,
    enabled: !!jobId && isRunning,
    onInsert: (profile) => {
      const followers = profile.followers_count
        ? ` (${(profile.followers_count / 1000).toFixed(1)}K followers)`
        : ''
      addLogEntry('success', `Discovered @${profile.username}${followers}`)
    },
  })

  // Subscribe to profile score updates
  useRealtime<{ profile_id: string; final_score: number }>({
    table: 'profile_scores',
    enabled: !!jobId && isRunning,
    onInsert: (score) => {
      addLogEntry('success', `Profile scored`, score.final_score)
    },
  })

  // Derive initial log entry from job data (computed during render, auto-memoized by compiler)
  const initialEntry: LogEntry | null = job
    ? {
        id: 'init',
        timestamp: new Date(job.created_at).toTimeString().slice(0, 8),
        type: 'info',
        message: `Pipeline started for "${job.name}"`,
      }
    : null

  const displayLog = initialEntry
    ? [initialEntry, ...activityLog]
    : activityLog

  // Auto-navigate to dashboard when completed
  useEffect(() => {
    if (job?.status === 'completed' && !hasAutoNavigated.current) {
      hasAutoNavigated.current = true
      toast.success('Discovery completed! Redirecting to results...')
      const timer = setTimeout(() => navigate(`/jobs/${jobId}`), 3000)
      return () => clearTimeout(timer)
    }
  }, [job?.status, jobId, navigate, toast])

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

  const handleRetry = async () => {
    if (!jobId) return
    try {
      await jobsService.retry(jobId)
      await jobsService.start(jobId)
      toast.success('Job retrying...')
      setActivityLog([])
    } catch {
      toast.error('Failed to retry job')
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
  const progress = getOverallProgress(job.status)

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

          {/* Retry button (shown when failed) */}
          {job.status === 'failed' && (
            <Button
              variant="secondary"
              leftIcon={<RefreshIcon />}
              onClick={handleRetry}
              className="text-apple-orange hover:text-apple-orange"
            >
              Retry
            </Button>
          )}

          {/* View Dashboard button */}
          <Button
            variant="primary"
            leftIcon={<DashboardIcon />}
            onClick={handleViewDashboard}
          >
            View Dashboard
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
            totalProfiles={job.discovery_limit ?? 50}
            completedProfiles={analytics?.done_profiles ?? job.profiles_scored}
            estimatedTime={isRunning ? '2-5 minutes' : undefined}
          />
        </div>

        {/* Activity Log */}
        <div className="lg:col-span-1">
          <ActivityLog entries={displayLog} maxHeight="500px" />
        </div>
      </div>

      {/* Error Message */}
      {job.status === 'failed' && job.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-sm text-red-700 font-medium">Error Details</p>
          <p className="text-sm text-red-600 mt-1">{job.error_message}</p>
        </div>
      )}

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
