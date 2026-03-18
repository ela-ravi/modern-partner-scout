import { useQueryClient } from '@tanstack/react-query'
import { useRealtime } from './useRealtime'
import type { Profile } from '@/types/api/profile'

export interface UseRealtimeProfilesOptions {
  /** Job ID to subscribe to */
  jobId: string
  /** Whether the subscription is enabled */
  enabled?: boolean
}

/**
 * Hook to subscribe to real-time profile updates for a job.
 * Automatically updates React Query cache when profiles are inserted or updated.
 * 
 * @example
 * ```tsx
 * function Dashboard({ jobId }) {
 *   useRealtimeProfiles({ jobId })
 *   const { data } = useProfiles({ job_id: jobId })
 *   // Profiles will update in real-time!
 * }
 * ```
 */
export function useRealtimeProfiles({ jobId, enabled = true }: UseRealtimeProfilesOptions) {
  const queryClient = useQueryClient()

  useRealtime<Profile>({
    table: 'discovered_profiles',
    jobId,
    enabled,
    onInsert: () => {
      // Invalidate profiles query to refetch with new profile
      queryClient.invalidateQueries({ queryKey: ['profiles', { job_id: jobId }] })
      
      // Also invalidate analytics
      queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
    },
    onUpdate: (updatedProfile) => {
      // Invalidate queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['profiles', { job_id: jobId }] })
      queryClient.invalidateQueries({ queryKey: ['profile', updatedProfile.id] })
      queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
    },
  })

  // Also subscribe to score updates
  useRealtime<{ profile_id: string; overall_score: number }>({
    table: 'profile_scores',
    enabled,
    onInsert: () => {
      // Invalidate profiles and analytics when a new score is added
      queryClient.invalidateQueries({ queryKey: ['profiles', { job_id: jobId }] })
      queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
    },
    onUpdate: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles', { job_id: jobId }] })
      queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
    },
  })
}
