/**
 * Hook for subscribing to real-time job status changes.
 * Updates React Query cache when job status changes in Supabase.
 */

import { useQueryClient } from '@tanstack/react-query'
import { useRealtime } from './useRealtime'
import { jobsKeys } from '../jobs/useJobs'
import type { Job } from '@/types/api/job'

export interface UseRealtimeJobStatusOptions {
  /** Job ID to subscribe to */
  jobId: string
  /** Whether the subscription is enabled */
  enabled?: boolean
  /** Callback when job status changes */
  onStatusChange?: (newStatus: Job['status'], previousStatus?: Job['status']) => void
}

/**
 * Hook to subscribe to real-time job status updates.
 * Automatically updates React Query cache when job status changes.
 * 
 * @example
 * ```tsx
 * function ProcessingPage({ jobId }) {
 *   useRealtimeJobStatus({ 
 *     jobId, 
 *     enabled: isRunning,
 *     onStatusChange: (newStatus) => {
 *       if (newStatus === 'completed') {
 *         toast.success('Discovery complete!')
 *       }
 *     }
 *   })
 *   const { data: job } = useJob(jobId)
 *   // Job will update in real-time!
 * }
 * ```
 */
export function useRealtimeJobStatus({ 
  jobId, 
  enabled = true,
  onStatusChange,
}: UseRealtimeJobStatusOptions) {
  const queryClient = useQueryClient()

  useRealtime<Job>({
    table: 'discovery_jobs',
    enabled: enabled && !!jobId,
    onUpdate: (updatedJob) => {
      // Only process updates for the specific job we're watching
      if (updatedJob.id === jobId) {
        // Get previous job data to detect status changes
        const previousJob = queryClient.getQueryData<Job>(jobsKeys.detail(jobId))
        
        // Invalidate job query to refetch with updated data
        queryClient.invalidateQueries({ queryKey: jobsKeys.detail(jobId) })
        
        // Also invalidate analytics as they may have changed
        queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
        
        // Also invalidate jobs list
        queryClient.invalidateQueries({ queryKey: jobsKeys.all })
        
        // Call the status change callback if provided and status actually changed
        if (onStatusChange && previousJob?.status !== updatedJob.status) {
          onStatusChange(updatedJob.status, previousJob?.status)
        }
      }
    },
  })
}
