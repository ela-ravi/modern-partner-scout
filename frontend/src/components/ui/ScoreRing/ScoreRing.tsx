import { cn } from '@/lib/utils'

export interface ScoreRingProps {
  /** Score value (0-100) */
  score: number
  /** Size of the ring in pixels */
  size?: number
  /** Stroke width */
  strokeWidth?: number
  /** Show score number in center */
  showValue?: boolean
  /** Additional class names */
  className?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'var(--color-apple-green, #34c759)'
  if (score >= 60) return 'var(--color-apple-blue, #0071e3)'
  if (score >= 40) return 'var(--color-apple-orange, #ff9500)'
  return 'var(--color-apple-red, #ff3b30)'
}

export function ScoreRing({
  score,
  size = 64,
  strokeWidth = 6,
  showValue = true,
  className,
}: ScoreRingProps) {
  const normalizedScore = Math.max(0, Math.min(100, score))
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (normalizedScore / 100) * circumference
  const color = getScoreColor(normalizedScore)

  return (
    <div
      className={cn('relative inline-flex items-center justify-center', className)}
      role="progressbar"
      aria-valuenow={normalizedScore}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Match score: ${normalizedScore} out of 100`}
    >
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-100"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 0.5s ease-out',
          }}
        />
      </svg>
      
      {showValue && (
        <span
          className="absolute inset-0 flex items-center justify-center font-semibold"
          style={{
            fontSize: size * 0.28,
            color,
          }}
          aria-hidden="true"
        >
          {normalizedScore}
        </span>
      )}
    </div>
  )
}
