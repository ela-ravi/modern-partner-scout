import { forwardRef, useId, type TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** Label for the textarea */
  label?: string
  /** Error message to display */
  error?: string
  /** Helper text below the textarea */
  helperText?: string
  /** Show character count */
  showCount?: boolean
  /** Maximum character length */
  maxLength?: number
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    { className, label, error, helperText, showCount, maxLength, id, value, ...props },
    ref
  ) => {
    const generatedId = useId()
    const textareaId = id || generatedId
    const errorId = error ? `${textareaId}-error` : undefined
    const helperId = helperText ? `${textareaId}-helper` : undefined
    const describedBy = [errorId, helperId].filter(Boolean).join(' ') || undefined

    const currentLength = typeof value === 'string' ? value.length : 0

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-apple-text mb-1.5"
          >
            {label}
            {props.required && <span className="text-apple-red ml-1">*</span>}
          </label>
        )}

        <textarea
          ref={ref}
          id={textareaId}
          value={value}
          maxLength={maxLength}
          className={cn(
            'w-full px-4 py-3 rounded-xl resize-y min-h-[120px]',
            'bg-white border transition-all duration-200',
            'text-apple-text placeholder:text-apple-text-tertiary',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:border-transparent',
            error
              ? 'border-apple-red focus-visible:ring-apple-red'
              : 'border-gray-300 hover:border-gray-400',
            'disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-apple-text-tertiary',
            className
          )}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={describedBy}
          {...props}
        />

        <div className="flex justify-between items-center mt-1.5">
          <div>
            {error && (
              <p id={errorId} role="alert" className="text-sm text-apple-red">
                {error}
              </p>
            )}
            {helperText && !error && (
              <p id={helperId} className="text-sm text-apple-text-secondary">
                {helperText}
              </p>
            )}
          </div>

          {showCount && maxLength && (
            <span className="text-sm text-apple-text-tertiary">
              {currentLength}/{maxLength}
            </span>
          )}
        </div>
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
