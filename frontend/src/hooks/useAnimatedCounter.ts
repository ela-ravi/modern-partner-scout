import { useEffect, useRef, useState, useMemo } from 'react'

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

function getReducedMotion(): boolean {
  return typeof window !== 'undefined'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Animated number counter that triggers when the element enters the viewport.
 * Returns a ref to attach to the container and the current display value.
 */
export function useAnimatedCounter(
  end: number,
  duration = 2000,
  prefix = '',
  suffix = ''
): { ref: React.RefObject<HTMLSpanElement | null>; display: string } {
  const reducedMotion = useMemo(() => getReducedMotion(), [])
  const ref = useRef<HTMLSpanElement>(null)
  const [display, setDisplay] = useState(
    reducedMotion ? `${prefix}${end.toLocaleString()}${suffix}` : `${prefix}0${suffix}`
  )
  const hasAnimated = useRef(reducedMotion)

  useEffect(() => {
    const el = ref.current
    if (!el || hasAnimated.current) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          hasAnimated.current = true
          observer.disconnect()

          let start: number | null = null
          function step(timestamp: number) {
            if (start === null) start = timestamp
            const elapsed = timestamp - start
            const progress = Math.min(elapsed / duration, 1)
            const easedProgress = easeOutCubic(progress)
            const current = Math.round(easedProgress * end)
            setDisplay(`${prefix}${current.toLocaleString()}${suffix}`)

            if (progress < 1) {
              requestAnimationFrame(step)
            }
          }

          requestAnimationFrame(step)
        }
      },
      { threshold: 0.3 }
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [end, duration, prefix, suffix])

  return { ref, display }
}
