import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreRing } from './ScoreRing'

describe('ScoreRing', () => {
  it('renders with correct aria attributes', () => {
    render(<ScoreRing score={85} />)

    const progressbar = screen.getByRole('progressbar')
    expect(progressbar).toHaveAttribute('aria-valuenow', '85')
    expect(progressbar).toHaveAttribute('aria-valuemin', '0')
    expect(progressbar).toHaveAttribute('aria-valuemax', '100')
  })

  it('has accessible label for screen readers', () => {
    render(<ScoreRing score={85} />)

    const progressbar = screen.getByRole('progressbar')
    expect(progressbar).toHaveAttribute('aria-label', 'Match score: 85 out of 100')
  })

  it('displays score value in center by default', () => {
    render(<ScoreRing score={75} />)

    expect(screen.getByText('75')).toBeInTheDocument()
  })

  it('hides score value when showValue is false', () => {
    render(<ScoreRing score={75} showValue={false} />)

    expect(screen.queryByText('75')).not.toBeInTheDocument()
  })

  it('clamps score to 0-100 range', () => {
    const { rerender } = render(<ScoreRing score={150} />)
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100')

    rerender(<ScoreRing score={-10} />)
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
  })

  it('uses green color for high scores (80+)', () => {
    render(<ScoreRing score={85} />)

    const valueText = screen.getByText('85')
    // Green is applied to high scores
    expect(valueText).toHaveStyle({ color: 'var(--color-apple-green, #34c759)' })
  })

  it('uses blue color for medium-high scores (60-79)', () => {
    render(<ScoreRing score={70} />)

    const valueText = screen.getByText('70')
    expect(valueText).toHaveStyle({ color: 'var(--color-apple-blue, #0071e3)' })
  })

  it('uses orange color for medium-low scores (40-59)', () => {
    render(<ScoreRing score={50} />)

    const valueText = screen.getByText('50')
    expect(valueText).toHaveStyle({ color: 'var(--color-apple-orange, #ff9500)' })
  })

  it('uses red color for low scores (<40)', () => {
    render(<ScoreRing score={30} />)

    const valueText = screen.getByText('30')
    expect(valueText).toHaveStyle({ color: 'var(--color-apple-red, #ff3b30)' })
  })

  it('renders SVG with correct size', () => {
    render(<ScoreRing score={50} size={100} />)

    const svg = document.querySelector('svg')
    expect(svg).toHaveAttribute('width', '100')
    expect(svg).toHaveAttribute('height', '100')
  })

  it('applies custom className', () => {
    render(<ScoreRing score={50} className="custom-class" />)

    const progressbar = screen.getByRole('progressbar')
    expect(progressbar).toHaveClass('custom-class')
  })
})
