import { cn } from '@/lib/utils'

export interface SkipLinkProps {
  /** Target element ID to skip to */
  targetId?: string
  /** Link text */
  children?: string
  /** Additional class names */
  className?: string
}

export function SkipLink({
  targetId = 'main-content',
  children = 'Skip to main content',
  className,
}: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={cn(
        // Visually hidden by default
        'sr-only',
        // Show on focus
        'focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100]',
        'focus:bg-white focus:px-4 focus:py-2 focus:rounded-xl',
        'focus:shadow-lg focus:text-apple-text focus:font-medium',
        'focus:ring-2 focus:ring-apple-blue focus:ring-offset-2',
        className
      )}
    >
      {children}
    </a>
  )
}
