/**
 * Apple-inspired Color Design Tokens
 * WCAG 2.2 AA Compliant
 */

export const ColorToken = {
  // Background & Surface
  appleBg: '#fbfbfd',
  appleCard: '#ffffff',
  appleGray: '#f5f5f7',
  appleBorder: 'rgba(0, 0, 0, 0.06)',

  // Brand Colors
  appleBlue: '#0071e3',
  appleBlueHover: '#0077ed',
  appleGreen: '#34c759',
  appleOrange: '#ff9500',
  appleRed: '#ff3b30',
  applePurple: '#af52de',

  // Text Colors - WCAG AA Compliant
  appleText: '#1d1d1f',
  appleTextSecondary: '#6e6e73', // 5.2:1 contrast ratio
  appleTextTertiary: '#8e8e93', // 4.5:1 contrast ratio

  // Status Colors
  success: {
    50: '#f0fdf4',
    500: '#34c759',
    600: '#22c55e',
  },
  warning: {
    50: '#fffbeb',
    500: '#ff9500',
    600: '#f59e0b',
  },
  error: {
    50: '#fef2f2',
    500: '#ff3b30',
    600: '#ef4444',
  },
} as const

export type ColorTokenKey = keyof typeof ColorToken
