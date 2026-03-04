import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/Card'
import PeopleIcon from '@mui/icons-material/People'
import StarIcon from '@mui/icons-material/Star'
import EmailIcon from '@mui/icons-material/Email'
import ScoreIcon from '@mui/icons-material/Score'
import type { JobAnalytics } from '@/types/api/profile'

export interface StatsGridProps {
  /** Analytics data */
  analytics: JobAnalytics
  /** Whether data is loading */
  isLoading?: boolean
  /** Additional class names */
  className?: string
}

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  color: string
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-3">
        <div
          className={cn(
            'w-10 h-10 rounded-xl flex items-center justify-center',
            color
          )}
        >
          {icon}
        </div>
        <div>
          <p className="text-sm text-apple-text-secondary">{label}</p>
          <p className="text-xl font-bold text-apple-text tabular-nums">{value}</p>
        </div>
      </div>
    </Card>
  )
}

function StatCardSkeleton() {
  return (
    <Card className="p-4 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gray-200" />
        <div className="space-y-2">
          <div className="h-3 w-16 bg-gray-200 rounded" />
          <div className="h-6 w-12 bg-gray-200 rounded" />
        </div>
      </div>
    </Card>
  )
}

export function StatsGrid({ analytics, isLoading, className }: StatsGridProps) {
  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    )
  }

  return (
    <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      <StatCard
        label="Processed"
        value={analytics.total_profiles}
        icon={<PeopleIcon className="w-5 h-5 text-white" />}
        color="bg-apple-blue"
      />
      <StatCard
        label="Qualified"
        value={analytics.done_profiles}
        icon={<StarIcon className="w-5 h-5 text-white" />}
        color="bg-green-500"
      />
      <StatCard
        label="Emails Found"
        value={analytics.profiles_with_email}
        icon={<EmailIcon className="w-5 h-5 text-white" />}
        color="bg-purple-500"
      />
      <StatCard
        label="Avg Score"
        value={analytics.avg_score != null ? `${Math.round(analytics.avg_score)}%` : 'N/A'}
        icon={<ScoreIcon className="w-5 h-5 text-white" />}
        color="bg-amber-500"
      />
    </div>
  )
}
