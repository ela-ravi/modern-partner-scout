/**
 * Hook for deleting a job
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsService } from '@/services/jobs'
import { jobsKeys } from './useJobs'

export function useDeleteJob() {
  const queryClient = useQueryClient()

  return useMutation<{ message: string }, Error, string>({
    mutationFn: (id) => jobsService.delete(id),
    onSuccess: () => {
      // Invalidate jobs list to refetch
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
