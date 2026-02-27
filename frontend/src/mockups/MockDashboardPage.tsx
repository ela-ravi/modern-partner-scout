import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import * as Tabs from '@radix-ui/react-tabs'
import * as Select from '@radix-ui/react-select'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Avatar } from '@/components/ui/Avatar'
import { ScoreRing } from '@/components/ui/ScoreRing'
import { StatsGrid } from '@/components/composite/StatsGrid'
import { ScoreBreakdown } from '@/components/composite/ScoreBreakdown'
import { ProfileGrid } from '@/components/features/ProfileGrid'
import { MockDashboardLayout } from './MockDashboardLayout'
import { MOCK_PROFILES } from './_data/mockProfiles'
import { MOCK_ANALYTICS } from './_data/mockAnalytics'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import CheckIcon from '@mui/icons-material/Check'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import EmailIcon from '@mui/icons-material/Email'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import BookmarkIcon from '@mui/icons-material/Bookmark'
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder'
import PhoneIcon from '@mui/icons-material/Phone'
import LanguageIcon from '@mui/icons-material/Language'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import type { Profile } from '@/types/api/profile'

const STATUS_TABS = [
  { value: 'all', label: 'All' },
  { value: 'bookmarked', label: 'Bookmarked' },
  { value: 'new', label: 'New' },
  { value: 'processing', label: 'Processing' },
  { value: 'done', label: 'Scored' },
] as const

const SORT_OPTIONS = [
  { value: 'score-desc', label: 'Score: High to Low' },
  { value: 'score-asc', label: 'Score: Low to High' },
  { value: 'created_at-desc', label: 'Newest First' },
  { value: 'follower_count-desc', label: 'Most Followers' },
  { value: 'engagement_rate-desc', label: 'Highest Engagement' },
] as const

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return String(num)
}

function getMatchLabel(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Great Match', color: 'text-apple-green' }
  if (score >= 70) return { label: 'Good Match', color: 'text-apple-blue' }
  if (score >= 60) return { label: 'Fair Match', color: 'text-apple-orange' }
  return { label: 'Low Match', color: 'text-apple-text-secondary' }
}

export default function MockDashboardPage() {
  const [activeTab, setActiveTab] = useState('all')
  const [sortValue, setSortValue] = useState('score-desc')
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null)
  const [emailProfile, setEmailProfile] = useState<Profile | null>(null)

  // Filter profiles based on active tab
  const filteredProfiles = useMemo(() => {
    let filtered = [...MOCK_PROFILES]

    if (activeTab === 'bookmarked') {
      filtered = filtered.filter((p) => p.is_bookmarked)
    } else if (activeTab !== 'all') {
      filtered = filtered.filter((p) => p.status === activeTab)
    }

    // Sort
    const [field, dir] = sortValue.split('-')
    filtered.sort((a, b) => {
      let aVal: number, bVal: number
      switch (field) {
        case 'score':
          aVal = a.score?.overall_score ?? 0
          bVal = b.score?.overall_score ?? 0
          break
        case 'follower_count':
          aVal = a.follower_count
          bVal = b.follower_count
          break
        case 'engagement_rate':
          aVal = a.engagement_rate
          bVal = b.engagement_rate
          break
        default:
          aVal = new Date(a.created_at).getTime()
          bVal = new Date(b.created_at).getTime()
      }
      return dir === 'desc' ? bVal - aVal : aVal - bVal
    })

    return filtered
  }, [activeTab, sortValue])

  const handleViewProfile = (profile: Profile) => setSelectedProfile(profile)
  const handleEmailProfile = (profile: Profile) => {
    setSelectedProfile(null)
    setEmailProfile(profile)
  }
  const handleBookmark = () => {
    // No-op in mockup — visual only
  }

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
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-apple-text">Summer 2026 Skincare Campaign</h1>
                <Badge variant="done">Completed</Badge>
              </div>
              <p className="text-sm text-apple-text-secondary mt-0.5">
                48 profiles discovered • 45 scored
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <StatsGrid analytics={MOCK_ANALYTICS} isLoading={false} />

        {/* Tabs and Sort */}
        <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            {/* Tab List */}
            <Tabs.List className="flex gap-1 p-1 bg-gray-100 rounded-lg" aria-label="Filter profiles by status">
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
            <Select.Root value={sortValue} onValueChange={setSortValue}>
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
              profiles={filteredProfiles}
              isLoading={false}
              hasMore={true}
              onLoadMore={() => {}}
              isLoadingMore={false}
              onView={handleViewProfile}
              onEmail={handleEmailProfile}
              onBookmark={handleBookmark}
            />
          </div>
        </Tabs.Root>

        {/* Profile Detail Modal */}
        {selectedProfile && (
          <MockProfileDetailModal
            profile={selectedProfile}
            isOpen={!!selectedProfile}
            onClose={() => setSelectedProfile(null)}
            onEmail={handleEmailProfile}
          />
        )}

        {/* Email Composer Modal */}
        {emailProfile && (
          <MockEmailComposerModal
            profile={emailProfile}
            isOpen={!!emailProfile}
            onClose={() => setEmailProfile(null)}
          />
        )}
      </div>
    </MockDashboardLayout>
  )
}

/* ─── Inline Profile Detail Modal ─── */

function MockProfileDetailModal({
  profile,
  isOpen,
  onClose,
  onEmail,
}: {
  profile: Profile
  isOpen: boolean
  onClose: () => void
  onEmail: (profile: Profile) => void
}) {
  const score = profile.score?.overall_score ?? 0
  const matchInfo = getMatchLabel(score)

  return (
    <Modal open={isOpen} onOpenChange={(open) => !open && onClose()} title="" size="lg">
      <div className="space-y-6">
        {/* Profile Header */}
        <div className="flex items-start gap-4">
          <Avatar
            name={profile.full_name}
            alt={`${profile.full_name} avatar`}
            src={profile.profile_pic_url}
            size="lg"
          />
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-apple-text">{profile.full_name}</h2>
            <p className="text-apple-text-secondary">@{profile.username}</p>
            {profile.bio && (
              <p className="text-sm text-apple-text-secondary mt-2">{profile.bio}</p>
            )}
          </div>
          {profile.score && (
            <div className="flex flex-col items-center">
              <ScoreRing score={score} size={64} />
              <span className={cn('text-xs font-medium mt-1', matchInfo.color)}>
                {matchInfo.label}
              </span>
            </div>
          )}
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-lg font-bold text-apple-text">{formatNumber(profile.follower_count)}</p>
            <p className="text-xs text-apple-text-secondary">Followers</p>
          </div>
          <div>
            <p className="text-lg font-bold text-apple-text">{formatNumber(profile.following_count)}</p>
            <p className="text-xs text-apple-text-secondary">Following</p>
          </div>
          <div>
            <p className="text-lg font-bold text-apple-text">{formatNumber(profile.post_count)}</p>
            <p className="text-xs text-apple-text-secondary">Posts</p>
          </div>
          <div>
            <p className="text-lg font-bold text-apple-text">{profile.engagement_rate}%</p>
            <p className="text-xs text-apple-text-secondary">Engagement</p>
          </div>
        </div>

        {/* Score Breakdown */}
        {profile.score && (
          <div>
            <h3 className="text-sm font-semibold text-apple-text mb-3">Score Breakdown</h3>
            <ScoreBreakdown score={profile.score} />
          </div>
        )}

        {/* AI Reasoning */}
        {profile.score?.reasoning && (
          <div>
            <h3 className="text-sm font-semibold text-apple-text mb-2">AI Reasoning</h3>
            <p className="text-sm text-apple-text-secondary bg-gray-50 rounded-xl p-4">
              {profile.score.reasoning}
            </p>
          </div>
        )}

        {/* Contact Info */}
        {(profile.email || profile.phone || profile.website || profile.address) && (
          <div>
            <h3 className="text-sm font-semibold text-apple-text mb-3">Contact Information</h3>
            <div className="space-y-2">
              {profile.email && (
                <div className="flex items-center gap-2 text-sm">
                  <EmailIcon className="w-4 h-4 text-apple-text-secondary" />
                  <span className="text-apple-text">{profile.email}</span>
                  <button className="text-apple-text-tertiary hover:text-apple-blue" aria-label="Copy email">
                    <ContentCopyIcon className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
              {profile.phone && (
                <div className="flex items-center gap-2 text-sm">
                  <PhoneIcon className="w-4 h-4 text-apple-text-secondary" />
                  <span className="text-apple-text">{profile.phone}</span>
                </div>
              )}
              {profile.website && (
                <div className="flex items-center gap-2 text-sm">
                  <LanguageIcon className="w-4 h-4 text-apple-text-secondary" />
                  <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-apple-blue hover:underline">
                    {profile.website}
                  </a>
                </div>
              )}
              {profile.address && (
                <div className="flex items-center gap-2 text-sm">
                  <LocationOnIcon className="w-4 h-4 text-apple-text-secondary" />
                  <span className="text-apple-text">{profile.address}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 pt-2 border-t border-apple-border">
          <Button
            variant="secondary"
            leftIcon={profile.is_bookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
            onClick={() => {}}
          >
            {profile.is_bookmarked ? 'Bookmarked' : 'Bookmark'}
          </Button>

          {profile.email && (
            <Button leftIcon={<EmailIcon />} onClick={() => onEmail(profile)}>
              Compose Email
            </Button>
          )}

          <a
            href={`https://instagram.com/${profile.username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-auto"
          >
            <Button variant="ghost" rightIcon={<OpenInNewIcon />}>
              Open Instagram
            </Button>
          </a>
        </div>
      </div>
    </Modal>
  )
}

/* ─── Inline Email Composer Modal ─── */

function MockEmailComposerModal({
  profile,
  isOpen,
  onClose,
}: {
  profile: Profile
  isOpen: boolean
  onClose: () => void
}) {
  const tones = [
    { id: 'professional', name: 'Professional', active: true },
    { id: 'casual', name: 'Casual', active: false },
    { id: 'friendly', name: 'Friendly', active: false },
  ]

  return (
    <Modal open={isOpen} onOpenChange={(open) => !open && onClose()} title="Compose Email" size="lg">
      <div className="space-y-4">
        {/* Recipient */}
        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
          <Avatar name={profile.full_name} alt={`${profile.full_name} avatar`} src={profile.profile_pic_url} size="sm" />
          <div>
            <p className="text-sm font-medium text-apple-text">{profile.full_name}</p>
            <p className="text-xs text-apple-text-secondary">{profile.email || 'No email available'}</p>
          </div>
        </div>

        {/* Tone Selection */}
        <div>
          <span className="block text-sm font-medium text-apple-text mb-2">Tone</span>
          <div className="flex gap-2">
            {tones.map((tone) => (
              <button
                key={tone.id}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  tone.active
                    ? 'bg-apple-blue text-white'
                    : 'bg-gray-100 text-apple-text-secondary hover:bg-gray-200'
                )}
              >
                {tone.name}
              </button>
            ))}
          </div>
        </div>

        {/* Subject */}
        <div>
          <label htmlFor="mock-email-subject" className="block text-sm font-medium text-apple-text mb-1">Subject</label>
          <input
            id="mock-email-subject"
            type="text"
            className="w-full px-3 py-2 border border-apple-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-apple-blue"
            defaultValue={`Collaboration Opportunity — Summer Skincare Campaign`}
          />
        </div>

        {/* Body */}
        <div>
          <label htmlFor="mock-email-body" className="block text-sm font-medium text-apple-text mb-1">Message</label>
          <textarea
            id="mock-email-body"
            className="w-full px-3 py-2 border border-apple-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-apple-blue min-h-[200px]"
            defaultValue={`Hi ${profile.full_name},

I've been following your incredible skincare content on Instagram and I'm really impressed by the way you combine ${profile.bio?.includes('Korean') ? 'K-beauty' : 'clean beauty'} expertise with authentic product reviews.

We're launching a new organic skincare line this summer and I think your audience would love it. We'd love to explore a collaboration — whether that's a product review, sponsored content, or something creative you have in mind.

Would you be open to a quick chat this week?

Best regards,
PartnerScout AI Team`}
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button leftIcon={<EmailIcon />} onClick={onClose}>Send Email</Button>
        </div>
      </div>
    </Modal>
  )
}
