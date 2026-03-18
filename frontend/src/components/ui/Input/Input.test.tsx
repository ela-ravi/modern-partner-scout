import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { Input } from './Input'

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Email" />)
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('shows required indicator when required', () => {
    render(<Input label="Email" required />)
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('handles user input', async () => {
    const user = userEvent.setup()
    render(<Input label="Email" />)
    
    const input = screen.getByLabelText('Email')
    await user.type(input, 'test@example.com')
    
    expect(input).toHaveValue('test@example.com')
  })

  it('displays error message', () => {
    render(<Input label="Email" error="Invalid email address" />)
    
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid email address')
    expect(screen.getByLabelText('Email')).toHaveAttribute('aria-invalid', 'true')
  })

  it('displays helper text', () => {
    render(<Input label="Email" helperText="We'll never share your email" />)
    expect(screen.getByText("We'll never share your email")).toBeInTheDocument()
  })

  it('hides helper text when error is shown', () => {
    render(
      <Input
        label="Email"
        error="Invalid"
        helperText="Helper text should be hidden"
      />
    )
    
    expect(screen.queryByText('Helper text should be hidden')).not.toBeInTheDocument()
    expect(screen.getByText('Invalid')).toBeInTheDocument()
  })

  it('links label to input via htmlFor', () => {
    render(<Input label="Username" id="username-field" />)
    
    const input = screen.getByLabelText('Username')
    expect(input).toHaveAttribute('id', 'username-field')
  })

  it('applies disabled state correctly', () => {
    render(<Input label="Disabled" disabled />)
    expect(screen.getByLabelText('Disabled')).toBeDisabled()
  })
})
