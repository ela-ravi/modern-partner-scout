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
} from '@/types/api/job'

export const jobsService = {
  /**
   * List all jobs for the current user
   */
  list: async () => {
    const response = await api.get<{ jobs: Job[]; total: number }>('/jobs')
    return response.jobs
  },

  /**
   * Get a specific job by ID
   */
  get: (id: string) => api.get<Job>(`/jobs/${id}`),

  /**
   * Create a new discovery job
   */
  create: (data: CreateJobRequest) => api.post<CreateJobResponse>('/jobs', data),

  /**
   * Delete a job
   */
  delete: (id: string) => api.delete<{ message: string }>(`/jobs/${id}`),

  /**
   * Start a pending job
   */
  start: (id: string) => api.post<JobActionResponse>(`/jobs/${id}/start`),

  /**
   * Cancel a running job
   */
  cancel: (id: string) => api.post<JobActionResponse>(`/jobs/${id}/cancel`),

  /**
   * Retry a failed job
   */
  retry: (id: string) => api.post<JobActionResponse>(`/jobs/${id}/retry`),
}
