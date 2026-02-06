import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FollowerPresets } from './FollowerPresets'

describe('FollowerPresets', () => {
  const mockOnSelect = vi.fn()

  beforeEach(() => {
    mockOnSelect.mockClear()
  })

  it('renders 4 preset buttons', () => {
    render(<FollowerPresets onSelect={mockOnSelect} />)
    
    expect(screen.getByRole('button', { name: /nano/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /micro/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /mid-tier/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /macro/i })).toBeInTheDocument()
  })

  it('calls onSelect with correct values when preset clicked', () => {
    render(<FollowerPresets onSelect={mockOnSelect} />)
    
    fireEvent.click(screen.getByRole('button', { name: /micro/i }))
    expect(mockOnSelect).toHaveBeenCalledWith(10000, 100000)
    
    fireEvent.click(screen.getByRole('button', { name: /nano/i }))
    expect(mockOnSelect).toHaveBeenCalledWith(1000, 10000)
    
    fireEvent.click(screen.getByRole('button', { name: /mid-tier/i }))
    expect(mockOnSelect).toHaveBeenCalledWith(100000, 500000)
    
    fireEvent.click(screen.getByRole('button', { name: /macro/i }))
    expect(mockOnSelect).toHaveBeenCalledWith(500000, 10000000)
  })

  it('shows active state for selected preset', () => {
    render(<FollowerPresets onSelect={mockOnSelect} activePreset="micro" />)
    
    const microButton = screen.getByRole('button', { name: /micro/i })
    expect(microButton).toHaveAttribute('data-active', 'true')
    
    const nanoButton = screen.getByRole('button', { name: /nano/i })
    expect(nanoButton).toHaveAttribute('data-active', 'false')
  })

  it('clears active state when no preset matches', () => {
    render(<FollowerPresets onSelect={mockOnSelect} activePreset={undefined} />)
    
    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      expect(button).toHaveAttribute('data-active', 'false')
    })
  })
})
