import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProfileCard } from './ProfileCard'
import type { Profile } from '@/types/api/profile'

const mockProfile: Profile = {
  id: 'profile-1',
  job_id: 'job-1',
  username: 'testuser',
  full_name: 'Test User',
  profile_pic_url: 'https://example.com/avatar.jpg',
  follower_count: 15000,
  following_count: 500,
  post_count: 120,
  engagement_rate: 4.5,
  status: 'done',
  is_bookmarked: false,
  email: 'test@example.com',
  score: {
    overall_score: 85,
    engagement: 90,
    relevance: 85,
    authenticity: 80,
    reach: 85,
    reasoning: 'Great match for your brand',
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('ProfileCard', () => {
  it('renders profile information correctly', () => {
    render(<ProfileCard profile={mockProfile} />)

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText('@testuser')).toBeInTheDocument()
    expect(screen.getByText('15.0K')).toBeInTheDocument()
    expect(screen.getByText('4.5%')).toBeInTheDocument()
  })

  it('renders avatar with descriptive alt text', () => {
    render(<ProfileCard profile={mockProfile} />)

    const avatar = screen.getByRole('img', { name: /profile photo of test user/i })
    expect(avatar).toBeInTheDocument()
  })

  it('renders status badge', () => {
    render(<ProfileCard profile={mockProfile} />)

    expect(screen.getByText('Scored')).toBeInTheDocument()
  })

  it('renders email badge when profile has email', () => {
    render(<ProfileCard profile={mockProfile} />)

    expect(screen.getByText('📧 Email')).toBeInTheDocument()
  })

  it('does not render email badge when profile has no email', () => {
    const profileWithoutEmail = { ...mockProfile, email: undefined }
    render(<ProfileCard profile={profileWithoutEmail} />)

    expect(screen.queryByText('📧 Email')).not.toBeInTheDocument()
  })

  it('renders score ring with correct score', () => {
    render(<ProfileCard profile={mockProfile} />)

    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '85')
  })

  it('calls onView when view button is clicked', () => {
    const handleView = vi.fn()
    render(<ProfileCard profile={mockProfile} onView={handleView} />)

    fireEvent.click(screen.getByRole('button', { name: /view profile for test user/i }))
    expect(handleView).toHaveBeenCalledWith(mockProfile)
  })

  it('calls onEmail when email button is clicked', () => {
    const handleEmail = vi.fn()
    render(<ProfileCard profile={mockProfile} onEmail={handleEmail} />)

    fireEvent.click(screen.getByRole('button', { name: /email test user/i }))
    expect(handleEmail).toHaveBeenCalledWith(mockProfile)
  })

  it('calls onBookmark when bookmark button is clicked', () => {
    const handleBookmark = vi.fn()
    render(<ProfileCard profile={mockProfile} onBookmark={handleBookmark} />)

    fireEvent.click(screen.getByRole('button', { name: /bookmark test user/i }))
    expect(handleBookmark).toHaveBeenCalledWith(mockProfile)
  })

  it('shows bookmarked state correctly', () => {
    const bookmarkedProfile = { ...mockProfile, is_bookmarked: true }
    render(<ProfileCard profile={bookmarkedProfile} />)

    expect(screen.getByRole('button', { name: /remove test user from bookmarks/i })).toBeInTheDocument()
  })

  it('has correct article structure with aria-labelledby', () => {
    render(<ProfileCard profile={mockProfile} />)

    const article = screen.getByRole('article')
    expect(article).toHaveAttribute('aria-labelledby', 'profile-name-profile-1')
  })

  it('formats large follower counts correctly', () => {
    const profileWithManyFollowers = { ...mockProfile, follower_count: 1500000 }
    render(<ProfileCard profile={profileWithManyFollowers} />)

    expect(screen.getByText('1.5M')).toBeInTheDocument()
  })

  it('renders NEW status correctly', () => {
    const newProfile = { ...mockProfile, status: 'new' as const }
    render(<ProfileCard profile={newProfile} />)

    expect(screen.getByText('NEW')).toBeInTheDocument()
  })

  it('renders processing status correctly', () => {
    const processingProfile = { ...mockProfile, status: 'processing' as const }
    render(<ProfileCard profile={processingProfile} />)

    expect(screen.getByText('Processing')).toBeInTheDocument()
  })
})
