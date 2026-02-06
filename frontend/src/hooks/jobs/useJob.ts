/**
 * Hook for fetching a single job by ID
 */

import { useQuery } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { Job } from '@/types/api/job'

export function useJob(id: string | undefined) {
  return useQuery<Job, Error>({
    queryKey: jobsKeys.detail(id || ''),
    queryFn: () => jobsService.get(id!),
    enabled: !!id,
  })
}
