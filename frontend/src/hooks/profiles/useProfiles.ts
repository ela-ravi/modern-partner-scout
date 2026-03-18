/**
 * Hook for fetching profiles for a job
 */

import { useQuery } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'
import type { ProfilesResponse, GetProfilesParams } from '@/types/api/profile'

export const profilesKeys = {
  all: ['profiles'] as const,
  lists: () => [...profilesKeys.all, 'list'] as const,
  list: (params: GetProfilesParams) => [...profilesKeys.lists(), params] as const,
  details: () => [...profilesKeys.all, 'detail'] as const,
  detail: (jobId: string, profileId: string) => [...profilesKeys.details(), jobId, profileId] as const,
  analytics: (jobId: string) => [...profilesKeys.all, 'analytics', jobId] as const,
}

export function useProfiles(params: GetProfilesParams) {
  return useQuery<ProfilesResponse, Error>({
    queryKey: profilesKeys.list(params),
    queryFn: () => profilesService.list(params),
    enabled: !!params.job_id,
  })
}
