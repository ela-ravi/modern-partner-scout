import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProfileGrid } from './ProfileGrid'
import type { Profile } from '@/types/api/profile'

const mockProfiles: Profile[] = [
  {
    id: 'profile-1',
    job_id: 'job-1',
    username: 'user1',
    full_name: 'User One',
    profile_pic_url: 'https://example.com/1.jpg',
    follower_count: 10000,
    following_count: 500,
    post_count: 100,
    engagement_rate: 4.5,
    status: 'done',
    is_bookmarked: false,
    score: {
      overall_score: 85,
      engagement: 90,
      relevance: 85,
      authenticity: 80,
      reach: 85,
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'profile-2',
    job_id: 'job-1',
    username: 'user2',
    full_name: 'User Two',
    profile_pic_url: 'https://example.com/2.jpg',
    follower_count: 25000,
    following_count: 800,
    post_count: 200,
    engagement_rate: 3.2,
    status: 'new',
    is_bookmarked: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

describe('ProfileGrid', () => {
  it('renders profile cards for each profile', () => {
    render(<ProfileGrid profiles={mockProfiles} />)

    expect(screen.getByText('User One')).toBeInTheDocument()
    expect(screen.getByText('User Two')).toBeInTheDocument()
  })

  it('shows empty state when no profiles', () => {
    render(<ProfileGrid profiles={[]} />)

    expect(screen.getByText('No profiles found')).toBeInTheDocument()
    expect(screen.getByText(/try adjusting your filters/i)).toBeInTheDocument()
  })

  it('shows loading skeleton state', () => {
    render(<ProfileGrid profiles={[]} isLoading />)

    // Should not show empty state when loading
    expect(screen.queryByText('No profiles found')).not.toBeInTheDocument()

    // Should show skeleton cards
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('shows Load More button when hasMore is true', () => {
    render(<ProfileGrid profiles={mockProfiles} hasMore />)

    expect(screen.getByRole('button', { name: /load more/i })).toBeInTheDocument()
  })

  it('hides Load More button when hasMore is false', () => {
    render(<ProfileGrid profiles={mockProfiles} hasMore={false} />)

    expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument()
  })

  it('calls onLoadMore when Load More is clicked', () => {
    const handleLoadMore = vi.fn()
    render(<ProfileGrid profiles={mockProfiles} hasMore onLoadMore={handleLoadMore} />)

    fireEvent.click(screen.getByRole('button', { name: /load more/i }))
    expect(handleLoadMore).toHaveBeenCalledTimes(1)
  })

  it('shows loading state on Load More button when isLoadingMore', () => {
    render(<ProfileGrid profiles={mockProfiles} hasMore isLoadingMore />)

    const loadMoreButton = screen.getByRole('button', { name: /load more/i })
    // Button should be disabled when loading
    expect(loadMoreButton).toHaveAttribute('aria-disabled', 'true')
  })

  it('passes action handlers to profile cards', () => {
    const handleView = vi.fn()
    const handleEmail = vi.fn()
    const handleBookmark = vi.fn()

    render(
      <ProfileGrid
        profiles={mockProfiles}
        onView={handleView}
        onEmail={handleEmail}
        onBookmark={handleBookmark}
      />
    )

    // Click view on first profile
    fireEvent.click(screen.getByRole('button', { name: /view profile for user one/i }))
    expect(handleView).toHaveBeenCalledWith(mockProfiles[0])

    // Click bookmark on first profile
    fireEvent.click(screen.getByRole('button', { name: /bookmark user one/i }))
    expect(handleBookmark).toHaveBeenCalledWith(mockProfiles[0])
  })

  it('applies responsive grid classes', () => {
    render(<ProfileGrid profiles={mockProfiles} />)

    const grid = document.querySelector('.grid')
    expect(grid).toHaveClass('grid-cols-1')
    expect(grid).toHaveClass('md:grid-cols-2')
    expect(grid).toHaveClass('lg:grid-cols-3')
  })

  it('applies custom className', () => {
    const { container } = render(
      <ProfileGrid profiles={mockProfiles} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })
})
