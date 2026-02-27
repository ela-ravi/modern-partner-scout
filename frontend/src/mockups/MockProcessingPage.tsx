import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PipelineProgress } from '@/components/features/PipelineProgress'
import { ActivityLog } from '@/components/composite/ActivityLog'
import { MockDashboardLayout } from './MockDashboardLayout'
import { MOCK_PIPELINE_STAGES } from './_data/mockPipelineStages'
import { MOCK_LOG_ENTRIES } from './_data/mockLogEntries'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import StopCircleIcon from '@mui/icons-material/StopCircle'
import DashboardIcon from '@mui/icons-material/Dashboard'

export default function MockProcessingPage() {
  return (
    <MockDashboardLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link to="/mockups/sessions">
              <Button variant="ghost" size="sm" aria-label="Back to sessions">
                <ArrowBackIcon className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-apple-text">Processing Pipeline</h1>
              <p className="text-sm text-apple-text-secondary mt-0.5">
                Fitness Brand Collab Q3 • Started 2:32 PM
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Badge variant="processing" className="gap-2">
              <span className="w-2 h-2 bg-apple-blue rounded-full animate-pulse" />
              Discovery Running
            </Badge>

            <Button variant="secondary" leftIcon={<StopCircleIcon />}>
              Stop
            </Button>

            <Link to="/mockups/dashboard">
              <Button variant="primary" leftIcon={<DashboardIcon />}>
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Pipeline Progress */}
          <div className="lg:col-span-2">
            <PipelineProgress
              stages={MOCK_PIPELINE_STAGES}
              overallProgress={70}
              totalProfiles={30}
              completedProfiles={22}
              estimatedTime="2-5 minutes"
            />
          </div>

          {/* Activity Log */}
          <div className="lg:col-span-1">
            <ActivityLog entries={MOCK_LOG_ENTRIES} maxHeight="500px" />
          </div>
        </div>
      </div>
    </MockDashboardLayout>
  )
}
