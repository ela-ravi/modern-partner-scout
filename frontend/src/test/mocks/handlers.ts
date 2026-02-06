import { http, HttpResponse } from 'msw'
import type { Job, CreateJobRequest, JobStatus } from '@/types/api/job'
import type { Profile, ProfileStatus, JobAnalytics } from '@/types/api/profile'

const API_URL = 'http://localhost:8000'

// Mock data
const mockJobs: Job[] = [
  {
    id: '1',
    name: 'Summer Campaign 2026',
    status: 'completed' as JobStatus,
    created_at: '2026-02-01T10:00:00Z',
    user_id: 'user-1',
    profiles_discovered: 45,
    profiles_scored: 45,
  },
  {
    id: '2',
    name: 'Spring Collection',
    status: 'scoring' as JobStatus,
    created_at: '2026-02-05T14:00:00Z',
    user_id: 'user-1',
    profiles_discovered: 23,
    profiles_scored: 12,
  },
  {
    id: '3',
    name: 'Q1 Influencer Outreach',
    status: 'pending' as JobStatus,
    created_at: '2026-02-06T09:00:00Z',
    user_id: 'user-1',
    profiles_discovered: 0,
    profiles_scored: 0,
  },
]

const mockProfiles: Profile[] = [
  {
    id: '1',
    job_id: '1',
    username: 'lifestyle_luna',
    full_name: 'Luna Martinez',
    bio: 'Fashion & lifestyle creator | Sustainable living advocate | NYC 📍',
    profile_pic_url: 'https://i.pravatar.cc/150?u=luna',
    follower_count: 156000,
    following_count: 890,
    post_count: 423,
    engagement_rate: 4.8,
    email: 'luna@example.com',
    status: 'done' as ProfileStatus,
    score: {
      overall_score: 92,
      engagement: 95,
      relevance: 88,
      authenticity: 90,
      reach: 85,
      content_quality: 94,
      brand_alignment: 92,
      reasoning: 'Excellent engagement rate and strong brand alignment with sustainable fashion content.',
    },
    is_bookmarked: true,
    created_at: '2026-02-01T12:00:00Z',
  },
  {
    id: '2',
    job_id: '1',
    username: 'alex_adventures',
    full_name: 'Alex Chen',
    bio: 'Travel photographer | Adventure seeker | Coffee lover ☕',
    profile_pic_url: 'https://i.pravatar.cc/150?u=alex',
    follower_count: 89000,
    following_count: 560,
    post_count: 312,
    engagement_rate: 3.9,
    status: 'done' as ProfileStatus,
    score: {
      overall_score: 78,
      engagement: 72,
      relevance: 80,
      authenticity: 85,
      reach: 70,
      content_quality: 82,
      brand_alignment: 75,
      reasoning: 'Good authenticity scores but lower reach than ideal for campaign goals.',
    },
    is_bookmarked: false,
    created_at: '2026-02-01T12:30:00Z',
  },
  {
    id: '3',
    job_id: '1',
    username: 'fitness_fab',
    full_name: 'Fabiana Rose',
    bio: 'Certified PT | Wellness coach | Plant-based athlete 🌱',
    profile_pic_url: 'https://i.pravatar.cc/150?u=fabiana',
    follower_count: 234000,
    following_count: 1200,
    post_count: 678,
    engagement_rate: 5.2,
    email: 'fab@wellness.co',
    status: 'new' as ProfileStatus,
    score: {
      overall_score: 88,
      engagement: 92,
      relevance: 85,
      authenticity: 88,
      reach: 90,
      content_quality: 86,
      brand_alignment: 87,
    },
    is_bookmarked: false,
    created_at: '2026-02-01T13:00:00Z',
  },
  {
    id: '4',
    job_id: '1',
    username: 'minimal_max',
    full_name: 'Max Turner',
    bio: 'Minimalist lifestyle | Tech enthusiast | Aspiring author',
    profile_pic_url: 'https://i.pravatar.cc/150?u=max',
    follower_count: 45000,
    following_count: 320,
    post_count: 156,
    engagement_rate: 6.1,
    status: 'processing' as ProfileStatus,
    is_bookmarked: false,
    created_at: '2026-02-01T13:30:00Z',
  },
  {
    id: '5',
    job_id: '1',
    username: 'chef_maria',
    full_name: 'Maria Santos',
    bio: 'Home chef | Recipe developer | Food photography 📸',
    profile_pic_url: 'https://i.pravatar.cc/150?u=maria',
    follower_count: 178000,
    following_count: 890,
    post_count: 567,
    engagement_rate: 4.4,
    email: 'maria@cookwithme.com',
    status: 'done' as ProfileStatus,
    score: {
      overall_score: 65,
      engagement: 70,
      relevance: 55,
      authenticity: 80,
      reach: 75,
      content_quality: 72,
      brand_alignment: 50,
      reasoning: 'Good engagement but food niche may not align well with fashion brand.',
    },
    is_bookmarked: false,
    created_at: '2026-02-01T14:00:00Z',
  },
]

const mockAnalytics: JobAnalytics = {
  total_discovered: 45,
  total_scored: 42,
  high_match_count: 12,
  emails_found: 28,
  average_score: 74.5,
  status_breakdown: {
    new: 8,
    processing: 5,
    done: 30,
    skipped: 2,
  },
}

export const handlers = [
  // Jobs endpoints
  http.get(`${API_URL}/api/jobs`, () => {
    return HttpResponse.json(mockJobs)
  }),

  http.get(`${API_URL}/api/jobs/:jobId`, ({ params }) => {
    const job = mockJobs.find((j) => j.id === params.jobId)
    if (!job) {
      return HttpResponse.json({ error: { message: 'Job not found' } }, { status: 404 })
    }
    return HttpResponse.json(job)
  }),

  http.post(`${API_URL}/api/jobs`, async ({ request }) => {
    const body = (await request.json()) as CreateJobRequest
    return HttpResponse.json({
      id: '4',
      name: body.name || 'New Campaign',
      status: 'pending' as JobStatus,
      message: 'Job created successfully',
    })
  }),

  http.delete(`${API_URL}/api/jobs/:jobId`, ({ params }) => {
    return HttpResponse.json({ message: `Job ${params.jobId} deleted` })
  }),

  http.post(`${API_URL}/api/jobs/:jobId/start`, ({ params }) => {
    return HttpResponse.json({
      job_id: params.jobId,
      status: 'analyzing' as JobStatus,
      message: 'Job started',
    })
  }),

  http.post(`${API_URL}/api/jobs/:jobId/cancel`, ({ params }) => {
    return HttpResponse.json({
      job_id: params.jobId,
      status: 'cancelled' as JobStatus,
      message: 'Job cancelled successfully',
    })
  }),

  http.post(`${API_URL}/api/jobs/:jobId/retry`, ({ params }) => {
    return HttpResponse.json({
      job_id: params.jobId,
      status: 'pending' as JobStatus,
      message: 'Job retry initiated',
    })
  }),

  // Profiles endpoints
  http.get(`${API_URL}/api/jobs/:jobId/profiles`, ({ request }) => {
    const url = new URL(request.url)
    const status = url.searchParams.get('status')
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '20')

    let filteredProfiles = [...mockProfiles]

    if (status) {
      filteredProfiles = filteredProfiles.filter((p) => p.status === status)
    }

    const start = (page - 1) * pageSize
    const end = start + pageSize
    const paginatedProfiles = filteredProfiles.slice(start, end)

    return HttpResponse.json({
      profiles: paginatedProfiles,
      total: filteredProfiles.length,
      page,
      page_size: pageSize,
      has_more: end < filteredProfiles.length,
    })
  }),

  http.get(`${API_URL}/api/jobs/:jobId/profiles/:profileId`, ({ params }) => {
    const profile = mockProfiles.find((p) => p.id === params.profileId)
    if (!profile) {
      return HttpResponse.json({ error: { message: 'Profile not found' } }, { status: 404 })
    }
    return HttpResponse.json(profile)
  }),

  http.post(`${API_URL}/api/jobs/:jobId/profiles/:profileId/bookmark`, ({ params }) => {
    const profile = mockProfiles.find((p) => p.id === params.profileId)
    return HttpResponse.json({
      is_bookmarked: profile ? !profile.is_bookmarked : true,
    })
  }),

  http.post(`${API_URL}/api/jobs/:jobId/profiles/:profileId/skip`, () => {
    return HttpResponse.json({ status: 'skipped' })
  }),

  // Analytics endpoint
  http.get(`${API_URL}/api/jobs/:jobId/analytics`, () => {
    return HttpResponse.json(mockAnalytics)
  }),

  // Email endpoints
  http.post(`${API_URL}/api/email/generate`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({
      subject: `Partnership Opportunity with ${body.brand_name || 'Our Brand'}`,
      body: 'Hi! We love your content and would like to discuss a partnership...',
    })
  }),

  http.post(`${API_URL}/api/email/send`, () => {
    return HttpResponse.json({
      success: true,
      message: 'Email sent successfully',
    })
  }),

  // Demo endpoint
  http.post(`${API_URL}/api/demo/start`, () => {
    return HttpResponse.json({
      job_id: 'demo-1',
      message: 'Demo started',
    })
  }),
]
