import { useEffect, useRef } from 'react'

/**
 * Scroll-reveal hook using IntersectionObserver.
 * Adds `data-revealed="true"` to elements with `.reveal-section` or `.reveal-item`
 * once they enter the viewport.
 */
export function useScrollReveal(rootMargin = '-60px') {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Respect reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) {
      container.querySelectorAll('.reveal-section, .reveal-item').forEach((el) => {
        el.setAttribute('data-revealed', 'true')
      })
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.setAttribute('data-revealed', 'true')
            observer.unobserve(entry.target)
          }
        })
      },
      { rootMargin, threshold: 0.1 }
    )

    const elements = container.querySelectorAll('.reveal-section, .reveal-item')
    elements.forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [rootMargin])

  return containerRef
}
