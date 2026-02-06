/**
 * Hook for canceling a running job
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { JobActionResponse } from '@/types/api/job'

export function useCancelJob() {
  const queryClient = useQueryClient()

  return useMutation<JobActionResponse, Error, string>({
    mutationFn: (id) => jobsService.cancel(id),
    onSuccess: (_, id) => {
      // Invalidate specific job and list
      queryClient.invalidateQueries({ queryKey: jobsKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
