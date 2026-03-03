/**
 * Profiles Service
 * API methods for managing discovered profiles
 *
 * Note: Backend does not have a standalone /jobs/{id}/profiles endpoint.
 * Profiles are returned as part of GET /jobs/{id} (JobWithProfiles).
 * This service adapts that response to the frontend's expected shape.
 */

import { api } from '@/lib/api'
import type {
  Profile,
  ProfilesResponse,
  GetProfilesParams,
  JobAnalytics,
} from '@/types/api/profile'

interface JobWithProfilesResponse {
  id: string
  profiles: Record<string, unknown>[]
  profiles_discovered: number
  profiles_scored: number
  [key: string]: unknown
}

/**
 * Transform a backend profile record into the frontend Profile shape.
 */
function transformProfile(raw: Record<string, unknown>): Profile {
  return {
    id: String(raw.id ?? ''),
    job_id: String(raw.job_id ?? ''),
    username: String(raw.username ?? ''),
    full_name: String(raw.full_name ?? raw.username ?? ''),
    bio: raw.bio as string | undefined,
    profile_pic_url: raw.profile_pic_url as string | undefined,
    follower_count: Number(raw.followers_count ?? raw.follower_count ?? 0),
    following_count: Number(raw.following_count ?? 0),
    post_count: Number(raw.posts_count ?? raw.post_count ?? 0),
    engagement_rate: Number(raw.engagement_rate ?? 0),
    email: (raw.contact_email ?? raw.email) as string | undefined,
    phone: (raw.contact_phone ?? raw.phone) as string | undefined,
    website: (raw.contact_website ?? raw.website ?? raw.external_url) as string | undefined,
    address: (() => {
      const oc = raw.other_contacts as Record<string, unknown> | undefined
      return oc?.address as string | undefined
    })(),
    email_source: raw.email_source as string | undefined,
    status: (raw.status as Profile['status']) ?? 'new',
    score: raw.final_score != null
      ? {
          overall_score: Number(raw.final_score),
          engagement: raw.engagement_score != null ? Number(raw.engagement_score) : undefined,
          relevance: raw.content_theme_score != null ? Number(raw.content_theme_score) : undefined,
          authenticity: raw.follower_quality_score != null ? Number(raw.follower_quality_score) : undefined,
          reach: raw.visual_aesthetic_score != null ? Number(raw.visual_aesthetic_score) : undefined,
          content_quality: raw.business_indicators_score != null ? Number(raw.business_indicators_score) : undefined,
          brand_alignment: raw.activity_recency_score != null ? Number(raw.activity_recency_score) : undefined,
          reasoning: typeof raw.reasoning === 'string'
            ? raw.reasoning
            : raw.reasoning && typeof raw.reasoning === 'object'
              ? (raw.reasoning as Record<string, unknown>).recommendation_reason
                ? String((raw.reasoning as Record<string, unknown>).recommendation_reason)
                : Object.entries(raw.reasoning as Record<string, unknown>)
                    .filter(([k, v]) => typeof v === 'string' && k !== 'fake_indicators')
                    .map(([, v]) => String(v))
                    .join(' ')
              : undefined,
        }
      : undefined,
    is_bookmarked: raw.is_bookmarked as boolean | undefined,
    created_at: String(raw.created_at ?? new Date().toISOString()),
    updated_at: raw.updated_at as string | undefined,
  }
}

export const profilesService = {
  /**
   * List profiles for a job with optional filtering and pagination.
   * Uses GET /jobs/{job_id} with profile query params since backend
   * embeds profiles in the job response.
   */
  list: async ({
    job_id,
    page = 1,
    page_size = 20,
    filters,
    sort,
  }: GetProfilesParams): Promise<ProfilesResponse> => {
    const params = new URLSearchParams()
    params.set('profile_limit', String(page_size))
    params.set('profile_offset', String((page - 1) * page_size))

    if (filters?.status) params.set('profile_status', filters.status)
    if (filters?.min_score) params.set('min_score', String(filters.min_score))
    if (filters?.is_bookmarked) params.set('is_bookmarked', 'true')

    const jobData = await api.get<JobWithProfilesResponse>(
      `/jobs/${job_id}?${params.toString()}`
    )

    const profiles = (jobData.profiles || []).map(transformProfile)

    // Client-side sort (backend doesn't support sort on embedded profiles)
    if (sort) {
      profiles.sort((a, b) => {
        let aVal: number, bVal: number
        switch (sort.field) {
          case 'score':
            aVal = a.score?.overall_score ?? 0
            bVal = b.score?.overall_score ?? 0
            break
          case 'follower_count':
            aVal = a.follower_count
            bVal = b.follower_count
            break
          case 'engagement_rate':
            aVal = a.engagement_rate
            bVal = b.engagement_rate
            break
          case 'created_at':
            aVal = new Date(a.created_at).getTime()
            bVal = new Date(b.created_at).getTime()
            break
          default:
            return 0
        }
        return sort.direction === 'desc' ? bVal - aVal : aVal - bVal
      })
    }

    return {
      profiles,
      total: jobData.profiles_discovered ?? profiles.length,
      page,
      page_size,
      has_more: profiles.length === page_size,
    }
  },

  /**
   * Get a specific profile by ID (fetches job and finds profile)
   */
  get: async (jobId: string, profileId: string): Promise<Profile> => {
    const jobData = await api.get<JobWithProfilesResponse>(`/jobs/${jobId}`)
    const raw = (jobData.profiles || []).find(
      (p) => String(p.id) === profileId
    )
    if (!raw) throw new Error('Profile not found')
    return transformProfile(raw)
  },

  /**
   * Toggle bookmark status for a profile.
   */
  toggleBookmark: async (_jobId: string, profileId: string) => {
    return api.patch<{ id: string; is_bookmarked: boolean }>(
      `/profiles/${profileId}/bookmark`,
      {}
    )
  },

  /**
   * Skip a profile (won't show in results)
   * Note: Backend doesn't have this endpoint yet
   */
  skip: async (jobId: string, profileId: string) => {
    void jobId; void profileId
    // TODO: Implement when backend adds skip endpoint
    return { status: 'skipped' }
  },

  /**
   * Get analytics summary for a job
   */
  getAnalytics: (jobId: string) => api.get<JobAnalytics>(`/jobs/${jobId}/analytics`),
}
