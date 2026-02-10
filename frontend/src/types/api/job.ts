/**
 * Job/Discovery Session API Types
 */

export type JobStatus =
  | 'pending'
  | 'analyzing'
  | 'discovering'
  | 'scoring'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface Job {
  id: string
  name: string
  status: JobStatus
  created_at: string
  updated_at?: string
  user_id: string
  brand_description: string
  reference_profiles: string[]
  follower_range_min: number
  follower_range_max: number
  discovery_limit: number
  keywords: string[]
  hashtags: string[]
  min_score_threshold: number
  profiles_discovered: number
  profiles_scored: number
  error_message?: string
}

export interface CreateJobRequest {
  name?: string
  brand_description: string
  reference_profiles: string[]
  follower_range_min?: number
  follower_range_max?: number
  discovery_limit?: number
  keywords?: string[]
  hashtags?: string[]
  min_score_threshold?: number
}

export interface CreateJobResponse {
  id: string
  name: string
  status: JobStatus
  message?: string
}

export interface JobActionResponse {
  job_id: string
  status: JobStatus
  message: string
}

export interface DemoStartResponse {
  job_id: string
  message: string
}
