import { cn } from '@/lib/utils'
import type { ProfileScore } from '@/types/api/profile'

export interface ScoreBreakdownProps {
  /** Score data */
  score: ProfileScore
  /** Additional class names */
  className?: string
}

const SCORE_DIMENSIONS: { key: keyof ProfileScore; label: string }[] = [
  { key: 'engagement', label: 'Engagement' },
  { key: 'relevance', label: 'Relevance' },
  { key: 'authenticity', label: 'Authenticity' },
  { key: 'reach', label: 'Reach' },
  { key: 'content_quality', label: 'Content Quality' },
  { key: 'brand_alignment', label: 'Brand Alignment' },
]

function getScoreColor(value: number): string {
  if (value >= 80) return 'bg-gradient-to-r from-apple-blue to-cyan-400'
  if (value >= 60) return 'bg-gradient-to-r from-apple-blue to-blue-400'
  if (value >= 40) return 'bg-gradient-to-r from-apple-orange to-yellow-400'
  return 'bg-gradient-to-r from-apple-red to-orange-400'
}

export function ScoreBreakdown({ score, className }: ScoreBreakdownProps) {
  // Build dimensions with values, filtering out undefined ones
  const dimensions = SCORE_DIMENSIONS.map((dim) => ({
    key: dim.key,
    label: dim.label,
    value: score[dim.key] as number | undefined,
  })).filter((dim): dim is { key: keyof ProfileScore; label: string; value: number } => 
    typeof dim.value === 'number'
  )

  return (
    <div className={cn('space-y-4', className)}>
      {dimensions.map((dim) => (
        <div key={dim.key}>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-sm text-apple-text-secondary">{dim.label}</span>
            <span className="text-sm font-semibold text-apple-blue">{dim.value}%</span>
          </div>
          <div className="h-1.5 bg-apple-gray rounded-full overflow-hidden">
            <div
              role="progressbar"
              aria-valuenow={dim.value}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${dim.label} score: ${dim.value} percent`}
              className={cn('h-full rounded-full transition-all duration-500', getScoreColor(dim.value))}
              style={{ width: `${dim.value}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
