/**
 * Demo Service
 * API methods for demo functionality
 */

import { api } from '@/lib/api'
import type { DemoStartResponse } from '@/types/api/job'

export const demoService = {
  /**
   * Start a demo discovery session with sample data
   */
  start: () => api.post<DemoStartResponse>('/api/demo/start'),
}
