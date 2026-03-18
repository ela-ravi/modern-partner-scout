/**
 * Profile API Types
 */

export type ProfileStatus = 'new' | 'processing' | 'done' | 'skipped'

export interface ProfileScore {
  overall_score: number
  engagement?: number
  relevance?: number
  authenticity?: number
  reach?: number
  content_quality?: number
  brand_alignment?: number
  reasoning?: string
}

export interface Profile {
  id: string
  job_id: string
  username: string
  full_name: string
  bio?: string
  profile_pic_url?: string
  follower_count: number
  following_count: number
  post_count: number
  engagement_rate: number
  email?: string
  phone?: string
  website?: string
  address?: string
  email_source?: string
  status: ProfileStatus
  score?: ProfileScore
  is_bookmarked?: boolean
  created_at: string
  updated_at?: string
}

export interface ProfilesResponse {
  profiles: Profile[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface ProfileFilters {
  status?: ProfileStatus
  min_score?: number
  has_email?: boolean
  is_bookmarked?: boolean
}

export interface ProfileSort {
  field: 'score' | 'created_at' | 'follower_count' | 'engagement_rate'
  direction: 'asc' | 'desc'
}

export interface GetProfilesParams {
  job_id: string
  page?: number
  page_size?: number
  filters?: ProfileFilters
  sort?: ProfileSort
}

export interface JobAnalytics {
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
}
