import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatsGrid } from './StatsGrid'
import type { JobAnalytics } from '@/types/api/profile'

const mockAnalytics: JobAnalytics = {
  job_id: 'job-1',
  total_profiles: 42,
  new_profiles: 7,
  processing_profiles: 5,
  done_profiles: 25,
  skipped_profiles: 5,
  avg_score: 72.5,
  max_score: 95,
  min_score: 30,
  profiles_with_email: 28,
}

describe('StatsGrid', () => {
  it('renders all stat cards with correct values', () => {
    render(<StatsGrid analytics={mockAnalytics} />)

    expect(screen.getByText('Discovered')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()

    expect(screen.getByText('Scored')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()

    expect(screen.getByText('Emails Found')).toBeInTheDocument()
    expect(screen.getByText('28')).toBeInTheDocument()

    expect(screen.getByText('Avg Score')).toBeInTheDocument()
    expect(screen.getByText('73%')).toBeInTheDocument() // Rounded
  })

  it('rounds average score to nearest integer', () => {
    const analyticsWithDecimal = { ...mockAnalytics, avg_score: 82.7 }
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
