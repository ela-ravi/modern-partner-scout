/**
 * Hook for starting a demo session
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { demoService } from '@/services/demo'
import { jobsKeys } from './useJobs'
import type { DemoStartResponse } from '@/types/api/job'

export function useStartDemo() {
  const queryClient = useQueryClient()

  return useMutation<DemoStartResponse, Error, void>({
    mutationFn: () => demoService.start(),
    onSuccess: () => {
      // Invalidate jobs list to show new demo job
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() })
    },
  })
}
