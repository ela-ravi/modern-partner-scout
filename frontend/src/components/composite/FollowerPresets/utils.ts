export type PresetType = 'nano' | 'micro' | 'mid-tier' | 'macro'

export const PRESETS: { id: PresetType; label: string; min: number; max: number }[] = [
  { id: 'nano', label: 'Nano (1K-10K)', min: 1000, max: 10000 },
  { id: 'micro', label: 'Micro (10K-100K)', min: 10000, max: 100000 },
  { id: 'mid-tier', label: 'Mid-tier (100K-500K)', min: 100000, max: 500000 },
  { id: 'macro', label: 'Macro (500K+)', min: 500000, max: 10000000 },
]

/**
 * Helper to determine which preset matches given min/max values
 */
export function getActivePreset(min: number, max: number): PresetType | undefined {
  const preset = PRESETS.find((p) => p.min === min && p.max === max)
  return preset?.id
}
