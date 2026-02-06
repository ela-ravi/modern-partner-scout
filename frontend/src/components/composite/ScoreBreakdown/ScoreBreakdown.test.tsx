import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreBreakdown } from './ScoreBreakdown'
import type { ProfileScore } from '@/types/api/profile'

const mockScore: ProfileScore = {
  overall_score: 85,
  engagement: 92,
  relevance: 88,
  authenticity: 85,
  reach: 78,
  content_quality: 90,
  brand_alignment: 86,
}

describe('ScoreBreakdown', () => {
  it('renders all score dimensions', () => {
    render(<ScoreBreakdown score={mockScore} />)

    expect(screen.getByText(/engagement/i)).toBeInTheDocument()
    expect(screen.getByText(/relevance/i)).toBeInTheDocument()
    expect(screen.getByText(/authenticity/i)).toBeInTheDocument()
    expect(screen.getByText(/reach/i)).toBeInTheDocument()
  })

  it('displays score percentages', () => {
    render(<ScoreBreakdown score={mockScore} />)

    expect(screen.getByText('92%')).toBeInTheDocument()
    expect(screen.getByText('88%')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('78%')).toBeInTheDocument()
  })

  it('renders progress bars with correct ARIA attributes', () => {
    render(<ScoreBreakdown score={mockScore} />)

    const progressBars = screen.getAllByRole('progressbar')
    expect(progressBars.length).toBeGreaterThan(0)

    // Check first progress bar has correct attributes
    const firstBar = progressBars[0]
    expect(firstBar).toHaveAttribute('aria-valuemin', '0')
    expect(firstBar).toHaveAttribute('aria-valuemax', '100')
    expect(firstBar).toHaveAttribute('aria-valuenow')
  })

  it('has accessible labels for screen readers', () => {
    render(<ScoreBreakdown score={mockScore} />)

    const progressBars = screen.getAllByRole('progressbar')
    progressBars.forEach((bar) => {
      expect(bar).toHaveAttribute('aria-label')
    })
  })

  it('renders correct number of dimensions', () => {
    render(<ScoreBreakdown score={mockScore} />)

    // Should show engagement, relevance, authenticity, reach, content_quality, brand_alignment
    const progressBars = screen.getAllByRole('progressbar')
    expect(progressBars.length).toBe(6)
  })

  it('handles partial score data gracefully', () => {
    const partialScore: ProfileScore = {
      overall_score: 75,
      engagement: 80,
    }
    render(<ScoreBreakdown score={partialScore} />)

    // Should only show engagement dimension
    expect(screen.getByText(/engagement/i)).toBeInTheDocument()
    expect(screen.queryByText(/relevance/i)).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <ScoreBreakdown score={mockScore} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })
})
