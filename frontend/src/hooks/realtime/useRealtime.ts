import { useEffect, useRef } from 'react'
import { supabase } from '@/lib/supabase'

export interface UseRealtimeOptions<T> {
  /** Table to subscribe to */
  table: 'discovered_profiles' | 'profile_scores' | 'discovery_jobs'
  /** Job ID to filter by (if applicable) */
  jobId?: string
  /** Callback when a new record is inserted */
  onInsert?: (record: T) => void
  /** Callback when a record is updated */
  onUpdate?: (record: T) => void
  /** Callback when a record is deleted */
  onDelete?: (record: T) => void
  /** Whether the subscription is enabled */
  enabled?: boolean
}

/**
 * Hook to subscribe to real-time changes from Supabase
 * 
 * @example
 * ```tsx
 * useRealtime({
 *   table: 'discovered_profiles',
 *   jobId: job.id,
 *   onInsert: (profile) => {
 *     queryClient.setQueryData(['profiles', job.id], (old) => ({
 *       ...old,
 *       profiles: [...old.profiles, profile],
 *     }))
 *   },
 * })
 * ```
 */
export function useRealtime<T = unknown>({
  table,
  jobId,
  onInsert,
  onUpdate,
  onDelete,
  enabled = true,
}: UseRealtimeOptions<T>) {
  // Use refs to avoid recreating subscription on callback changes
  const onInsertRef = useRef(onInsert)
  const onUpdateRef = useRef(onUpdate)
  const onDeleteRef = useRef(onDelete)

  // Update refs when callbacks change
  useEffect(() => {
    onInsertRef.current = onInsert
    onUpdateRef.current = onUpdate
    onDeleteRef.current = onDelete
  }, [onInsert, onUpdate, onDelete])

  useEffect(() => {
    if (!enabled) return

    // Create channel name with job filter if provided
    const channelName = jobId
      ? `${table}:job_id=eq.${jobId}`
      : table

    // Create channel
    const channel = supabase.channel(channelName)

    // Subscribe to INSERT events
    if (onInsertRef.current) {
      channel.on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table,
          ...(jobId && { filter: `job_id=eq.${jobId}` }),
        },
        (payload) => {
          onInsertRef.current?.(payload.new as T)
        }
      )
    }

    // Subscribe to UPDATE events
    if (onUpdateRef.current) {
      channel.on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table,
          ...(jobId && { filter: `job_id=eq.${jobId}` }),
        },
        (payload) => {
          onUpdateRef.current?.(payload.new as T)
        }
      )
    }

    // Subscribe to DELETE events
    if (onDeleteRef.current) {
      channel.on(
        'postgres_changes',
        {
          event: 'DELETE',
          schema: 'public',
          table,
          ...(jobId && { filter: `job_id=eq.${jobId}` }),
        },
        (payload) => {
          onDeleteRef.current?.(payload.old as T)
        }
      )
    }

    // Subscribe to the channel
    const subscription = channel.subscribe()

    // Cleanup on unmount
    return () => {
      subscription.unsubscribe()
    }
  }, [table, jobId, enabled])
}
