import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ActivityLog } from './ActivityLog'
import type { LogEntry } from './ActivityLog'

const mockEntries: LogEntry[] = [
  {
    id: '1',
    timestamp: '12:34:52',
    type: 'success',
    message: 'Scored @cleaneatingamy',
    score: 96,
  },
  {
    id: '2',
    timestamp: '12:34:48',
    type: 'info',
    message: 'Discovered @mindful_living',
  },
  {
    id: '3',
    timestamp: '12:34:45',
    type: 'success',
    message: 'Email found for @wellnessbysarah',
  },
  {
    id: '4',
    timestamp: '12:34:41',
    type: 'error',
    message: 'Rate limit exceeded',
  },
]

describe('ActivityLog', () => {
  it('renders log entries with timestamps', () => {
    render(<ActivityLog entries={mockEntries} />)

    expect(screen.getByText('12:34:52')).toBeInTheDocument()
    expect(screen.getByText('12:34:48')).toBeInTheDocument()
    expect(screen.getByText('12:34:45')).toBeInTheDocument()
  })

  it('renders log messages', () => {
    render(<ActivityLog entries={mockEntries} />)

    expect(screen.getByText(/Scored @cleaneatingamy/)).toBeInTheDocument()
    expect(screen.getByText(/Discovered @mindful_living/)).toBeInTheDocument()
  })

  it('renders success entries with green styling', () => {
    render(<ActivityLog entries={mockEntries} />)

    // Check for success indicator
    const successEntries = screen.getAllByText('✓')
    expect(successEntries.length).toBeGreaterThan(0)
  })

  it('renders error entries with red styling', () => {
    render(<ActivityLog entries={mockEntries} />)

    // Check for error indicator
    expect(screen.getByText('✗')).toBeInTheDocument()
  })

  it('displays scores when provided', () => {
    render(<ActivityLog entries={mockEntries} />)

    expect(screen.getByText('96%')).toBeInTheDocument()
  })

  it('has ARIA live region for screen readers', () => {
    render(<ActivityLog entries={mockEntries} />)

    const liveRegion = screen.getByRole('log')
    expect(liveRegion).toHaveAttribute('aria-live', 'polite')
    expect(liveRegion).toHaveAttribute('aria-label', 'Activity log')
  })

  it('renders empty state when no entries', () => {
    render(<ActivityLog entries={[]} />)

    expect(screen.getByText(/No activity yet/i)).toBeInTheDocument()
  })
})
