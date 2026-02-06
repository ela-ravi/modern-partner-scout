/**
 * Shadow Design Tokens
 */

export const ShadowToken = {
  card: '0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1)',
  cardHover: '0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1)',
  modal: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  soft: '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
  medium: '0 4px 20px -2px rgba(0, 0, 0, 0.1), 0 12px 25px -5px rgba(0, 0, 0, 0.05)',
  large: '0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 20px 50px -15px rgba(0, 0, 0, 0.1)',
  dropdown: '0 10px 40px -5px rgba(0, 0, 0, 0.1), 0 0 1px rgba(0, 0, 0, 0.1)',
} as const

export type ShadowTokenKey = keyof typeof ShadowToken
