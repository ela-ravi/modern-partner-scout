/**
 * Hook for fetching a single profile
 */

import { useQuery } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'
import { profilesKeys } from './useProfiles'
import type { Profile } from '@/types/api/profile'

export function useProfile(jobId: string | undefined, profileId: string | undefined) {
  return useQuery<Profile, Error>({
    queryKey: profilesKeys.detail(jobId || '', profileId || ''),
    queryFn: () => profilesService.get(jobId!, profileId!),
    enabled: !!jobId && !!profileId,
  })
}
