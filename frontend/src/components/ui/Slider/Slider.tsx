import { useId } from 'react'
import * as RadixSlider from '@radix-ui/react-slider'
import { cn } from '@/lib/utils'

export interface SliderProps {
  /** Current value(s) */
  value?: number[]
  /** Default value(s) */
  defaultValue?: number[]
  /** Called when value changes */
  onValueChange?: (value: number[]) => void
  /** Minimum value */
  min?: number
  /** Maximum value */
  max?: number
  /** Step increment */
  step?: number
  /** Label for the slider */
  label?: string
  /** Whether to show the current value */
  showValue?: boolean
  /** Format function for the value display */
  formatValue?: (value: number) => string
  /** Helper text */
  helperText?: string
  /** Whether the slider is disabled */
  disabled?: boolean
  /** Additional class names */
  className?: string
  /** Aria label when no visible label */
  'aria-label'?: string
}

export function Slider({
  value,
  defaultValue = [50],
  onValueChange,
  min = 0,
  max = 100,
  step = 1,
  label,
  showValue = true,
  formatValue = (v) => String(v),
  helperText,
  disabled = false,
  className,
  'aria-label': ariaLabel,
}: SliderProps) {
  const uniqueId = useId()
  const labelId = `slider-label-${uniqueId}`
  const descriptionId = `slider-desc-${uniqueId}`

  const currentValue = value || defaultValue
  const displayValue = currentValue.length === 2
    ? `${formatValue(currentValue[0])} - ${formatValue(currentValue[1])}`
    : formatValue(currentValue[0])

  return (
    <div className={cn('space-y-3', className)}>
      {/* Label and value */}
      {(label || showValue) && (
        <div className="flex items-center justify-between">
          {label && (
            <label
              id={labelId}
              className="text-sm font-medium text-apple-text"
            >
              {label}
            </label>
          )}
          {showValue && (
            <span className="text-sm font-medium text-apple-blue tabular-nums">
              {displayValue}
            </span>
          )}
        </div>
      )}

      {/* Slider */}
      <RadixSlider.Root
        value={value}
        defaultValue={defaultValue}
        onValueChange={onValueChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        aria-labelledby={label ? labelId : undefined}
        aria-label={!label ? ariaLabel : undefined}
        aria-describedby={helperText ? descriptionId : undefined}
        className={cn(
          'relative flex items-center select-none touch-none w-full h-5',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Track */}
        <RadixSlider.Track
          className={cn(
            'relative grow rounded-full h-2 bg-apple-border',
            'overflow-hidden'
          )}
        >
          <RadixSlider.Range
            className={cn(
              'absolute h-full rounded-full',
              'bg-apple-blue'
            )}
          />
        </RadixSlider.Track>

        {/* Thumbs */}
        {currentValue.map((_, index) => (
          <RadixSlider.Thumb
            key={index}
            className={cn(
              'block w-5 h-5 rounded-full bg-white shadow-lg',
              'border-2 border-apple-blue',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2',
              'hover:scale-110 transition-transform duration-200',
              disabled && 'cursor-not-allowed'
            )}
          />
        ))}
      </RadixSlider.Root>

      {/* Min/Max labels */}
      <div className="flex justify-between text-xs text-apple-text-tertiary">
        <span>{formatValue(min)}</span>
        <span>{formatValue(max)}</span>
      </div>

      {/* Helper text */}
      {helperText && (
        <p id={descriptionId} className="text-sm text-apple-text-secondary">
          {helperText}
        </p>
      )}
    </div>
  )
}
