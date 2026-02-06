import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { SessionCard } from '@/components/composite/SessionCard'
import { EmptyState } from '@/components/features/EmptyState'
import { useJobs, useDeleteJob } from '@/hooks/jobs'
import { useToast } from '@/components/ui/Toast'
import type { Job } from '@/types/api/job'
import AddIcon from '@mui/icons-material/Add'

export default function SessionsPage() {
  const { data: jobs, isLoading, error } = useJobs()
  const deleteJob = useDeleteJob()
  const toast = useToast()

  const [jobToDelete, setJobToDelete] = useState<Job | null>(null)

  const handleDeleteClick = (job: Job) => {
    setJobToDelete(job)
  }

  const handleConfirmDelete = async () => {
    if (!jobToDelete) return

    try {
      await deleteJob.mutateAsync(jobToDelete.id)
      toast.success(`"${jobToDelete.name}" deleted successfully`)
      setJobToDelete(null)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to delete session')
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-apple-text">Discovery Sessions</h1>
            <p className="text-apple-text-secondary mt-1">
              Manage your partner discovery campaigns
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-apple-red mb-4">Failed to load sessions</p>
        <p className="text-apple-text-secondary">{error.message}</p>
      </div>
    )
  }

  // Empty state
  if (!jobs || jobs.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-apple-text">Discovery Sessions</h1>
            <p className="text-apple-text-secondary mt-1">
              Manage your partner discovery campaigns
            </p>
          </div>
        </div>

        <EmptyState />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-apple-text">Discovery Sessions</h1>
          <p className="text-apple-text-secondary mt-1">
            Manage your partner discovery campaigns
          </p>
        </div>
        <Link to="/new-session">
          <Button leftIcon={<AddIcon />}>New Session</Button>
        </Link>
      </div>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {jobs.map((job) => (
          <SessionCard
            key={job.id}
            job={job}
            onDelete={handleDeleteClick}
          />
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        open={!!jobToDelete}
        onOpenChange={(open) => !open && setJobToDelete(null)}
        title="Delete Session"
        description="This action cannot be undone."
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-apple-text">
            Are you sure you want to delete{' '}
            <strong>"{jobToDelete?.name}"</strong>?
          </p>
          <p className="text-sm text-apple-text-secondary">
            All discovered profiles and data will be permanently removed.
          </p>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => setJobToDelete(null)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirmDelete}
              loading={deleteJob.isPending}
            >
              Delete Session
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
