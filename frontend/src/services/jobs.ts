/**
 * Jobs/Discovery Sessions Service
 * API methods for managing discovery jobs
 */

import { api } from '@/lib/api'
import type {
  Job,
  CreateJobRequest,
  CreateJobResponse,
  JobActionResponse,
  JobListResponse,
} from '@/types/api/job'

export const jobsService = {
  /**
   * List all jobs for the current user
   */
  list: async (): Promise<Job[]> => {
    const response = await api.get<JobListResponse>('/api/jobs')
    return response.jobs
  },

  /**
   * Get a specific job by ID
   */
  get: (id: string) => api.get<Job>(`/api/jobs/${id}`),

  /**
   * Create a new discovery job
   */
  create: (data: CreateJobRequest) => api.post<CreateJobResponse>('/api/jobs', data),

  /**
   * Delete a job
   */
  delete: (id: string) => api.delete<{ message: string }>(`/api/jobs/${id}`),

  /**
   * Start a pending job
   */
  start: (id: string) => api.post<JobActionResponse>(`/api/jobs/${id}/start`),

  /**
   * Cancel a running job
   */
  cancel: (id: string) => api.post<JobActionResponse>(`/api/jobs/${id}/cancel`),

  /**
   * Retry a failed job
   */
  retry: (id: string) => api.post<JobActionResponse>(`/api/jobs/${id}/retry`),
}
