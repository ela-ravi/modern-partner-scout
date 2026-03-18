import type { JobAnalytics } from '@/types/api/profile'

export const MOCK_ANALYTICS: JobAnalytics = {
  job_id: 'job-001-summer-skincare',
  total_profiles: 48,
  new_profiles: 3,
  processing_profiles: 2,
  done_profiles: 40,
  skipped_profiles: 3,
  avg_score: 72,
  max_score: 94,
  min_score: 34,
  profiles_with_email: 28,
}
