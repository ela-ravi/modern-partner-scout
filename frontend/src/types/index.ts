// Enums
export type JobStatus = 'pending' | 'analyzing' | 'discovering' | 'scoring' | 'completed' | 'failed';
export type ProfileStatus = 'new' | 'processing' | 'done' | 'skipped';

// Main Types
export interface DiscoveryJob {
  id: string;
  user_id: string;
  name: string;
  brand_description: string;
  reference_profiles: string[];
  follower_range_min?: number;
  follower_range_max?: number;
  discovery_limit?: number;
  status: JobStatus;
  profiles_discovered: number;
  profiles_scored: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface BrandDNA {
  id: string;
  job_id: string;
  hashtags: string[];
  keywords: string[];
  visual_themes?: string[]; // Made optional as it wasn't in SQL schema but is in types
  content_pillars?: string[]; // Made optional
  target_audience_description?: string; // Made optional
  embedding_vector?: number[];
  created_at: string;
}

export interface DiscoveredProfile {
  id: string;
  job_id: string;
  instagram_url: string;
  username: string;
  full_name?: string;
  profile_picture_url?: string;
  bio?: string;
  followers: number; // Changed from followers_count to match DB view
  following?: number; // Changed from following_count
  posts_count?: number;
  engagement_rate?: number;
  following_ratio?: number;
  is_verified: boolean;
  is_business?: boolean; // Changed from is_business_account
  external_url?: string;
  business_email?: string;
  business_category?: string;
  status: ProfileStatus;
  created_at: string;
}

export interface ProfileScore {
  id: string;
  profile_id: string;
  visual_aesthetic_match: number;      // 0-100
  content_theme_alignment: number;     // 0-100
  engagement_rate_score: number;       // 0-100
  follower_quality: number;            // 0-100
  business_indicators: number;         // 0-100
  activity_recency: number;            // 0-100
  score: number;                       // Final score 0-100
  recommendation?: string;
  reasoning: Record<string, any>;
  is_fake_suspected?: boolean;
  created_at: string;
}

export interface ProfileContact {
  id: string;
  profile_id: string;
  email?: string;
  email_source?: string; // Changed from source to email_source in view
  phone?: string;
  website?: string;
  other_contacts?: Record<string, any>;
  created_at: string;
}

// Combined View (from v_complete_profiles)
export interface CompleteProfile extends DiscoveredProfile {
  score?: number; // From view
  visual_aesthetic_match?: number;
  content_theme_alignment?: number;
  engagement_rate_score?: number;
  follower_quality?: number;
  business_indicators?: number;
  activity_recency?: number;
  reasoning?: Record<string, any>;
  email?: string;
  email_source?: string;
}

export interface JobWithProfiles {
  job: DiscoveryJob;
  profiles: CompleteProfile[];
  brand_dna?: BrandDNA;
}

// Analytics Response
// Analytics Response conforming to backend
export interface JobAnalytics {
  job_id: string;
  total_profiles: number;
  new_profiles: number;
  processing_profiles: number;
  done_profiles: number;
  skipped_profiles: number;
  avg_score: number | null;
  max_score: number | null;
  min_score: number | null;
  profiles_with_email: number;
}

// API Responses
export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface ApiResponse<T> {
  data: T;
  error?: ApiError;
}
