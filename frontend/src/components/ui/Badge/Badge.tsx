import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import BlockIcon from '@mui/icons-material/Block'
import FiberNewIcon from '@mui/icons-material/FiberNew'

export type BadgeVariant = 'new' | 'processing' | 'done' | 'failed' | 'cancelled' | 'info' | 'warning' | 'default'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Visual variant */
  variant?: BadgeVariant
  /** Optional icon override */
  icon?: ReactNode
  /** Show icon alongside text (WCAG 1.4.1 - not color alone) */
  showIcon?: boolean
  /** Size variant */
  size?: 'sm' | 'md'
}

const variantConfig: Record<
  BadgeVariant,
  { className: string; icon: ReactNode; label: string }
> = {
  new: {
    className: 'bg-apple-blue/10 text-apple-blue',
    icon: <FiberNewIcon className="w-3.5 h-3.5" />,
    label: 'New',
  },
  processing: {
    className: 'bg-apple-orange/10 text-apple-orange',
    icon: <HourglassEmptyIcon className="w-3.5 h-3.5 animate-pulse" />,
    label: 'Processing',
  },
  done: {
    className: 'bg-apple-green/10 text-apple-green',
    icon: <CheckCircleIcon className="w-3.5 h-3.5" />,
    label: 'Done',
  },
  failed: {
    className: 'bg-apple-red/10 text-apple-red',
    icon: <ErrorIcon className="w-3.5 h-3.5" />,
    label: 'Failed',
  },
  cancelled: {
    className: 'bg-gray-100 text-apple-text-secondary',
    icon: <BlockIcon className="w-3.5 h-3.5" />,
    label: 'Cancelled',
  },
  info: {
    className: 'bg-purple-100 text-purple-600',
    icon: null,
    label: 'Info',
  },
  warning: {
    className: 'bg-apple-orange/90 text-white',
    icon: null,
    label: 'Warning',
  },
  default: {
    className: 'bg-apple-gray text-apple-text-secondary',
    icon: null,
    label: '',
  },
}

const sizeStyles = {
  sm: 'px-2 py-0.5 text-[11px]',
  md: 'px-2.5 py-0.5 text-xs',
}

export function Badge({
  className,
  variant = 'default',
  icon,
  showIcon = true,
  size = 'md',
  children,
  ...props
}: BadgeProps) {
  const config = variantConfig[variant]
  const displayIcon = icon ?? config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        sizeStyles[size],
        config.className,
        className
      )}
      aria-label={children ? undefined : config.label}
      {...props}
    >
      {showIcon && displayIcon && (
        <span aria-hidden="true">{displayIcon}</span>
      )}
      {children}
    </span>
  )
}
