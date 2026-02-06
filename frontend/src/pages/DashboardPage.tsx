import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import * as Tabs from '@radix-ui/react-tabs'
import * as Select from '@radix-ui/react-select'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { StatsGrid } from '@/components/composite/StatsGrid'
import { ProfileGrid } from '@/components/features/ProfileGrid'
import { ProfileDetail } from '@/components/features/ProfileDetail'
import { EmailComposer } from '@/components/features/EmailComposer'
import { useJob } from '@/hooks/jobs'
import { useProfiles, useJobAnalytics, useToggleBookmark, useSkipProfile } from '@/hooks/profiles'
import { useRealtimeProfiles } from '@/hooks/realtime'
import { useToast } from '@/components/ui/Toast'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import CheckIcon from '@mui/icons-material/Check'
import type { Profile, ProfileStatus, ProfileSort } from '@/types/api/profile'
import type { JobStatus } from '@/types/api/job'
import type { EmailComposerData } from '@/types/api/email'

const STATUS_TABS = [
  { value: 'all', label: 'All' },
  { value: 'new', label: 'New' },
  { value: 'processing', label: 'Processing' },
  { value: 'done', label: 'Scored' },
] as const

const SORT_OPTIONS = [
  { value: 'score-desc', label: 'Score: High to Low' },
  { value: 'score-asc', label: 'Score: Low to High' },
  { value: 'created_at-desc', label: 'Newest First' },
  { value: 'created_at-asc', label: 'Oldest First' },
  { value: 'follower_count-desc', label: 'Most Followers' },
  { value: 'engagement_rate-desc', label: 'Highest Engagement' },
] as const

function getJobStatusBadge(status: JobStatus) {
  switch (status) {
    case 'completed':
      return <Badge variant="done">Completed</Badge>
    case 'scoring':
    case 'discovering':
    case 'analyzing':
      return <Badge variant="processing">{status}</Badge>
    case 'pending':
      return <Badge variant="new">Pending</Badge>
    case 'failed':
      return <Badge variant="failed">Failed</Badge>
    case 'cancelled':
      return <Badge variant="cancelled">Cancelled</Badge>
    default:
      return null
  }
}

function parseSort(value: string): ProfileSort {
  const [field, direction] = value.split('-') as [ProfileSort['field'], ProfileSort['direction']]
  return { field, direction }
}

export default function DashboardPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const toggleBookmark = useToggleBookmark()
  const skipProfile = useSkipProfile()

  const [activeTab, setActiveTab] = useState<string>('all')
  const [sortValue, setSortValue] = useState<string>('score-desc')
  const [page, setPage] = useState(1)
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null)
  const [emailProfile, setEmailProfile] = useState<EmailComposerData | null>(null)

  // Fetch job details
  const { data: job, isLoading: jobLoading } = useJob(jobId)

  // Fetch analytics
  const { data: analytics, isLoading: analyticsLoading } = useJobAnalytics(jobId)

  // Subscribe to real-time updates
  useRealtimeProfiles({
    jobId: jobId || '',
    enabled: !!jobId && job?.status !== 'completed' && job?.status !== 'failed',
  })

  // Fetch profiles
  const statusFilter = activeTab === 'all' ? undefined : (activeTab as ProfileStatus)
  const sort = parseSort(sortValue)

  const {
    data: profilesData,
    isLoading: profilesLoading,
    isFetching,
  } = useProfiles({
    job_id: jobId || '',
    page,
    page_size: 20,
    filters: statusFilter ? { status: statusFilter } : undefined,
    sort,
  })

  const handleLoadMore = () => {
    setPage((p) => p + 1)
  }

  const handleViewProfile = (profile: Profile) => {
    setSelectedProfile(profile)
  }

  const handleCloseProfile = () => {
    setSelectedProfile(null)
  }

  const handleSkipProfile = async (profile: Profile) => {
    if (!jobId) return
    try {
      await skipProfile.mutateAsync({ jobId, profileId: profile.id })
      toast.success(`Skipped ${profile.full_name}`)
      setSelectedProfile(null)
    } catch {
      toast.error('Failed to skip profile')
    }
  }

  const handleEmailProfile = (profile: Profile) => {
    if (!profile.email || !jobId) return
    setEmailProfile({
      profileId: profile.id,
      jobId,
      recipientName: profile.full_name,
      recipientEmail: profile.email,
      recipientHandle: profile.username,
      profileImageUrl: profile.profile_pic_url,
    })
    // Close the profile detail modal when opening email composer
    setSelectedProfile(null)
  }

  const handleEmailSent = () => {
    toast.success('Email sent successfully!')
    setEmailProfile(null)
  }

  const handleCloseEmailComposer = () => {
    setEmailProfile(null)
  }

  const handleBookmarkProfile = async (profile: Profile) => {
    if (!jobId) return
    try {
      await toggleBookmark.mutateAsync({ jobId, profileId: profile.id })
      toast.success(
        profile.is_bookmarked
          ? `Removed ${profile.full_name} from bookmarks`
          : `Added ${profile.full_name} to bookmarks`
      )
    } catch {
      toast.error('Failed to update bookmark')
    }
  }

  // Reset page when filters change
  const handleTabChange = (value: string) => {
    setActiveTab(value)
    setPage(1)
  }

  const handleSortChange = (value: string) => {
    setSortValue(value)
    setPage(1)
  }

  if (jobLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 w-64 bg-gray-200 rounded" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded-xl" />
          ))}
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
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-apple-text">{job.name}</h1>
              {getJobStatusBadge(job.status)}
            </div>
            <p className="text-sm text-apple-text-secondary mt-0.5">
              {job.profiles_discovered} profiles discovered • {job.profiles_scored} scored
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      {analytics && <StatsGrid analytics={analytics} isLoading={analyticsLoading} />}

      {/* Tabs and Sort */}
      <Tabs.Root value={activeTab} onValueChange={handleTabChange}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Tab List */}
          <Tabs.List
            className="flex gap-1 p-1 bg-gray-100 rounded-lg"
            aria-label="Filter profiles by status"
          >
            {STATUS_TABS.map((tab) => (
              <Tabs.Trigger
                key={tab.value}
                value={tab.value}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-md transition-all',
                  'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2',
                  'data-[state=active]:bg-white data-[state=active]:text-apple-text data-[state=active]:shadow-sm',
                  'data-[state=inactive]:text-apple-text-secondary data-[state=inactive]:hover:text-apple-text'
                )}
              >
                {tab.label}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          {/* Sort Dropdown */}
          <Select.Root value={sortValue} onValueChange={handleSortChange}>
            <Select.Trigger
              className={cn(
                'inline-flex items-center justify-between gap-2 px-3 py-2 rounded-lg',
                'bg-white border border-apple-border text-sm',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue',
                'min-w-[180px]'
              )}
              aria-label="Sort profiles"
            >
              <Select.Value />
              <Select.Icon>
                <KeyboardArrowDownIcon className="w-5 h-5 text-apple-text-secondary" />
              </Select.Icon>
            </Select.Trigger>

            <Select.Portal>
              <Select.Content
                className={cn(
                  'overflow-hidden bg-white rounded-lg shadow-lg border border-apple-border',
                  'animate-in fade-in-0 zoom-in-95'
                )}
                position="popper"
                sideOffset={4}
              >
                <Select.Viewport className="p-1">
                  {SORT_OPTIONS.map((option) => (
                    <Select.Item
                      key={option.value}
                      value={option.value}
                      className={cn(
                        'relative flex items-center px-8 py-2 text-sm rounded-md cursor-pointer',
                        'focus:outline-none focus:bg-apple-blue/10',
                        'data-[highlighted]:bg-apple-blue/10'
                      )}
                    >
                      <Select.ItemIndicator className="absolute left-2">
                        <CheckIcon className="w-4 h-4 text-apple-blue" />
                      </Select.ItemIndicator>
                      <Select.ItemText>{option.label}</Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Viewport>
              </Select.Content>
            </Select.Portal>
          </Select.Root>
        </div>

        {/* Profile Grid */}
        <div className="mt-6">
          <ProfileGrid
            profiles={profilesData?.profiles || []}
            isLoading={profilesLoading}
            hasMore={profilesData?.has_more}
            onLoadMore={handleLoadMore}
            isLoadingMore={isFetching && !profilesLoading}
            onView={handleViewProfile}
            onEmail={handleEmailProfile}
            onBookmark={handleBookmarkProfile}
          />
        </div>
      </Tabs.Root>

      {/* Profile Detail Modal */}
      {selectedProfile && (
        <ProfileDetail
          profile={selectedProfile}
          isOpen={!!selectedProfile}
          onClose={handleCloseProfile}
          onEmail={handleEmailProfile}
          onBookmark={handleBookmarkProfile}
          onSkip={handleSkipProfile}
        />
      )}

      {/* Email Composer Modal */}
      {emailProfile && (
        <EmailComposer
          isOpen={!!emailProfile}
          onClose={handleCloseEmailComposer}
          profile={emailProfile}
          onSent={handleEmailSent}
        />
      )}
    </div>
  )
}
