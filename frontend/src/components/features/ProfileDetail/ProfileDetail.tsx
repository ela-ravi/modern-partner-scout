import { useCallback } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { ScoreRing } from '@/components/ui/ScoreRing'
import { ScoreBreakdown } from '@/components/composite/ScoreBreakdown'
import { useToast } from '@/components/ui/Toast'
import CloseIcon from '@mui/icons-material/Close'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import EmailIcon from '@mui/icons-material/Email'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import BookmarkIcon from '@mui/icons-material/Bookmark'
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder'
import BlockIcon from '@mui/icons-material/Block'
import StarIcon from '@mui/icons-material/Star'
import ThumbUpIcon from '@mui/icons-material/ThumbUp'
import PhoneIcon from '@mui/icons-material/Phone'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import LanguageIcon from '@mui/icons-material/Language'
import type { Profile } from '@/types/api/profile'

export interface ProfileDetailProps {
  /** Profile to display */
  profile: Profile
  /** Whether the modal is open */
  isOpen: boolean
  /** Called when modal should close */
  onClose: () => void
  /** Called when email button is clicked */
  onEmail?: (profile: Profile) => void
  /** Called when bookmark is toggled */
  onBookmark?: (profile: Profile) => void
  /** Called when skip is clicked */
  onSkip?: (profile: Profile) => void
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    const val = num / 1000000
    return val % 1 === 0 ? `${val}M` : `${val.toFixed(1)}M`
  }
  if (num >= 1000) {
    const val = num / 1000
    return val % 1 === 0 ? `${val}K` : `${val.toFixed(1)}K`
  }
  return String(num)
}

function getMatchLabel(score: number): { label: string; color: string } {
  if (score >= 90) return { label: 'Excellent Match', color: 'text-apple-green' }
  if (score >= 80) return { label: 'Great Match', color: 'text-apple-green' }
  if (score >= 70) return { label: 'Good Match', color: 'text-apple-blue' }
  if (score >= 60) return { label: 'Fair Match', color: 'text-apple-orange' }
  return { label: 'Low Match', color: 'text-apple-text-secondary' }
}

export function ProfileDetail({
  profile,
  isOpen,
  onClose,
  onEmail,
  onBookmark,
  onSkip,
}: ProfileDetailProps) {
  const toast = useToast()
  const score = profile.score?.overall_score ?? 0
  const matchInfo = getMatchLabel(score)

  const handleCopyEmail = useCallback(async () => {
    if (!profile.email) return
    try {
      await navigator.clipboard.writeText(profile.email)
      toast.success('Email copied to clipboard')
    } catch {
      toast.error('Failed to copy email')
    }
  }, [profile.email, toast])

  const handleViewOnInstagram = useCallback(() => {
    window.open(`https://instagram.com/${profile.username}`, '_blank')
  }, [profile.username])

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        {/* Backdrop */}
        <Dialog.Overlay
          className={cn(
            'fixed inset-0 bg-black/40 backdrop-blur-sm z-50',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
            'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0'
          )}
        />

        {/* Modal */}
        <Dialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2',
            'w-full max-w-4xl max-h-[90vh] overflow-hidden',
            'bg-white rounded-2xl shadow-2xl z-50',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
            'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
            'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
            'data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]',
            'data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]',
            'duration-200'
          )}
        >
          {/* Header with Cover */}
          <div className="relative h-40 bg-gradient-to-br from-emerald-100 to-teal-100">
            {/* Close Button */}
            <Dialog.Close asChild>
              <button
                className={cn(
                  'absolute top-4 right-4 w-9 h-9 rounded-full',
                  'bg-white/90 backdrop-blur-md flex items-center justify-center',
                  'text-apple-text-secondary hover:text-apple-text transition-colors shadow-sm z-20',
                  'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue'
                )}
                aria-label="Close modal"
              >
                <CloseIcon className="w-5 h-5" />
              </button>
            </Dialog.Close>

            {/* Top Match Badge */}
            {score >= 90 && (
              <div className="absolute top-4 left-4 z-20">
                <Badge variant="warning" className="gap-1.5">
                  <StarIcon className="w-3 h-3" />
                  TOP MATCH
                </Badge>
              </div>
            )}

            {/* Profile overlay section */}
            <div className="absolute bottom-0 left-0 right-0 px-8 pb-4 pt-12 bg-gradient-to-t from-white via-white/95 to-transparent">
              <div className="flex flex-col md:flex-row gap-4 md:items-end">
                <Avatar
                  src={profile.profile_pic_url}
                  alt={`Profile photo of ${profile.full_name}`}
                  name={profile.full_name}
                  size="2xl"
                  className="ring-4 ring-white shadow-lg -mb-8"
                />
                <div className="flex-1 flex flex-wrap items-center justify-between gap-4 pb-1">
                  <div>
                    <Dialog.Title className="text-2xl font-semibold mb-1 text-apple-text">
                      {profile.full_name}
                    </Dialog.Title>
                    <Dialog.Description className="sr-only">
                      Profile details for {profile.full_name}
                    </Dialog.Description>
                    <a
                      href={`https://instagram.com/${profile.username}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-apple-blue hover:underline text-sm"
                    >
                      @{profile.username}
                    </a>
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    leftIcon={<OpenInNewIcon className="w-4 h-4" />}
                    onClick={handleViewOnInstagram}
                  >
                    View on Instagram
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Info */}
          <div className="relative px-8 pt-10 pb-8 bg-white">
            <div className="grid lg:grid-cols-3 gap-6 overflow-y-auto max-h-[calc(90vh-240px)] scrollbar-thin pr-2">
              {/* Left Column */}
              <div className="lg:col-span-2 space-y-5">
                {/* Bio */}
                {profile.bio && (
                  <div className="bg-apple-gray rounded-2xl p-5">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-3">
                      Bio
                    </h3>
                    <p className="text-apple-text-secondary text-sm leading-relaxed whitespace-pre-line">
                      {profile.bio}
                    </p>
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-apple-gray rounded-2xl p-4 text-center">
                    <p className="text-xl font-semibold">{formatNumber(profile.follower_count)}</p>
                    <p className="text-apple-text-tertiary text-xs">Followers</p>
                  </div>
                  <div className="bg-apple-gray rounded-2xl p-4 text-center">
                    <p className="text-xl font-semibold">{formatNumber(profile.following_count)}</p>
                    <p className="text-apple-text-tertiary text-xs">Following</p>
                  </div>
                  <div className="bg-apple-gray rounded-2xl p-4 text-center">
                    <p className="text-xl font-semibold text-apple-green">{profile.engagement_rate}%</p>
                    <p className="text-apple-text-tertiary text-xs">Engagement</p>
                  </div>
                  <div className="bg-apple-gray rounded-2xl p-4 text-center">
                    <p className="text-xl font-semibold">{formatNumber(profile.post_count)}</p>
                    <p className="text-apple-text-tertiary text-xs">Posts</p>
                  </div>
                </div>

                {/* AI Analysis */}
                {profile.score?.reasoning && (
                  <div className="bg-apple-gray rounded-2xl p-5">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-3">
                      AI Analysis
                    </h3>
                    <p className="text-apple-text-secondary text-sm leading-relaxed">
                      {typeof profile.score.reasoning === 'string'
                        ? profile.score.reasoning
                        : 'AI analysis completed.'}
                    </p>
                  </div>
                )}
              </div>

              {/* Right Column - Score & Actions */}
              <div className="space-y-5">
                {/* Match Score */}
                {profile.score && (
                  <div className="bg-apple-gray rounded-2xl p-5 text-center">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-4">
                      Match Score
                    </h3>
                    <div className="flex justify-center mb-3">
                      <ScoreRing score={score} size={112} strokeWidth={8} />
                    </div>
                    <p className={cn('text-sm font-medium', matchInfo.color)}>{matchInfo.label}</p>
                  </div>
                )}

                {/* Score Breakdown */}
                {profile.score && (
                  <div className="bg-apple-gray rounded-2xl p-5">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-4">
                      Score Breakdown
                    </h3>
                    <ScoreBreakdown score={profile.score} />
                  </div>
                )}

                {/* AI Recommendation */}
                {score >= 80 && (
                  <div className="bg-gradient-to-br from-apple-green/5 to-emerald-50 border border-apple-green/20 rounded-2xl p-5">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-3">
                      AI Recommendation
                    </h3>
                    <div className="flex items-start gap-3">
                      <ThumbUpIcon className="text-apple-green flex-shrink-0" />
                      <div>
                        <p className="font-semibold text-apple-green text-sm mb-1">Highly Recommended</p>
                        <p className="text-apple-text-secondary text-xs leading-relaxed">
                          Strong brand alignment with excellent engagement. Ideal for collaboration.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Contact Info */}
                {(profile.email || profile.phone || profile.address || profile.website) && (
                  <div className="bg-apple-gray rounded-2xl p-5">
                    <h3 className="font-medium text-apple-text-secondary text-xs uppercase tracking-wider mb-3">
                      Contact
                    </h3>
                    <div className="space-y-2">
                      {profile.email && (
                        <div className="flex items-center gap-3 p-3 bg-white rounded-xl">
                          <EmailIcon className="text-apple-orange flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <span className="text-sm truncate block">{profile.email}</span>
                            {profile.email_source && (
                              <Badge variant="info" size="sm" className="mt-1">
                                {profile.email_source}
                              </Badge>
                            )}
                          </div>
                          <button
                            onClick={handleCopyEmail}
                            className="text-apple-text-tertiary hover:text-apple-blue transition-colors flex-shrink-0"
                            aria-label="Copy email address"
                          >
                            <ContentCopyIcon className="w-5 h-5" />
                          </button>
                        </div>
                      )}
                      {profile.phone && (
                        <div className="flex items-center gap-3 p-3 bg-white rounded-xl">
                          <PhoneIcon className="text-apple-green flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <span className="text-sm truncate block">{profile.phone}</span>
                            <Badge variant="info" size="sm" className="mt-1">
                              phone
                            </Badge>
                          </div>
                        </div>
                      )}
                      {profile.address && (
                        <div className="flex items-center gap-3 p-3 bg-white rounded-xl">
                          <LocationOnIcon className="text-apple-red flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <span className="text-sm block leading-snug">{profile.address}</span>
                            <Badge variant="info" size="sm" className="mt-1">
                              address
                            </Badge>
                          </div>
                        </div>
                      )}
                      {profile.website && (
                        <div className="flex items-center gap-3 p-3 bg-white rounded-xl">
                          <LanguageIcon className="text-apple-blue flex-shrink-0" />
                          <a
                            href={profile.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 min-w-0 text-sm text-apple-blue hover:underline truncate block"
                          >
                            {profile.website.replace(/^https?:\/\//, '')}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="space-y-3">
                  {profile.email && (
                    <Button
                      variant="primary"
                      className="w-full"
                      leftIcon={<EmailIcon />}
                      onClick={() => onEmail?.(profile)}
                      aria-label="Compose email"
                    >
                      Compose Email
                    </Button>
                  )}
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      variant="secondary"
                      leftIcon={profile.is_bookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
                      onClick={() => onBookmark?.(profile)}
                      aria-label={profile.is_bookmarked ? 'Saved' : 'Save'}
                    >
                      {profile.is_bookmarked ? 'Saved' : 'Save'}
                    </Button>
                    <Button
                      variant="secondary"
                      leftIcon={<BlockIcon />}
                      onClick={() => onSkip?.(profile)}
                      aria-label="Skip this profile"
                    >
                      Skip
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
