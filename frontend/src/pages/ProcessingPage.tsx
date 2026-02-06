/**
 * ProcessingPage
 * Shows real-time AI pipeline processing status
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { PipelineProgress, type PipelineStage } from '@/components/features/PipelineProgress'
import { ActivityLog, type LogEntry } from '@/components/composite/ActivityLog'
import { useJob, useCancelJob } from '@/hooks/jobs'
import { useJobAnalytics } from '@/hooks/profiles'
import { useToast } from '@/components/ui/Toast'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import StopCircleIcon from '@mui/icons-material/StopCircle'
import DashboardIcon from '@mui/icons-material/Dashboard'
import RefreshIcon from '@mui/icons-material/Refresh'
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
      // Find the stage that failed
      const failedIndex = stages.findIndex((s) => s.status === 'active')
      if (failedIndex >= 0) {
        stages[failedIndex].status = 'failed'
        stages[failedIndex].error = 'Processing failed'
      } else {
        stages[0].status = 'failed'
        stages[0].error = 'Processing failed'
      }
      break
    case 'cancelled':
      stages.forEach((s) => {
        if (s.status === 'active') s.status = 'pending'
      })
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

  const [showCancelModal, setShowCancelModal] = useState(false)
  const [activityLog, setActivityLog] = useState<LogEntry[]>([])

  // Fetch job details
  const { data: job, isLoading: jobLoading } = useJob(jobId)
  const { data: analytics } = useJobAnalytics(jobId)

  // Simulate activity log updates (in real app, this would come from WebSocket or polling)
  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'failed') return

    const addLogEntry = () => {
      const types: LogEntry['type'][] = ['info', 'success', 'success', 'info']
      const messages = [
        'Discovered @mindful_living',
        'Scored @cleaneatingamy',
        'Email found for @wellnessbysarah',
        'Processing @yogawithjames',
      ]

      const now = new Date()
      const timestamp = now.toTimeString().slice(0, 8)
      const entry: LogEntry = {
        id: `${Date.now()}`,
        timestamp,
        type: types[Math.floor(Math.random() * types.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
        score: Math.random() > 0.5 ? Math.floor(Math.random() * 30) + 70 : undefined,
      }

      setActivityLog((prev) => [...prev.slice(-49), entry])
    }

    const interval = setInterval(addLogEntry, 2000)
    return () => clearInterval(interval)
  }, [job])

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

  const isRunning = ['pending', 'analyzing', 'discovering', 'scoring'].includes(job.status)
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
              onClick={() => toast.info('Retry not implemented yet')}
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
