/**
 * Hook for toggling profile bookmark
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'
import { profilesKeys } from './useProfiles'

interface ToggleBookmarkParams {
  jobId: string
  profileId: string
}

export function useToggleBookmark() {
  const queryClient = useQueryClient()

  return useMutation<{ is_bookmarked: boolean }, Error, ToggleBookmarkParams>({
    mutationFn: ({ jobId, profileId }) => profilesService.toggleBookmark(jobId, profileId),
    onSuccess: (_, { jobId }) => {
      // Invalidate profiles list to refetch
      queryClient.invalidateQueries({ queryKey: profilesKeys.lists() })
      queryClient.invalidateQueries({ queryKey: profilesKeys.analytics(jobId) })
    },
  })
}
