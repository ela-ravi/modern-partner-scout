import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cn } from '@/lib/utils'
import CircularProgress from '@mui/icons-material/Loop'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Show loading spinner */
  loading?: boolean
  /** Icon to display on the left */
  leftIcon?: ReactNode
  /** Icon to display on the right */
  rightIcon?: ReactNode
  /** Use child as button element (for links styled as buttons) */
  asChild?: boolean
}

const variantStyles = {
  primary:
    'bg-apple-blue text-white hover:bg-apple-blue-hover focus-visible:ring-apple-blue disabled:bg-apple-blue/50',
  secondary:
    'bg-apple-gray text-apple-text hover:bg-gray-200 focus-visible:ring-gray-400 disabled:bg-gray-100',
  ghost:
    'bg-transparent text-apple-text-secondary hover:bg-apple-gray focus-visible:ring-gray-400 disabled:text-apple-text-tertiary',
  danger:
    'bg-apple-red text-white hover:bg-red-600 focus-visible:ring-apple-red disabled:bg-apple-red/50',
}

const sizeStyles = {
  sm: 'h-8 px-3 text-sm gap-1.5 min-w-[60px]',
  md: 'h-10 px-4 text-sm gap-2 min-w-[80px]',
  lg: 'h-12 px-6 text-base gap-2.5 min-w-[100px]',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      disabled,
      children,
      asChild = false,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button'
    const isDisabled = disabled || loading

    return (
      <Comp
        className={cn(
          // Base styles
          'inline-flex items-center justify-center font-medium rounded-xl',
          'transition-all duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed',
          // Minimum touch target for WCAG 2.5.8
          'min-h-[24px] min-w-[24px]',
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        {...props}
      >
        {loading ? (
          <>
            <CircularProgress
              className="animate-spin h-4 w-4"
              aria-hidden="true"
            />
            <span className="sr-only">Loading</span>
            {children}
          </>
        ) : (
          <>
            {leftIcon && <span aria-hidden="true">{leftIcon}</span>}
            {children}
            {rightIcon && <span aria-hidden="true">{rightIcon}</span>}
          </>
        )}
      </Comp>
    )
  }
)

Button.displayName = 'Button'
