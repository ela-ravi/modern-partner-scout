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

/**
 * Backend analytics response shape (different from frontend JobAnalytics)
 */
interface BackendAnalyticsResponse {
  job_id: string
  total_profiles: number
  new_profiles: number
  processing_profiles: number
  done_profiles: number
  skipped_profiles: number
  avg_score: number | null
  max_score: number | null
  min_score: number | null
  profiles_with_email: number
  high_score_count: number
}

/**
 * Transform backend analytics response to frontend JobAnalytics format
 */
function transformAnalytics(backend: BackendAnalyticsResponse): JobAnalytics {
  return {
    total_discovered: backend.total_profiles,
    total_scored: backend.done_profiles,
    high_match_count: backend.high_score_count ?? 0,
    emails_found: backend.profiles_with_email,
    average_score: backend.avg_score ?? 0,
    status_breakdown: {
      new: backend.new_profiles,
      processing: backend.processing_profiles,
      done: backend.done_profiles,
      skipped: backend.skipped_profiles,
    },
  }
}

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
   * Transforms backend response to match frontend JobAnalytics type
   */
  getAnalytics: async (jobId: string): Promise<JobAnalytics> => {
    const rawResponse = await api.get<BackendAnalyticsResponse>(`/api/jobs/${jobId}/analytics`)
    
    // #region agent log
    fetch('http://127.0.0.1:7247/ingest/a4834e21-fce4-4031-b8aa-7e6c09773ae1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'profiles.ts:getAnalytics',message:'Raw analytics API response',data:{jobId,rawResponse},hypothesisId:'H1-field-mismatch',timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    
    const transformed = transformAnalytics(rawResponse)
    
    // #region agent log
    fetch('http://127.0.0.1:7247/ingest/a4834e21-fce4-4031-b8aa-7e6c09773ae1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'profiles.ts:getAnalytics',message:'Transformed analytics',data:{transformed},hypothesisId:'H1-field-mismatch',timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    
    return transformed
  },
}
