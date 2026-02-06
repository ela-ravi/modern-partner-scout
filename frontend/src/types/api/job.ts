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
  profiles_discovered: number
  profiles_scored: number
  error_message?: string
}

export interface CreateJobRequest {
  name: string
  reference_profiles?: string[]
  brand_description?: string
  min_followers?: number
  max_followers?: number
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
