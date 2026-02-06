import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useRealtime } from './useRealtime'

// Mock Supabase client
vi.mock('@/lib/supabase', () => ({
  supabase: {
    channel: vi.fn(() => ({
      on: vi.fn().mockReturnThis(),
      subscribe: vi.fn().mockReturnValue({
        unsubscribe: vi.fn(),
      }),
    })),
  },
}))

describe('useRealtime', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('subscribes to a channel on mount', async () => {
    const { supabase } = await import('@/lib/supabase')

    renderHook(() =>
      useRealtime({
        table: 'discovered_profiles',
        jobId: 'job-123',
        onInsert: vi.fn(),
      })
    )

    expect(supabase.channel).toHaveBeenCalledWith(expect.stringContaining('discovered_profiles'))
  })

  it('unsubscribes on unmount', async () => {
    const mockUnsubscribe = vi.fn()
    const { supabase } = await import('@/lib/supabase')
    
    const mockChannel = {
      on: vi.fn().mockReturnThis(),
      subscribe: vi.fn().mockReturnValue({
        unsubscribe: mockUnsubscribe,
      }),
    }
    vi.mocked(supabase.channel).mockReturnValue(mockChannel as never)

    const { unmount } = renderHook(() =>
      useRealtime({
        table: 'discovered_profiles',
        jobId: 'job-123',
        onInsert: vi.fn(),
      })
    )

    unmount()
    expect(mockUnsubscribe).toHaveBeenCalled()
  })

  it('calls onInsert callback when new record is inserted', async () => {
    const onInsert = vi.fn()
    const { supabase } = await import('@/lib/supabase')

    let insertHandler: (payload: { new: unknown }) => void = () => {}

    const mockChannel = {
      on: vi.fn((_event, filter, callback) => {
        if (filter?.event === 'INSERT') {
          insertHandler = callback
        }
        return mockChannel
      }),
      subscribe: vi.fn().mockReturnValue({
        unsubscribe: vi.fn(),
      }),
    }
    vi.mocked(supabase.channel).mockReturnValue(mockChannel as never)

    renderHook(() =>
      useRealtime({
        table: 'discovered_profiles',
        jobId: 'job-123',
        onInsert,
      })
    )

    // Simulate an insert
    act(() => {
      insertHandler({ new: { id: 'profile-1', job_id: 'job-123' } })
    })

    expect(onInsert).toHaveBeenCalledWith({ id: 'profile-1', job_id: 'job-123' })
  })

  it('calls onUpdate callback when record is updated', async () => {
    const onUpdate = vi.fn()
    const { supabase } = await import('@/lib/supabase')

    let updateHandler: (payload: { new: unknown }) => void = () => {}

    const mockChannel = {
      on: vi.fn((_event, filter, callback) => {
        if (filter?.event === 'UPDATE') {
          updateHandler = callback
        }
        return mockChannel
      }),
      subscribe: vi.fn().mockReturnValue({
        unsubscribe: vi.fn(),
      }),
    }
    vi.mocked(supabase.channel).mockReturnValue(mockChannel as never)

    renderHook(() =>
      useRealtime({
        table: 'discovered_profiles',
        jobId: 'job-123',
        onUpdate,
      })
    )

    // Simulate an update
    act(() => {
      updateHandler({ new: { id: 'profile-1', job_id: 'job-123', status: 'done' } })
    })

    expect(onUpdate).toHaveBeenCalledWith({ id: 'profile-1', job_id: 'job-123', status: 'done' })
  })

  it('filters by jobId when provided', async () => {
    const { supabase } = await import('@/lib/supabase')

    const mockChannel = {
      on: vi.fn().mockReturnThis(),
      subscribe: vi.fn().mockReturnValue({
        unsubscribe: vi.fn(),
      }),
    }
    vi.mocked(supabase.channel).mockReturnValue(mockChannel as never)

    renderHook(() =>
      useRealtime({
        table: 'discovered_profiles',
        jobId: 'job-123',
        onInsert: vi.fn(),
      })
    )

    // Verify the channel was created with job filter in the name
    expect(supabase.channel).toHaveBeenCalledWith('discovered_profiles:job_id=eq.job-123')
  })
})
