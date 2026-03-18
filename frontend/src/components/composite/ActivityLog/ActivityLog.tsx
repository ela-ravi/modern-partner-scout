/**
 * ActivityLog Component
 * Real-time log entries with ARIA live region
 */

import { useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'

export interface LogEntry {
  id: string
  timestamp: string
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
  score?: number
}

export interface ActivityLogProps {
  /** Log entries */
  entries: LogEntry[]
  /** Maximum height */
  maxHeight?: string
  /** Additional class names */
  className?: string
}

function getIndicator(type: LogEntry['type']) {
  switch (type) {
    case 'success':
      return <span className="text-apple-green font-medium">✓</span>
    case 'error':
      return <span className="text-apple-red font-medium">✗</span>
    case 'warning':
      return <span className="text-apple-orange font-medium">!</span>
    default:
      return <span className="text-apple-blue font-medium">→</span>
  }
}

function getScoreColor(score: number) {
  if (score >= 90) return 'text-apple-orange'
  if (score >= 80) return 'text-apple-blue'
  return 'text-apple-text-secondary'
}

export function ActivityLog({
  entries,
  maxHeight = '500px',
  className,
}: ActivityLogProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to latest entry
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [entries])

  if (entries.length === 0) {
    return (
      <div
        className={cn(
          'bg-white rounded-2xl border border-gray-200 p-6 text-center',
          className
        )}
      >
        <p className="text-apple-text-secondary text-sm">No activity yet</p>
        <p className="text-apple-text-tertiary text-xs mt-1">
          Activity will appear here as the pipeline runs
        </p>
      </div>
    )
  }

  return (
    <div
      className={cn('bg-white rounded-2xl border border-gray-200 p-4', className)}
    >
      <h3 className="font-semibold mb-4">Live Activity</h3>
      <div
        ref={containerRef}
        role="log"
        aria-live="polite"
        aria-relevant="additions"
        aria-label="Activity log"
        className="overflow-y-auto space-y-1.5 font-mono text-sm scrollbar-thin"
        style={{ maxHeight }}
      >
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="flex gap-3 items-center p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <span className="text-apple-text-tertiary text-xs whitespace-nowrap">
              {entry.timestamp}
            </span>
            {getIndicator(entry.type)}
            <span className="text-apple-text-secondary flex-1 truncate">
              {entry.message}
              {entry.score !== undefined && (
                <span className={cn('ml-2 font-medium', getScoreColor(entry.score))}>
                  {entry.score}%
                </span>
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
