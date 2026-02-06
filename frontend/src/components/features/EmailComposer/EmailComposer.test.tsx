import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EmailComposer } from './EmailComposer'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock the email hooks
vi.mock('@/hooks/email', () => ({
  useEmailTones: vi.fn(() => ({
    data: [
      { id: 'professional', name: 'Professional', description: 'Formal business tone' },
      { id: 'friendly', name: 'Friendly', description: 'Casual and warm' },
      { id: 'enthusiastic', name: 'Enthusiastic', description: 'Excited and energetic' },
    ],
    isLoading: false,
  })),
  useGenerateEmail: vi.fn(() => ({
    mutate: vi.fn(),
    mutateAsync: vi.fn().mockResolvedValue({
      subject: 'Collaboration Opportunity',
      body: 'Hi there, I would love to collaborate...',
      recipient_email: 'test@example.com',
      recipient_name: 'Test User',
      tone_used: 'professional',
    }),
    isPending: false,
  })),
  useSendEmail: vi.fn(() => ({
    mutate: vi.fn(),
    mutateAsync: vi.fn().mockResolvedValue({ success: true }),
    isPending: false,
  })),
}))

const mockProfile = {
  profileId: 'profile-1',
  jobId: 'job-1',
  recipientName: 'Clean Eating Amy',
  recipientEmail: 'amy@example.com',
  recipientHandle: '@cleaneatingamy',
  profileImageUrl: 'https://example.com/avatar.jpg',
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

describe('EmailComposer', () => {
  const mockOnClose = vi.fn()
  const mockOnSent = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders modal with recipient info', () => {
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    expect(screen.getByText('Compose Email')).toBeInTheDocument()
    expect(screen.getByText('Clean Eating Amy')).toBeInTheDocument()
    expect(screen.getByText('amy@example.com')).toBeInTheDocument()
  })

  it('renders tone selector', () => {
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Friendly')).toBeInTheDocument()
    expect(screen.getByText('Enthusiastic')).toBeInTheDocument()
  })

  it('renders subject and body inputs', () => {
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    expect(screen.getByLabelText(/subject/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument()
  })

  it('renders generate and send buttons', () => {
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    expect(screen.getByRole('button', { name: /generate/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('allows user to edit subject and body', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    const subjectInput = screen.getByLabelText(/subject/i)
    const bodyInput = screen.getByLabelText(/message/i)

    await user.clear(subjectInput)
    await user.type(subjectInput, 'New Subject')
    await user.clear(bodyInput)
    await user.type(bodyInput, 'New body content')

    expect(subjectInput).toHaveValue('New Subject')
    expect(bodyInput).toHaveValue('New body content')
  })

  it('has proper accessibility attributes', () => {
    renderWithProviders(
      <EmailComposer
        isOpen={true}
        onClose={mockOnClose}
        profile={mockProfile}
        onSent={mockOnSent}
      />
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby')
  })
})
