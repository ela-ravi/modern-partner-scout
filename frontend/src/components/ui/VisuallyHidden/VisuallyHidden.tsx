import type { ReactNode } from 'react'

export interface VisuallyHiddenProps {
  /** Content to be hidden visually but accessible to screen readers */
  children: ReactNode
  /** Render as a specific element */
  as?: 'span' | 'div' | 'p' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
}

/**
 * Hides content visually but keeps it accessible to screen readers.
 * Useful for providing context that is only needed by assistive technology.
 */
export function VisuallyHidden({ children, as: Component = 'span' }: VisuallyHiddenProps) {
  return (
    <Component
      style={{
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: 0,
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        borderWidth: 0,
      }}
    >
      {children}
    </Component>
  )
}
