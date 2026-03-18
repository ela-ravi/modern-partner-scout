import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PipelineProgress } from './PipelineProgress'
import type { PipelineStage } from './PipelineProgress'

const mockStages: PipelineStage[] = [
  {
    id: 'analyzer',
    name: 'Brand Analyzer',
    status: 'completed',
    description: 'Extracted brand DNA from 2 reference profiles',
    progress: 100,
    stats: { hashtags: 4, keywords: 12 },
  },
  {
    id: 'discovery',
    name: 'Discovery Engine',
    status: 'active',
    description: 'Scanning Instagram for matching profiles',
    progress: 60,
    stats: { discovered: 23 },
  },
  {
    id: 'scoring',
    name: 'Scoring Agent',
    status: 'pending',
    description: 'Analyzing profiles against brand DNA',
    progress: 0,
    stats: { scored: 0, pending: 23 },
  },
  {
    id: 'email',
    name: 'Email Extractor',
    status: 'pending',
    description: 'Extracting contact emails from scored profiles',
    progress: 0,
  },
]

describe('PipelineProgress', () => {
  it('renders all 4 stages', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    expect(screen.getByText('Brand Analyzer')).toBeInTheDocument()
    expect(screen.getByText('Discovery Engine')).toBeInTheDocument()
    expect(screen.getByText('Scoring Agent')).toBeInTheDocument()
    expect(screen.getByText('Email Extractor')).toBeInTheDocument()
  })

  it('shows completed stages with checkmark', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    // Check for "Complete" badge
    expect(screen.getByText('Complete')).toBeInTheDocument()
  })

  it('shows active stage with "Running" status', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    expect(screen.getByText('Running')).toBeInTheDocument()
  })

  it('shows pending stages with muted styling', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    // There are 2 pending stages (scoring and email)
    const pendingBadges = screen.getAllByText('Pending')
    expect(pendingBadges.length).toBe(2)
  })

  it('renders overall progress bar with aria attributes', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    const progressBar = screen.getByRole('progressbar', { name: /overall progress/i })
    expect(progressBar).toHaveAttribute('aria-valuenow', '40')
    expect(progressBar).toHaveAttribute('aria-valuemin', '0')
    expect(progressBar).toHaveAttribute('aria-valuemax', '100')
  })

  it('displays stage descriptions', () => {
    render(<PipelineProgress stages={mockStages} overallProgress={40} />)

    expect(screen.getByText(/Extracted brand DNA/)).toBeInTheDocument()
    expect(screen.getByText(/Scanning Instagram/)).toBeInTheDocument()
  })

  it('handles failed status correctly', () => {
    const failedStages: PipelineStage[] = [
      { ...mockStages[0] },
      { ...mockStages[1], status: 'failed', error: 'Rate limit exceeded' },
      { ...mockStages[2] },
      { ...mockStages[3] },
    ]

    render(<PipelineProgress stages={failedStages} overallProgress={30} />)

    expect(screen.getByText('Failed')).toBeInTheDocument()
  })
})
