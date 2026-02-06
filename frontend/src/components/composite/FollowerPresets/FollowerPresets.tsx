import { cn } from '@/lib/utils'
import { PRESETS, type PresetType } from './utils'

export interface FollowerPresetsProps {
  /** Called when a preset is selected with min and max values */
  onSelect: (min: number, max: number) => void
  /** Currently active preset (if any) */
  activePreset?: PresetType
  /** Additional class names */
  className?: string
}

export function FollowerPresets({ onSelect, activePreset, className }: FollowerPresetsProps) {
  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {PRESETS.map((preset) => {
        const isActive = activePreset === preset.id

        return (
          <button
            key={preset.id}
            type="button"
            onClick={() => onSelect(preset.min, preset.max)}
            data-active={isActive ? 'true' : 'false'}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium',
              'border transition-all duration-200',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2',
              isActive
                ? 'bg-apple-blue/10 border-apple-blue text-apple-blue'
                : 'bg-white border-apple-border text-apple-text-secondary hover:border-apple-blue hover:text-apple-blue'
            )}
          >
            {preset.label}
          </button>
        )
      })}
    </div>
  )
}
