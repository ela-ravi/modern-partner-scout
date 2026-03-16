import { useState, useRef, useId, useCallback, type KeyboardEvent, type ChangeEvent, type ClipboardEvent } from 'react'
import { cn } from '@/lib/utils'
import CloseIcon from '@mui/icons-material/Close'

export interface TagInputProps {
  /** Current tags */
  value?: string[]
  /** Called when tags change */
  onChange?: (tags: string[]) => void
  /** Placeholder text */
  placeholder?: string
  /** Maximum number of tags */
  maxTags?: number
  /** Validation function for tags */
  validate?: (tag: string) => boolean | string
  /** Prefix to auto-prepend to pasted items (e.g. "#" for hashtags) */
  prefix?: string
  /** Label for the input */
  label?: string
  /** Helper text */
  helperText?: string
  /** Error message */
  error?: string
  /** Whether the input is disabled */
  disabled?: boolean
  /** Additional class names */
  className?: string
}

export function TagInput({
  value = [],
  onChange,
  placeholder = 'Type and press Enter',
  maxTags,
  validate,
  prefix,
  label,
  helperText,
  error,
  disabled = false,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const liveRegionRef = useRef<HTMLDivElement>(null)
  const uniqueId = useId()
  const inputId = `tag-input-${uniqueId}`
  const descriptionId = `tag-input-desc-${uniqueId}`
  const errorId = `tag-input-error-${uniqueId}`

  const announceToScreenReader = useCallback((message: string) => {
    if (liveRegionRef.current) {
      liveRegionRef.current.textContent = message
      // Clear after announcement
      setTimeout(() => {
        if (liveRegionRef.current) {
          liveRegionRef.current.textContent = ''
        }
      }, 1000)
    }
  }, [])

  const addTag = useCallback((tag: string) => {
    const trimmedTag = tag.trim()
    
    if (!trimmedTag) return
    
    // Check for duplicates
    if (value.includes(trimmedTag)) {
      setValidationError('Tag already exists')
      return
    }
    
    // Check max tags
    if (maxTags && value.length >= maxTags) {
      setValidationError(`Maximum ${maxTags} tags allowed`)
      return
    }
    
    // Validate tag
    if (validate) {
      const result = validate(trimmedTag)
      if (result !== true) {
        setValidationError(typeof result === 'string' ? result : 'Invalid tag')
        return
      }
    }
    
    setValidationError(null)
    onChange?.([...value, trimmedTag])
    setInputValue('')
    announceToScreenReader(`${trimmedTag} added`)
  }, [value, onChange, maxTags, validate, announceToScreenReader])

  const removeTag = useCallback((indexToRemove: number) => {
    const tagToRemove = value[indexToRemove]
    const newTags = value.filter((_, index) => index !== indexToRemove)
    onChange?.(newTags)
    announceToScreenReader(`${tagToRemove} removed`)
    inputRef.current?.focus()
  }, [value, onChange, announceToScreenReader])

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addTag(inputValue)
    } else if (e.key === 'Backspace' && inputValue === '' && value.length > 0) {
      removeTag(value.length - 1)
    }
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value)
    setValidationError(null)
  }

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    const text = e.clipboardData.getData('text')
    // Split on newlines, commas, or semicolons
    const items = text.split(/[\n\r,;]+/).map(s => s.trim()).filter(Boolean)
    if (items.length === 0) return

    e.preventDefault()
    const newTags = [...value]
    let added = 0
    for (const raw of items) {
      if (maxTags && newTags.length >= maxTags) break
      // Auto-prepend prefix (e.g. "#" for hashtags) if not already present
      let tag = raw
      if (prefix && !tag.startsWith(prefix)) {
        tag = `${prefix}${tag}`
      }
      if (!newTags.includes(tag) && tag.trim()) {
        // Skip items that fail validation during bulk paste
        if (validate) {
          const result = validate(tag)
          if (result !== true) continue
        }
        newTags.push(tag)
        added++
      }
    }
    if (added > 0) {
      onChange?.(newTags)
      setInputValue('')
      setValidationError(null)
      announceToScreenReader(`${added} tag${added > 1 ? 's' : ''} added`)
    }
  }

  const displayError = error || validationError
  const hasError = !!displayError

  return (
    <div className={cn('space-y-1.5', className)}>
      {/* Label */}
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-apple-text"
        >
          {label}
        </label>
      )}

      {/* Tag container */}
      {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events */}
      <div
        className={cn(
          'flex flex-wrap gap-2 p-3 rounded-xl border bg-white transition-all duration-200',
          'focus-within:border-apple-blue focus-within:ring-2 focus-within:ring-apple-blue/20',
          hasError ? 'border-apple-red' : 'border-apple-border',
          disabled && 'bg-gray-50 cursor-not-allowed'
        )}
        onClick={() => inputRef.current?.focus()}
      >
        {/* Tags */}
        {value.map((tag, index) => (
          <span
            key={`${tag}-${index}`}
            className={cn(
              'inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-sm',
              'bg-apple-blue/10 text-apple-blue'
            )}
          >
            {tag}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                removeTag(index)
              }}
              disabled={disabled}
              className={cn(
                'w-5 h-5 inline-flex items-center justify-center rounded-full',
                'hover:bg-apple-blue/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue',
                'transition-colors'
              )}
              aria-label={`Remove ${tag}`}
            >
              <CloseIcon className="w-3.5 h-3.5" />
            </button>
          </span>
        ))}

        {/* Input */}
        <input
          ref={inputRef}
          id={inputId}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder={value.length === 0 ? placeholder : ''}
          disabled={disabled}
          aria-describedby={cn(
            helperText && descriptionId,
            hasError && errorId
          )}
          aria-invalid={hasError}
          className={cn(
            'flex-1 min-w-[120px] outline-none text-sm bg-transparent',
            'placeholder:text-apple-text-tertiary',
            disabled && 'cursor-not-allowed'
          )}
        />
      </div>

      {/* Helper text */}
      {helperText && !hasError && (
        <p id={descriptionId} className="text-sm text-apple-text-secondary">
          {helperText}
        </p>
      )}

      {/* Error message */}
      {hasError && (
        <p id={errorId} className="text-sm text-apple-red" role="alert">
          {displayError}
        </p>
      )}

      {/* Live region for screen reader announcements */}
      <div
        ref={liveRegionRef}
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />
    </div>
  )
}
