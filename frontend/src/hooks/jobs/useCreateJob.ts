/**
 * Hook for creating a new job
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { CreateJobRequest, CreateJobResponse } from '@/types/api/job'

export function useCreateJob() {
  const queryClient = useQueryClient()

  return useMutation<CreateJobResponse, Error, CreateJobRequest>({
    mutationFn: (data) => jobsService.create(data),
    onSuccess: () => {
      // Invalidate jobs list to refetch
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
