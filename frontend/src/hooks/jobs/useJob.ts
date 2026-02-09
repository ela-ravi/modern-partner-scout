/**
 * Hook for fetching a single job by ID
 */

import { useQuery } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { Job } from '@/types/api/job'

export interface UseJobOptions {
  /** Enable polling at regular intervals (for running jobs) */
  enablePolling?: boolean
  /** Polling interval in milliseconds (default: 3000ms) */
  pollingInterval?: number
}

/**
 * Hook for fetching a single job by ID with optional polling support.
 * 
 * @param id - Job UUID to fetch
 * @param options - Optional configuration for polling
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { data: job } = useJob(jobId)
 * 
 * // With polling (for running jobs)
 * const { data: job } = useJob(jobId, { enablePolling: isRunning })
 * ```
 */
export function useJob(id: string | undefined, options?: UseJobOptions) {
  const { enablePolling = false, pollingInterval = 3000 } = options ?? {}

  return useQuery<Job, Error>({
    queryKey: jobsKeys.detail(id || ''),
    queryFn: () => jobsService.get(id!),
    enabled: !!id,
    // Poll every 3 seconds when enabled (fallback for real-time)
    refetchInterval: enablePolling ? pollingInterval : false,
    // Don't refetch on window focus when polling is active
    refetchOnWindowFocus: !enablePolling,
  })
}
