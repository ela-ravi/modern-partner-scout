/**
 * Profiles Service
 * API methods for managing discovered profiles
 */

import { api } from '@/lib/api'
import type {
  Profile,
  ProfilesResponse,
  GetProfilesParams,
  JobAnalytics,
} from '@/types/api/profile'

export const profilesService = {
  /**
   * List profiles for a job with optional filtering and pagination
   */
  list: async ({
    job_id,
    page = 1,
    page_size = 20,
    filters,
    sort,
  }: GetProfilesParams): Promise<ProfilesResponse> => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(page_size))

    if (filters?.status) params.set('status', filters.status)
    if (filters?.min_score) params.set('min_score', String(filters.min_score))
    if (filters?.has_email !== undefined) params.set('has_email', String(filters.has_email))
    if (filters?.is_bookmarked !== undefined)
      params.set('is_bookmarked', String(filters.is_bookmarked))

    if (sort) {
      params.set('sort_by', sort.field)
      params.set('sort_direction', sort.direction)
    }

    return api.get<ProfilesResponse>(`/api/jobs/${job_id}/profiles?${params.toString()}`)
  },

  /**
   * Get a specific profile by ID
   */
  get: (jobId: string, profileId: string) =>
    api.get<Profile>(`/api/jobs/${jobId}/profiles/${profileId}`),

  /**
   * Toggle bookmark status for a profile
   */
  toggleBookmark: (jobId: string, profileId: string) =>
    api.post<{ is_bookmarked: boolean }>(`/api/jobs/${jobId}/profiles/${profileId}/bookmark`),

  /**
   * Skip a profile (won't show in results)
   */
  skip: (jobId: string, profileId: string) =>
    api.post<{ status: string }>(`/api/jobs/${jobId}/profiles/${profileId}/skip`),

  /**
   * Get analytics summary for a job
   */
  getAnalytics: (jobId: string) => api.get<JobAnalytics>(`/api/jobs/${jobId}/analytics`),
}
