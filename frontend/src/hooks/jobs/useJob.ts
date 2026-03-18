/**
 * Hook for fetching a single job by ID
 */

import { useQuery } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { Job } from '@/types/api/job'

export interface UseJobOptions {
  /** Poll interval in ms. Set to false to disable. */
  refetchInterval?: number | false
}

export function useJob(id: string | undefined, options?: UseJobOptions) {
  return useQuery<Job, Error>({
    queryKey: jobsKeys.detail(id || ''),
    queryFn: () => jobsService.get(id!),
    enabled: !!id,
    refetchInterval: options?.refetchInterval,
    // Retry transient errors (connection drops during orchestration)
    retry: 3,
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 5000),
  })
}
