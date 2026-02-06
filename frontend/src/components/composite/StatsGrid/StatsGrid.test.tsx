import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatsGrid } from './StatsGrid'
import type { JobAnalytics } from '@/types/api/profile'

const mockAnalytics: JobAnalytics = {
  total_discovered: 42,
  total_scored: 35,
  high_match_count: 15,
  emails_found: 28,
  average_score: 72.5,
  status_breakdown: {
    new: 7,
    processing: 5,
    done: 25,
    skipped: 5,
  },
}

describe('StatsGrid', () => {
  it('renders all stat cards with correct values', () => {
    render(<StatsGrid analytics={mockAnalytics} />)

    expect(screen.getByText('Discovered')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()

    expect(screen.getByText('High Match')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()

    expect(screen.getByText('Emails Found')).toBeInTheDocument()
    expect(screen.getByText('28')).toBeInTheDocument()

    expect(screen.getByText('Avg Score')).toBeInTheDocument()
    expect(screen.getByText('73%')).toBeInTheDocument() // Rounded
  })

  it('rounds average score to nearest integer', () => {
    const analyticsWithDecimal = { ...mockAnalytics, average_score: 82.7 }
    render(<StatsGrid analytics={analyticsWithDecimal} />)

    expect(screen.getByText('83%')).toBeInTheDocument()
  })

  it('shows skeleton loading state', () => {
    render(<StatsGrid analytics={mockAnalytics} isLoading />)

    // Should not show actual values
    expect(screen.queryByText('42')).not.toBeInTheDocument()
    expect(screen.queryByText('Discovered')).not.toBeInTheDocument()

    // Should show skeleton elements (via animate-pulse class on parent)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('applies custom className', () => {
    const { container } = render(
      <StatsGrid analytics={mockAnalytics} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('displays grid with 4 columns on large screens', () => {
    const { container } = render(<StatsGrid analytics={mockAnalytics} />)

    expect(container.firstChild).toHaveClass('lg:grid-cols-4')
  })

  it('displays grid with 2 columns on smaller screens', () => {
    const { container } = render(<StatsGrid analytics={mockAnalytics} />)

    expect(container.firstChild).toHaveClass('grid-cols-2')
  })
})
