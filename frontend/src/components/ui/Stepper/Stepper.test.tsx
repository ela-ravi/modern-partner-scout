import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Stepper } from './Stepper'

const mockSteps = [
  { label: 'Configure', status: 'complete' as const },
  { label: 'Launch', status: 'active' as const },
]

describe('Stepper', () => {
  it('renders correct number of steps', () => {
    render(<Stepper steps={mockSteps} />)
    
    expect(screen.getByText('Configure')).toBeInTheDocument()
    expect(screen.getByText('Launch')).toBeInTheDocument()
  })

  it('shows active step with correct styling', () => {
    render(<Stepper steps={mockSteps} />)
    
    const activeStep = screen.getByText('Launch').closest('[data-status]')
    expect(activeStep).toHaveAttribute('data-status', 'active')
  })

  it('shows completed step with checkmark', () => {
    render(<Stepper steps={mockSteps} />)
    
    const completeStep = screen.getByText('Configure').closest('[data-status]')
    expect(completeStep).toHaveAttribute('data-status', 'complete')
    // Check for checkmark icon (aria-label)
    expect(screen.getByLabelText(/complete/i)).toBeInTheDocument()
  })

  it('shows upcoming step with number', () => {
    const stepsWithUpcoming = [
      { label: 'Step 1', status: 'active' as const },
      { label: 'Step 2', status: 'upcoming' as const },
    ]
    render(<Stepper steps={stepsWithUpcoming} />)
    
    const upcomingStep = screen.getByText('Step 2').closest('[data-status]')
    expect(upcomingStep).toHaveAttribute('data-status', 'upcoming')
  })

  it('renders connector lines between steps', () => {
    render(<Stepper steps={mockSteps} />)
    
    // Should have connector between steps
    const connectors = document.querySelectorAll('[data-connector]')
    expect(connectors.length).toBe(mockSteps.length - 1)
  })

  it('has correct aria-current on active step', () => {
    render(<Stepper steps={mockSteps} />)
    
    const activeIndicator = screen.getByText('2')
    expect(activeIndicator.closest('[aria-current]')).toHaveAttribute('aria-current', 'step')
  })

  it('hides labels on mobile when hideLabelsOnMobile is true', () => {
    render(<Stepper steps={mockSteps} hideLabelsOnMobile />)
    
    const labels = screen.getAllByText(/Configure|Launch/)
    labels.forEach(label => {
      expect(label).toHaveClass('hidden', 'sm:block')
    })
  })
})
