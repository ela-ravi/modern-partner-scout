/**
 * Hook for fetching all jobs
 */

import { useQuery } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import type { Job } from '@/types/api/job'

export const jobsKeys = {
  all: ['jobs'] as const,
  lists: () => [...jobsKeys.all, 'list'] as const,
  list: (filters?: Record<string, unknown>) => [...jobsKeys.lists(), filters] as const,
  details: () => [...jobsKeys.all, 'detail'] as const,
  detail: (id: string) => [...jobsKeys.details(), id] as const,
}

export function useJobs() {
  return useQuery<Job[], Error>({
    queryKey: jobsKeys.lists(),
    queryFn: () => jobsService.list(),
  })
}
