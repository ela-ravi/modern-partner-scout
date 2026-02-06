import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProfileDetail } from './ProfileDetail'
import { ToastProvider } from '@/components/ui/Toast'
import type { Profile } from '@/types/api/profile'

// Wrapper with providers
const renderWithProviders = (ui: React.ReactElement) => {
  return render(<ToastProvider>{ui}</ToastProvider>)
}

const mockProfile: Profile = {
  id: 'profile-1',
  job_id: 'job-1',
  username: 'testuser',
  full_name: 'Test User',
  bio: 'Recipe developer & wellness advocate 🥗',
  profile_pic_url: 'https://example.com/avatar.jpg',
  follower_count: 256000,
  following_count: 1200,
  post_count: 847,
  engagement_rate: 6.8,
  status: 'done',
  is_bookmarked: false,
  email: 'test@example.com',
  website: 'https://example.com',
  score: {
    overall_score: 96,
    engagement: 98,
    relevance: 95,
    authenticity: 92,
    reach: 97,
    reasoning: 'Excellent match for your brand',
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('ProfileDetail', () => {
  it('renders profile name and username', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText('@testuser')).toBeInTheDocument()
  })

  it('displays bio section', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    expect(screen.getByText(/recipe developer/i)).toBeInTheDocument()
  })

  it('shows follower stats', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    expect(screen.getByText('256K')).toBeInTheDocument()
    expect(screen.getByText('1.2K')).toBeInTheDocument()
    expect(screen.getByText('6.8%')).toBeInTheDocument()
    expect(screen.getByText('847')).toBeInTheDocument()
  })

  it('displays match score ring', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    const scoreRing = screen.getByRole('progressbar', { name: /match score/i })
    expect(scoreRing).toHaveAttribute('aria-valuenow', '96')
  })

  it('shows score breakdown', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    // Score breakdown should have progress bars with ARIA
    const progressBars = screen.getAllByRole('progressbar')
    expect(progressBars.length).toBeGreaterThan(1) // Main score ring + breakdown bars
  })

  it('displays email with copy button', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /copy email/i })).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn()
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={handleClose} />)

    fireEvent.click(screen.getByRole('button', { name: /close/i }))
    expect(handleClose).toHaveBeenCalled()
  })

  it('calls onEmail when email button is clicked', () => {
    const handleEmail = vi.fn()
    renderWithProviders(
      <ProfileDetail profile={mockProfile} isOpen onClose={() => {}} onEmail={handleEmail} />
    )

    fireEvent.click(screen.getByRole('button', { name: /compose email/i }))
    expect(handleEmail).toHaveBeenCalledWith(mockProfile)
  })

  it('calls onBookmark when bookmark button is clicked', () => {
    const handleBookmark = vi.fn()
    renderWithProviders(
      <ProfileDetail profile={mockProfile} isOpen onClose={() => {}} onBookmark={handleBookmark} />
    )

    fireEvent.click(screen.getByRole('button', { name: /save/i }))
    expect(handleBookmark).toHaveBeenCalledWith(mockProfile)
  })

  it('calls onSkip when skip button is clicked', () => {
    const handleSkip = vi.fn()
    renderWithProviders(
      <ProfileDetail profile={mockProfile} isOpen onClose={() => {}} onSkip={handleSkip} />
    )

    fireEvent.click(screen.getByRole('button', { name: /skip/i }))
    expect(handleSkip).toHaveBeenCalledWith(mockProfile)
  })

  it('shows bookmarked state correctly', () => {
    const bookmarkedProfile = { ...mockProfile, is_bookmarked: true }
    renderWithProviders(<ProfileDetail profile={bookmarkedProfile} isOpen onClose={() => {}} />)

    expect(screen.getByRole('button', { name: /saved/i })).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen={false} onClose={() => {}} />)

    expect(screen.queryByText('Test User')).not.toBeInTheDocument()
  })

  it('displays AI analysis reasoning', () => {
    renderWithProviders(<ProfileDetail profile={mockProfile} isOpen onClose={() => {}} />)

    expect(screen.getByText(/excellent match for your brand/i)).toBeInTheDocument()
  })
})
