import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import LoginPage from '../LoginPage'
import * as AuthContext from '@/contexts/AuthContext'
import * as ToastContext from '@/components/ui/Toast'

// Mock the hooks
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('@/components/ui/Toast', () => ({
  useToast: vi.fn(),
  ToastProvider: ({ children }: { children: React.ReactNode }) => children,
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ state: null }),
  }
})

const mockSignIn = vi.fn()
const mockSignUp = vi.fn()
const mockToast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn(),
  dismiss: vi.fn(),
  toasts: [],
}

const mockUseAuth = vi.mocked(AuthContext.useAuth)
const mockUseToast = vi.mocked(ToastContext.useToast)

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    mockUseAuth.mockReturnValue({
      user: null,
      session: null,
      isLoading: false,
      isAuthenticated: false,
      signIn: mockSignIn,
      signUp: mockSignUp,
      signOut: vi.fn(),
    })

    mockUseToast.mockReturnValue(mockToast)
  })

  describe('Login Form', () => {
    it('renders login form by default', () => {
      render(<LoginPage />)

      expect(screen.getByText('Sign in to your account')).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    it('does not call signIn with invalid email', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      // HTML5 email validation will prevent form submission
      await user.type(emailInput, 'invalid-email')
      await user.type(passwordInput, 'password123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))

      // signIn should not be called with invalid email
      expect(mockSignIn).not.toHaveBeenCalled()
    })

    it('shows validation error for short password', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, '123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))

      await waitFor(() => {
        expect(screen.getByText(/at least 6 characters/i)).toBeInTheDocument()
      })
    })

    it('calls signIn with valid credentials', async () => {
      mockSignIn.mockResolvedValue(undefined)
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123')
      })
    })

    it('shows error toast on login failure', async () => {
      mockSignIn.mockRejectedValue(new Error('Invalid credentials'))
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'wrongpassword')
      await user.click(screen.getByRole('button', { name: /sign in/i }))

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Invalid credentials')
      })
    })

    it('has autocomplete attributes for accessibility', () => {
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)

      expect(emailInput).toHaveAttribute('autocomplete', 'email')
      expect(passwordInput).toHaveAttribute('autocomplete', 'current-password')
    })
  })

  describe('Sign Up Form', () => {
    it('switches to sign up form when toggle is clicked', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      await user.click(screen.getByText(/don't have an account/i))

      expect(screen.getByText('Create an account')).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    })

    it('shows error when passwords do not match', async () => {
      const user = userEvent.setup({ delay: null })
      render(<LoginPage />)

      await user.click(screen.getByText(/don't have an account/i))

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInputs = screen.getAllByLabelText(/password/i)
      const passwordInput = passwordInputs[0]
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'differentpassword')
      await user.click(screen.getByRole('button', { name: /create account/i }))

      await waitFor(() => {
        expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument()
      })
    })

    it('calls signUp with valid data', async () => {
      mockSignUp.mockResolvedValue(undefined)
      const user = userEvent.setup()
      render(<LoginPage />)

      await user.click(screen.getByText(/don't have an account/i))

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInputs = screen.getAllByLabelText(/password/i)
      const passwordInput = passwordInputs[0]
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

      await user.type(emailInput, 'new@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(screen.getByRole('button', { name: /create account/i }))

      await waitFor(() => {
        expect(mockSignUp).toHaveBeenCalledWith('new@example.com', 'password123')
      })
    })

    it('shows success toast and switches to login after sign up', async () => {
      mockSignUp.mockResolvedValue(undefined)
      const user = userEvent.setup()
      render(<LoginPage />)

      await user.click(screen.getByText(/don't have an account/i))

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInputs = screen.getAllByLabelText(/password/i)
      const passwordInput = passwordInputs[0]
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

      await user.type(emailInput, 'new@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(screen.getByRole('button', { name: /create account/i }))

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Account created')
        )
      })
    })
  })

  describe('Form Toggle', () => {
    it('can switch between login and sign up forms', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      // Start on login
      expect(screen.getByText('Sign in to your account')).toBeInTheDocument()

      // Switch to sign up
      await user.click(screen.getByText(/don't have an account/i))
      expect(screen.getByText('Create an account')).toBeInTheDocument()

      // Switch back to login
      await user.click(screen.getByText(/already have an account/i))
      expect(screen.getByText('Sign in to your account')).toBeInTheDocument()
    })
  })
})
