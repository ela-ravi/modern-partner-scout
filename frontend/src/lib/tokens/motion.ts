/**
 * Animation & Motion Design Tokens
 */

export const MotionToken = {
  // Animation keyframes (match CSS @keyframes)
  fadeIn: 'fadeIn 0.6s ease-out forwards',
  slideUp: 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
  scaleIn: 'scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
  slideDown: 'slideDown 0.3s ease-out forwards',

  // Easing functions
  easeOut: 'cubic-bezier(0.16, 1, 0.3, 1)',
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',

  // Durations
  fast: '150ms',
  normal: '200ms',
  slow: '300ms',
  verySlow: '600ms',
} as const

export type MotionTokenKey = keyof typeof MotionToken
