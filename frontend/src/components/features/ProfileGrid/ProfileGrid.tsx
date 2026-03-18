import { cn } from '@/lib/utils'
import { ProfileCard } from '@/components/composite/ProfileCard'
import { Button } from '@/components/ui/Button'
import { SkeletonCard } from '@/components/ui/Skeleton'
import SearchOffIcon from '@mui/icons-material/SearchOff'
import type { Profile } from '@/types/api/profile'

export interface ProfileGridProps {
  /** List of profiles to display */
  profiles: Profile[]
  /** Whether data is loading */
  isLoading?: boolean
  /** Whether there are more profiles to load */
  hasMore?: boolean
  /** Called when "Load More" is clicked */
  onLoadMore?: () => void
  /** Whether load more is in progress */
  isLoadingMore?: boolean
  /** Called when view is clicked */
  onView?: (profile: Profile) => void
  /** Called when email is clicked */
  onEmail?: (profile: Profile) => void
  /** Called when bookmark is toggled */
  onBookmark?: (profile: Profile) => void
  /** Additional class names */
  className?: string
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <SearchOffIcon className="w-8 h-8 text-apple-text-tertiary" />
      </div>
      <h3 className="text-lg font-semibold text-apple-text mb-1">No profiles found</h3>
      <p className="text-apple-text-secondary">
        Try adjusting your filters or wait for more profiles to be discovered.
      </p>
    </div>
  )
}

function LoadingGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonCard key={i} className="h-80" />
      ))}
    </div>
  )
}

export function ProfileGrid({
  profiles,
  isLoading,
  hasMore,
  onLoadMore,
  isLoadingMore,
  onView,
  onEmail,
  onBookmark,
  className,
}: ProfileGridProps) {
  if (isLoading) {
    return <LoadingGrid />
  }

  if (profiles.length === 0) {
    return <EmptyState />
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Profile Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {profiles.map((profile) => (
          <ProfileCard
            key={profile.id}
            profile={profile}
            onView={onView}
            onEmail={onEmail}
            onBookmark={onBookmark}
          />
        ))}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center">
          <Button
            variant="secondary"
            onClick={onLoadMore}
            loading={isLoadingMore}
          >
            Load More
          </Button>
        </div>
      )}
    </div>
  )
}
