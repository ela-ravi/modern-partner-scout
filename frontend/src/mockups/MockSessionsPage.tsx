import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { SessionCard } from '@/components/composite/SessionCard'
import { MockDashboardLayout } from './MockDashboardLayout'
import { MOCK_JOBS } from './_data/mockJobs'
import type { Job } from '@/types/api/job'
import AddIcon from '@mui/icons-material/Add'

export default function MockSessionsPage() {
  const [jobToDelete, setJobToDelete] = useState<Job | null>(null)

  return (
    <MockDashboardLayout activePath="/mockups/sessions">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-apple-text">Discovery Sessions</h1>
            <p className="text-apple-text-secondary mt-1">
              Manage your partner discovery campaigns
            </p>
          </div>
          <Link to="/mockups/discovery-config">
            <Button leftIcon={<AddIcon />}>New Session</Button>
          </Link>
        </div>

        {/* Sessions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {MOCK_JOBS.map((job, i) => (
            <div
              key={job.id}
              className="animate-slide-up"
              style={{ animationDelay: `${i * 60}ms`, animationFillMode: 'backwards' }}
            >
              <SessionCard
                job={job}
                onDelete={setJobToDelete}
              />
            </div>
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
              <strong>&quot;{jobToDelete?.name}&quot;</strong>?
            </p>
            <p className="text-sm text-apple-text-secondary">
              All discovered profiles and data will be permanently removed.
            </p>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="secondary" onClick={() => setJobToDelete(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={() => setJobToDelete(null)}>
                Delete Session
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MockDashboardLayout>
  )
}
