/**
 * Hook for toggling profile bookmark with optimistic update
 */

import { useMutation, useQueryClient, type QueryKey } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'
import { profilesKeys } from './useProfiles'
import type { ProfilesResponse } from '@/types/api/profile'

interface ToggleBookmarkParams {
  jobId: string
  profileId: string
}

interface BookmarkContext {
  previousQueries: [QueryKey, ProfilesResponse | undefined][]
}

export function useToggleBookmark() {
  const queryClient = useQueryClient()

  return useMutation<{ id: string; is_bookmarked: boolean }, Error, ToggleBookmarkParams, BookmarkContext>({
    mutationFn: ({ jobId, profileId }) => profilesService.toggleBookmark(jobId, profileId),
    onMutate: async ({ profileId }) => {
      // Cancel outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: profilesKeys.lists() })

      // Snapshot previous queries for rollback
      const previousQueries = queryClient.getQueriesData<ProfilesResponse>({
        queryKey: profilesKeys.lists(),
      })

      // Optimistically toggle is_bookmarked in all matching profile lists
      queryClient.setQueriesData<ProfilesResponse>(
        { queryKey: profilesKeys.lists() },
        (old) => {
          if (!old) return old
          return {
            ...old,
            profiles: old.profiles.map((p) =>
              p.id === profileId ? { ...p, is_bookmarked: !p.is_bookmarked } : p
            ),
          }
        }
      )

      return { previousQueries }
    },
    onError: (_err, _vars, context) => {
      // Rollback on error
      if (context?.previousQueries) {
        for (const [key, data] of context.previousQueries) {
          queryClient.setQueryData(key, data)
        }
      }
    },
    onSettled: (_, __, { jobId }) => {
      queryClient.invalidateQueries({ queryKey: profilesKeys.lists() })
      queryClient.invalidateQueries({ queryKey: profilesKeys.analytics(jobId) })
    },
  })
}
