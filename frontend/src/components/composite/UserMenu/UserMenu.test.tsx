import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UserMenu } from './UserMenu'
import * as AuthContext from '@/contexts/AuthContext'

// Mock the useAuth hook
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

const mockSignOut = vi.fn()
const mockUseAuth = vi.mocked(AuthContext.useAuth)

describe('UserMenu', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    mockUseAuth.mockReturnValue({
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      user: { id: 'user-123', email: 'test@example.com' } as any,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      session: {} as any,
      isLoading: false,
      isAuthenticated: true,
      signIn: vi.fn(),
      signUp: vi.fn(),
      signOut: mockSignOut,
    })
  })

  it('renders user initials', () => {
    render(<UserMenu />)

    expect(screen.getByRole('button', { name: /user menu/i })).toHaveTextContent('TE')
  })

  it('opens dropdown on click', async () => {
    const user = userEvent.setup()
    render(<UserMenu />)

    await user.click(screen.getByRole('button', { name: /user menu/i }))

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })
  })

  it('shows menu items when open', async () => {
    const user = userEvent.setup()
    render(<UserMenu />)

    await user.click(screen.getByRole('button', { name: /user menu/i }))

    await waitFor(() => {
      expect(screen.getByText('Profile')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
      expect(screen.getByText('Sign Out')).toBeInTheDocument()
    })
  })

  it('calls signOut when Sign Out is clicked', async () => {
    mockSignOut.mockResolvedValue(undefined)
    const user = userEvent.setup()
    render(<UserMenu />)

    await user.click(screen.getByRole('button', { name: /user menu/i }))

    await waitFor(() => {
      expect(screen.getByText('Sign Out')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Sign Out'))

    await waitFor(() => {
      expect(mockSignOut).toHaveBeenCalled()
    })
  })

  it('has proper aria-label for accessibility', () => {
    render(<UserMenu />)

    expect(screen.getByRole('button')).toHaveAttribute(
      'aria-label',
      'User menu for test@example.com'
    )
  })

  it('can be navigated with keyboard', async () => {
    const user = userEvent.setup()
    render(<UserMenu />)

    // Focus and open with Enter
    const trigger = screen.getByRole('button', { name: /user menu/i })
    trigger.focus()
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(screen.getByText('Profile')).toBeInTheDocument()
    })

    // Navigate with arrow keys
    await user.keyboard('{ArrowDown}')
    await user.keyboard('{ArrowDown}')
    await user.keyboard('{ArrowDown}')

    // Close with Escape
    await user.keyboard('{Escape}')

    await waitFor(() => {
      expect(screen.queryByText('Profile')).not.toBeInTheDocument()
    })
  })
})
