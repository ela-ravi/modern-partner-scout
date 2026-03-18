import { cn } from '@/lib/utils'
import { Badge, type BadgeVariant } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { ScoreRing } from '@/components/ui/ScoreRing'
import { Button } from '@/components/ui/Button'
import EmailIcon from '@mui/icons-material/Email'
import BookmarkIcon from '@mui/icons-material/Bookmark'
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder'
import VisibilityIcon from '@mui/icons-material/Visibility'
import PeopleIcon from '@mui/icons-material/People'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import type { Profile, ProfileStatus } from '@/types/api/profile'

export interface ProfileCardProps {
  /** Profile data */
  profile: Profile
  /** Called when view button is clicked */
  onView?: (profile: Profile) => void
  /** Called when email button is clicked */
  onEmail?: (profile: Profile) => void
  /** Called when bookmark is toggled */
  onBookmark?: (profile: Profile) => void
  /** Additional class names */
  className?: string
}

function getStatusVariant(status: ProfileStatus): BadgeVariant {
  switch (status) {
    case 'new':
      return 'new'
    case 'processing':
      return 'processing'
    case 'done':
      return 'done'
    case 'skipped':
      return 'cancelled'
    default:
      return 'default'
  }
}

function getStatusLabel(status: ProfileStatus): string {
  switch (status) {
    case 'new':
      return 'NEW'
    case 'processing':
      return 'Processing'
    case 'done':
      return 'Scored'
    case 'skipped':
      return 'Skipped'
    default:
      return status
  }
}

function formatFollowerCount(count: number): string {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`
  }
  return String(count)
}

export function ProfileCard({
  profile,
  onView,
  onEmail,
  onBookmark,
  className,
}: ProfileCardProps) {
  const score = profile.score?.overall_score ?? 0
  const hasEmail = !!profile.email

  return (
    <article
      aria-labelledby={`profile-name-${profile.id}`}
      className={cn(
        'group relative rounded-2xl bg-white shadow-sm border border-apple-border overflow-hidden',
        'transition-all duration-300 hover:shadow-lg hover:-translate-y-1',
        className
      )}
    >
      {/* Cover gradient */}
      <div
        className="h-20 bg-gradient-to-br from-apple-blue/20 via-purple-500/20 to-pink-500/20"
        aria-hidden="true"
      />

      {/* Avatar */}
      <div className="flex justify-center -mt-10 relative z-10">
        <Avatar
          src={profile.profile_pic_url}
          alt={`Profile photo of ${profile.full_name}`}
          name={profile.full_name}
          size="lg"
          className="ring-4 ring-white"
        />
      </div>

      {/* Content */}
      <div className="p-5 pt-3 text-center">
        {/* Name and username */}
        <h3
          id={`profile-name-${profile.id}`}
          className="font-semibold text-apple-text text-lg truncate"
        >
          {profile.full_name}
        </h3>
        <p className="text-sm text-apple-text-secondary truncate">@{profile.username}</p>

        {/* Status badge */}
        <div className="mt-2">
          <Badge variant={getStatusVariant(profile.status)} size="sm">
            {getStatusLabel(profile.status)}
          </Badge>
          {hasEmail && (
            <Badge variant="info" size="sm" className="ml-1">
              Email
            </Badge>
          )}
          {profile.phone && (
            <Badge variant="info" size="sm" className="ml-1">
              Phone
            </Badge>
          )}
          {profile.address && (
            <Badge variant="info" size="sm" className="ml-1">
              Address
            </Badge>
          )}
        </div>

        {/* Stats */}
        <div className="flex justify-center gap-4 mt-4 text-sm">
          <div className="flex items-center gap-1 text-apple-text-secondary">
            <PeopleIcon className="w-4 h-4" />
            <span className="font-medium text-apple-text">
              {formatFollowerCount(profile.follower_count)}
            </span>
          </div>
          <div className="flex items-center gap-1 text-apple-text-secondary">
            <TrendingUpIcon className="w-4 h-4" />
            <span className="font-medium text-apple-text">{profile.engagement_rate}%</span>
          </div>
        </div>

        {/* Score Ring */}
        {profile.score && (
          <div className="flex justify-center mt-4">
            <ScoreRing score={score} size={56} />
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-center gap-2 mt-4">
          <Button
            variant="primary"
            size="sm"
            onClick={() => onView?.(profile)}
            leftIcon={<VisibilityIcon className="w-4 h-4" />}
            aria-label={`View profile for ${profile.full_name}`}
          >
            View
          </Button>

          {hasEmail && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onEmail?.(profile)}
              aria-label={`Email ${profile.full_name}`}
            >
              <EmailIcon className="w-4 h-4" />
            </Button>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={() => onBookmark?.(profile)}
            aria-label={profile.is_bookmarked ? `Remove ${profile.full_name} from bookmarks` : `Bookmark ${profile.full_name}`}
            className={cn(
              profile.is_bookmarked && 'text-amber-500 hover:text-amber-600'
            )}
          >
            {profile.is_bookmarked ? (
              <BookmarkIcon className="w-4 h-4" />
            ) : (
              <BookmarkBorderIcon className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </article>
  )
}
