/**
 * Hook for fetching job analytics
 */

import { useQuery } from '@tanstack/react-query'
import { profilesService } from '@/services/profiles'
import { profilesKeys } from './useProfiles'
import type { JobAnalytics } from '@/types/api/profile'

export function useJobAnalytics(
  jobId: string | undefined,
  options?: { refetchInterval?: number | false },
) {
  return useQuery<JobAnalytics, Error>({
    queryKey: profilesKeys.analytics(jobId || ''),
    queryFn: () => profilesService.getAnalytics(jobId!),
    enabled: !!jobId,
    refetchInterval: options?.refetchInterval,
  })
}
