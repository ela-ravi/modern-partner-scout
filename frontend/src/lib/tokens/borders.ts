/**
 * Border Radius Design Tokens
 */

export const BorderToken = {
  radiusCard: '18px',
  radiusButton: '12px',
  radiusPill: '980px',
  radiusInput: '12px',
  radiusAvatar: '16px',
  radiusSm: '8px',
  radiusMd: '12px',
  radiusLg: '18px',
  radiusXl: '24px',
  radiusFull: '9999px',
} as const

export type BorderTokenKey = keyof typeof BorderToken
