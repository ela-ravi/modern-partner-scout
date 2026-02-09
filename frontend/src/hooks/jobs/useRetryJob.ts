import { useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'
import type { Job } from '@/types/api/job'

export function useRetryJob() {
  const queryClient = useQueryClient()

  return useMutation<Job, Error, string>({
    mutationFn: (jobId) => jobsService.retry(jobId),
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: jobsKeys.detail(jobId) })
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
