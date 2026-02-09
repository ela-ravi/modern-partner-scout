/**
 * Hook for starting a pending job
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { JobActionResponse } from '@/types/api/job'

export function useStartJob() {
  const queryClient = useQueryClient()

  return useMutation<JobActionResponse, Error, string>({
    mutationFn: (jobId) => jobsService.start(jobId),
    onSuccess: (_, jobId) => {
      // Invalidate the specific job to refetch with updated status
      queryClient.invalidateQueries({ queryKey: jobsKeys.detail(jobId) })
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
