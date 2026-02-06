import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/Skeleton'

export interface AvatarProps {
  /** Image source URL */
  src?: string
  /** Alt text for the image */
  alt: string
  /** Name for fallback initials */
  name?: string
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  /** Additional class names */
  className?: string
}

const sizeStyles = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-lg',
  '2xl': 'w-20 h-20 text-xl',
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function Avatar({ src, alt, name, size = 'md', className }: AvatarProps) {
  const [isLoading, setIsLoading] = useState(!!src)
  const [hasError, setHasError] = useState(false)

  const showImage = src && !hasError
  const showFallback = !src || hasError
  const initials = name ? getInitials(name) : '?'

  return (
    <div
      className={cn(
        'relative rounded-[16px] overflow-hidden',
        'bg-apple-gray flex items-center justify-center',
        'font-medium text-apple-text-secondary',
        sizeStyles[size],
        className
      )}
    >
      {isLoading && (
        <Skeleton
          variant="rectangular"
          className="absolute inset-0"
        />
      )}

      {showImage && (
        <img
          src={src}
          alt={alt}
          className="w-full h-full object-cover"
          onLoad={() => setIsLoading(false)}
          onError={() => {
            setIsLoading(false)
            setHasError(true)
          }}
        />
      )}

      {showFallback && !isLoading && (
        <span aria-label={name || alt}>{initials}</span>
      )}
    </div>
  )
}
