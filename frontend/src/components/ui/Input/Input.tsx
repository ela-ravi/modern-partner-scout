import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Label for the input */
  label?: string
  /** Error message to display */
  error?: string
  /** Helper text below the input */
  helperText?: string
  /** Icon to show on the left side */
  leftIcon?: ReactNode
  /** Icon to show on the right side */
  rightIcon?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const generatedId = useId()
    const inputId = id || generatedId
    const errorId = error ? `${inputId}-error` : undefined
    const helperId = helperText ? `${inputId}-helper` : undefined
    const describedBy = [errorId, helperId].filter(Boolean).join(' ') || undefined

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-apple-text mb-1.5"
          >
            {label}
            {props.required && <span className="text-apple-red ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-text-tertiary">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full px-4 py-3 rounded-xl',
              'bg-white border transition-all duration-200',
              'text-apple-text placeholder:text-apple-text-tertiary',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:border-transparent',
              // WCAG 3:1 border contrast
              error
                ? 'border-apple-red focus-visible:ring-apple-red'
                : 'border-gray-300 hover:border-gray-400',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              'disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-apple-text-tertiary',
              className
            )}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={describedBy}
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-apple-text-tertiary">
              {rightIcon}
            </div>
          )}
        </div>

        {error && (
          <p
            id={errorId}
            role="alert"
            className="mt-1.5 text-sm text-apple-red flex items-center gap-1"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={helperId} className="mt-1.5 text-sm text-apple-text-secondary">
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
