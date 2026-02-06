import { useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'

export interface SkipProfileParams {
  jobId: string
  profileId: string
}

/**
 * Hook to skip a profile (mark it as not interested)
 */
export function useSkipProfile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ jobId, profileId }: SkipProfileParams) =>
      profilesService.skip(jobId, profileId),
    onSuccess: (_data, { jobId }) => {
      // Invalidate profiles and analytics queries
      queryClient.invalidateQueries({ queryKey: ['profiles', { job_id: jobId }] })
      queryClient.invalidateQueries({ queryKey: ['job-analytics', jobId] })
    },
  })
}
