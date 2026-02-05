-- Seed data for demo/testing
-- Create demo users in auth.users
WITH instance AS (
    SELECT id AS instance_id FROM auth.instances LIMIT 1
)
INSERT INTO auth.users (
    id,
    instance_id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_sso_user
)
SELECT
    '11111111-1111-1111-1111-111111111111',
    instance_id,
    'authenticated',
    'authenticated',
    'demo@partnerscout.ai',
    crypt('Password123!', gen_salt('bf')),
    NOW(),
    NOW(),
    NOW(),
    '{"provider":"email","providers":["email"]}',
    '{"full_name":"Demo User"}',
    false
FROM instance
ON CONFLICT (id) DO NOTHING;

WITH instance AS (
    SELECT id AS instance_id FROM auth.instances LIMIT 1
)
INSERT INTO auth.users (
    id,
    instance_id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_sso_user
)
SELECT
    '22222222-2222-2222-2222-222222222222',
    instance_id,
    'authenticated',
    'authenticated',
    'test@partnerscout.ai',
    crypt('Password123!', gen_salt('bf')),
    NOW(),
    NOW(),
    NOW(),
    '{"provider":"email","providers":["email"]}',
    '{"full_name":"Test User"}',
    false
FROM instance
ON CONFLICT (id) DO NOTHING;

-- Discovery jobs
INSERT INTO discovery_jobs (
    id,
    user_id,
    name,
    brand_description,
    reference_profiles,
    status,
    profiles_discovered,
    profiles_scored,
    created_at,
    updated_at
)
VALUES
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'Sustainable Fashion Discovery',
    'Eco-friendly sustainable fashion brand targeting millennials.',
    ARRAY[
        'https://instagram.com/everlane',
        'https://instagram.com/reformation',
        'https://instagram.com/patagonia'
    ],
    'completed',
    5,
    5,
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days'
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '11111111-1111-1111-1111-111111111111',
    'Fitness Brand Partners',
    'Premium fitness apparel brand focused on high-performance athletes.',
    ARRAY['https://instagram.com/lululemon', 'https://instagram.com/gymshark'],
    'scoring',
    3,
    1,
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day'
),
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    'Tech Accessories',
    'Premium tech accessories.',
    ARRAY[]::TEXT[],
    'pending',
    0,
    0,
    NOW() - INTERVAL '3 hours',
    NOW() - INTERVAL '3 hours'
),
(
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    '11111111-1111-1111-1111-111111111111',
    'Failed Discovery Test',
    'Test brand for failure scenarios.',
    ARRAY['https://instagram.com/invalid_profile_404'],
    'failed',
    0,
    0,
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days'
);

-- Brand DNA (embedding left NULL for demo)
INSERT INTO brand_dna (
    id,
    job_id,
    hashtags,
    keywords,
    competitors,
    embedding,
    analysis,
    created_at
)
VALUES (
    'd1d1d1d1-d1d1-d1d1-d1d1-d1d1d1d1d1d1',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    ARRAY['#sustainablefashion', '#ecofriendly', '#ethicalfashion'],
    ARRAY['sustainable', 'ethical', 'eco-friendly', 'minimalist'],
    ARRAY['patagonia', 'everlane'],
    NULL,
    '{"summary":"Sustainable fashion brand DNA"}',
    NOW() - INTERVAL '2 days'
);

-- Discovered profiles (mix of genuine and fake)
INSERT INTO discovered_profiles (
    id,
    job_id,
    instagram_url,
    username,
    full_name,
    profile_picture_url,
    bio,
    followers,
    following,
    posts_count,
    engagement_rate,
    is_verified,
    is_business,
    external_url,
    business_email,
    business_category,
    following_ratio,
    status,
    created_at
)
VALUES
(
    'aaaaaaaa-1111-1111-1111-111111111111',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/greenfashionista',
    'greenfashionista',
    'Green Fashionista',
    NULL,
    'Sustainable style inspiration.',
    20000,
    600,
    120,
    3.5,
    true,
    true,
    'https://greenfashionista.com',
    'hello@greenfashionista.com',
    'Fashion',
    0.03,
    'done',
    NOW() - INTERVAL '2 days'
),
(
    'bbbbbbbb-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/fitcoach',
    'fitcoach',
    'Fit Coach',
    NULL,
    'Training tips and programs.',
    8000,
    400,
    80,
    4.0,
    false,
    true,
    NULL,
    'coach@fitcoach.com',
    'Fitness',
    0.05,
    'done',
    NOW() - INTERVAL '2 days'
),
(
    'cccccccc-3333-3333-3333-333333333333',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/suspiciousgrowth',
    'suspiciousgrowth',
    'Suspicious Growth',
    NULL,
    'Quick growth secrets.',
    5000,
    4000,
    45,
    0.8,
    false,
    false,
    NULL,
    NULL,
    NULL,
    0.8,
    'done',
    NOW() - INTERVAL '2 days'
),
(
    'dddddddd-4444-4444-4444-444444444444',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/viraltrend',
    'viraltrend',
    'Viral Trend',
    NULL,
    'Trending content.',
    80000,
    1000,
    10,
    0.5,
    false,
    true,
    NULL,
    NULL,
    NULL,
    0.01,
    'done',
    NOW() - INTERVAL '2 days'
),
(
    'eeeeeeee-5555-5555-5555-555555555555',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/cleanbeauty',
    'cleanbeauty',
    'Clean Beauty',
    NULL,
    'Clean ingredients only.',
    15000,
    650,
    200,
    2.5,
    false,
    true,
    NULL,
    NULL,
    'Beauty',
    0.04,
    'done',
    NOW() - INTERVAL '2 days'
);

-- Profile scores (6 dimensions populated)
INSERT INTO profile_scores (
    id,
    profile_id,
    score,
    visual_aesthetic_match,
    content_theme_alignment,
    engagement_rate_score,
    follower_quality,
    business_indicators,
    activity_recency,
    reasoning,
    created_at
)
VALUES
(
    '11111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'aaaaaaaa-1111-1111-1111-111111111111',
    80,
    85,
    80,
    75,
    78,
    82,
    70,
    '{"summary":"Strong alignment with sustainable fashion audience."}',
    NOW() - INTERVAL '2 days'
),
(
    '22222222-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'bbbbbbbb-2222-2222-2222-222222222222',
    68,
    70,
    68,
    65,
    72,
    70,
    60,
    '{"summary":"Good fitness content but mid engagement quality."}',
    NOW() - INTERVAL '2 days'
),
(
    '33333333-cccc-cccc-cccc-cccccccccccc',
    'cccccccc-3333-3333-3333-333333333333',
    14,
    15,
    10,
    12,
    20,
    18,
    10,
    '{"summary":"High following ratio and low engagement signal fake growth."}',
    NOW() - INTERVAL '2 days'
),
(
    '44444444-dddd-dddd-dddd-dddddddddddd',
    'dddddddd-4444-4444-4444-444444444444',
    30,
    35,
    30,
    25,
    28,
    32,
    20,
    '{"summary":"Low content volume relative to follower count."}',
    NOW() - INTERVAL '2 days'
),
(
    '55555555-eeee-eeee-eeee-eeeeeeeeeeee',
    'eeeeeeee-5555-5555-5555-555555555555',
    72,
    75,
    70,
    68,
    70,
    74,
    65,
    '{"summary":"Clean beauty profile with solid engagement."}',
    NOW() - INTERVAL '2 days'
);

-- Profile contacts (emails for genuine profiles)
INSERT INTO profile_contacts (
    id,
    profile_id,
    email,
    source,
    confidence,
    extracted_at
)
VALUES
(
    'c1111111-1111-1111-1111-111111111111',
    'aaaaaaaa-1111-1111-1111-111111111111',
    'greenfashionista@creator.com',
    'bio',
    0.92,
    NOW() - INTERVAL '2 days'
),
(
    'c2222222-2222-2222-2222-222222222222',
    'bbbbbbbb-2222-2222-2222-222222222222',
    'fitcoach@creator.com',
    'external_url',
    0.74,
    NOW() - INTERVAL '2 days'
);
-- ============================================================================
-- Migration 007: Seed Data
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Demo data for testing and presentations.
-- Matches PRD specifications and mock_data fixtures.
-- 
-- NOTE: This is for demo/test environments only.
-- Do NOT run in production unless you want sample data.
-- ============================================================================

-- ============================================================================
-- DEMO USER
-- In real Supabase, users are created via auth.users (Supabase Auth).
-- For local testing, we insert directly.
-- ============================================================================

-- Skip user insertion for Supabase - users come from auth.users
-- This seed file assumes a user already exists from Supabase Auth signup.

-- If testing locally, uncomment and use a real auth.users UUID:
-- INSERT INTO auth.users (id, email) VALUES 
--     ('00000000-0000-0000-0000-000000000001', 'demo@partnerscout.ai');

-- ============================================================================
-- DEMO DISCOVERY JOB (Completed)
-- ============================================================================

INSERT INTO discovery_jobs (
    id, 
    user_id, 
    name, 
    brand_description, 
    reference_profiles, 
    status,
    profiles_discovered,
    profiles_scored
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',  -- Replace with real user UUID
    'Sustainable Fashion Discovery',
    'Eco-friendly sustainable fashion brand targeting millennials who value ethical production and minimalist aesthetics.',
    ARRAY['https://instagram.com/everlane', 'https://instagram.com/reformation', 'https://instagram.com/patagonia'],
    'completed',
    5,
    5
);

-- ============================================================================
-- DEMO BRAND DNA
-- ============================================================================

INSERT INTO brand_dna (
    id,
    job_id, 
    hashtags, 
    keywords,
    competitors,
    analysis
) VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    ARRAY['#sustainablefashion', '#ecofriendly', '#ethicalfashion', '#slowfashion', '#consciousfashion', '#minimalistfashion', '#capsulewardrobe', '#sustainablestyle'],
    ARRAY['sustainable', 'ethical', 'eco-friendly', 'minimalist', 'conscious', 'organic', 'fair-trade', 'transparency', 'capsule wardrobe', 'timeless style'],
    ARRAY['everlane', 'reformation', 'patagonia'],
    '{"style": "minimalist", "values": ["sustainability", "transparency", "quality"], "target_audience": "eco-conscious millennials"}'::jsonb
);

-- ============================================================================
-- DEMO PROFILES - Mix of genuine and fake for testing
-- ============================================================================

-- Profile 1: High-quality genuine profile (should score 85+)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, profile_picture_url, bio,
    followers, following, posts_count, engagement_rate, is_verified, is_business,
    external_url, business_email, business_category, following_ratio, status
) VALUES (
    'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/eco_boutique_nyc',
    'eco_boutique_nyc',
    'Eco Boutique NYC',
    'https://picsum.photos/seed/eco1/150/150',
    '🌿 Sustainable fashion boutique in Brooklyn. Curated ethical brands. Shop consciously. 📧 hello@ecoboutique.nyc',
    45000,
    1200,
    520,
    3.5,
    false,
    true,
    'https://ecoboutique.nyc',
    'hello@ecoboutique.nyc',
    'Clothing Store',
    0.027,
    'done'
);

-- Profile 2: Good quality genuine profile (should score 70-85)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, profile_picture_url, bio,
    followers, following, posts_count, engagement_rate, is_verified, is_business,
    external_url, business_email, business_category, following_ratio, status
) VALUES (
    'bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/sustainable_style_co',
    'sustainable_style_co',
    'Sustainable Style Co',
    'https://picsum.photos/seed/sus1/150/150',
    'Ethical fashion for the modern woman ✨ Free shipping on orders $75+',
    28000,
    890,
    340,
    4.2,
    false,
    true,
    'https://sustainablestyle.co',
    'contact@sustainablestyle.co',
    'Clothing Store',
    0.032,
    'done'
);

-- Profile 3: Suspicious profile (high following ratio, should score 30-50)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, profile_picture_url, bio,
    followers, following, posts_count, engagement_rate, is_verified, is_business,
    external_url, business_email, business_category, following_ratio, status
) VALUES (
    'cccc3333-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/fashion_deals_daily',
    'fashion_deals_daily',
    'Fashion Deals 🔥',
    'https://picsum.photos/seed/fake1/150/150',
    'Best deals! DM for promos 💰💰💰 Follow for follows!',
    52000,
    48500,
    45,
    0.3,
    false,
    false,
    null,
    null,
    null,
    0.933,
    'done'
);

-- Profile 4: Fake/bot profile (should score < 30, status: skipped)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, profile_picture_url, bio,
    followers, following, posts_count, engagement_rate, is_verified, is_business,
    external_url, business_email, business_category, following_ratio, status
) VALUES (
    'dddd4444-dddd-dddd-dddd-dddddddddddd',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/bot_follower_farm',
    'bot_follower_farm',
    'Get Followers Fast',
    'https://picsum.photos/seed/bot1/150/150',
    'Get 10K followers in 24hrs! DM NOW! 🚀🚀🚀',
    85000,
    78000,
    12,
    0.1,
    false,
    false,
    null,
    null,
    null,
    0.918,
    'skipped'
);

-- Profile 5: Verified excellent profile (should score 90+)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, profile_picture_url, bio,
    followers, following, posts_count, engagement_rate, is_verified, is_business,
    external_url, business_email, business_category, following_ratio, status
) VALUES (
    'eeee5555-eeee-eeee-eeee-eeeeeeeeeeee',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/green_threads_la',
    'green_threads_la',
    'Green Threads LA',
    'https://picsum.photos/seed/green1/150/150',
    'Plant-based fashion brand 🌱 Made in LA. Organic cotton. Carbon neutral.',
    67000,
    2100,
    890,
    5.1,
    true,
    true,
    'https://greenthreads.la',
    'partnerships@greenthreads.la',
    'Clothing Brand',
    0.031,
    'done'
);

-- ============================================================================
-- DEMO PROFILE SCORES (PRD 5.3 - 6 Dimensions)
-- ============================================================================

-- Score for eco_boutique_nyc (87 - Excellent)
INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning
) VALUES (
    'score-001-0000-0000-000000000001',
    'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    87,
    92, 88, 82, 95, 90, 85,
    '{"summary": "Excellent match for sustainable fashion brand. Strong visual alignment with minimalist aesthetic. High-quality genuine following with excellent engagement.", "recommendation": "Highly recommended for partnership outreach.", "visual_notes": "Clean, minimalist feed with earth tones matching brand aesthetic.", "content_notes": "Consistent sustainable fashion messaging aligned with brand values.", "engagement_notes": "3.5% engagement rate indicates genuine, engaged audience.", "authenticity_notes": "Low following ratio (0.027), high post count - genuine profile.", "business_notes": "Business account with email, website, and category.", "activity_notes": "Active posting schedule, recent content within last week."}'::jsonb
);

-- Score for sustainable_style_co (78 - Good)
INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning
) VALUES (
    'score-002-0000-0000-000000000002',
    'bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    78,
    80, 82, 88, 90, 85, 75,
    '{"summary": "Good match with strong content alignment. Genuine profile with above-average engagement.", "recommendation": "Recommended for partnership consideration.", "visual_notes": "Aesthetic partially aligned, some variance in style.", "content_notes": "Strong ethical fashion focus.", "engagement_notes": "4.2% engagement rate - excellent for follower count.", "authenticity_notes": "Genuine profile indicators across all metrics.", "business_notes": "Full business presence verified.", "activity_notes": "Consistent but slightly less frequent posting."}'::jsonb
);

-- Score for fashion_deals_daily (32 - Suspicious)
INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning
) VALUES (
    'score-003-0000-0000-000000000003',
    'cccc3333-cccc-cccc-cccc-cccccccccccc',
    32,
    25, 20, 15, 35, 20, 60,
    '{"summary": "Poor match. Multiple fake profile indicators detected. Not recommended.", "recommendation": "Skip - likely engagement farm or spam account.", "visual_notes": "Inconsistent visual style, promotional content.", "content_notes": "Generic deals content, no brand alignment.", "engagement_notes": "0.3% engagement rate - suspiciously low for follower count.", "authenticity_notes": "WARNING: Following ratio 0.93, only 45 posts for 52K followers.", "business_notes": "No business account, no email, no website.", "activity_notes": "Sporadic posting pattern."}'::jsonb
);

-- Score for bot_follower_farm (18 - Fake)
INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning
) VALUES (
    'score-004-0000-0000-000000000004',
    'dddd4444-dddd-dddd-dddd-dddddddddddd',
    18,
    10, 5, 5, 10, 10, 40,
    '{"summary": "Fake/bot account. All indicators point to purchased followers or bot farm.", "recommendation": "SKIP - Bot/fake account detected.", "visual_notes": "Promotional spam content only.", "content_notes": "No relevant content, follower-selling messaging.", "engagement_notes": "0.1% engagement - definitively fake.", "authenticity_notes": "CRITICAL: 12 posts for 85K followers, following ratio 0.92.", "business_notes": "No business indicators whatsoever.", "activity_notes": "Minimal posting activity."}'::jsonb
);

-- Score for green_threads_la (94 - Excellent, Verified)
INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning
) VALUES (
    'score-005-0000-0000-000000000005',
    'eeee5555-eeee-eeee-eeee-eeeeeeeeeeee',
    94,
    95, 96, 92, 98, 100, 90,
    '{"summary": "Exceptional match. Verified account with perfect brand alignment and excellent engagement.", "recommendation": "Priority outreach recommended - ideal partner.", "visual_notes": "Perfect aesthetic match with sustainable fashion focus.", "content_notes": "Organic, carbon neutral messaging perfectly aligned.", "engagement_notes": "5.1% engagement - exceptional for 67K followers.", "authenticity_notes": "Verified account, genuine organic growth indicators.", "business_notes": "Complete business profile with partnership email.", "activity_notes": "High activity, consistent posting schedule."}'::jsonb
);

-- ============================================================================
-- DEMO PROFILE CONTACTS
-- ============================================================================

INSERT INTO profile_contacts (profile_id, email, source) VALUES
    ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'hello@ecoboutique.nyc', 'business_email'),
    ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'contact@sustainablestyle.co', 'business_email'),
    ('eeee5555-eeee-eeee-eeee-eeeeeeeeeeee', 'partnerships@greenthreads.la', 'business_email');

-- Note: No contacts for fake profiles (cccc3333, dddd4444)

-- ============================================================================
-- ADDITIONAL DEMO JOBS (Different Statuses for Testing)
-- ============================================================================

-- Pending job
INSERT INTO discovery_jobs (
    id, user_id, name, brand_description, reference_profiles, status
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'Fitness Brand Partners',
    'Premium fitness apparel brand focused on high-performance athletes.',
    ARRAY['https://instagram.com/lululemon', 'https://instagram.com/gymshark'],
    'pending'
);

-- In-progress (scoring) job
INSERT INTO discovery_jobs (
    id, user_id, name, brand_description, reference_profiles, status, profiles_discovered, profiles_scored
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    '00000000-0000-0000-0000-000000000001',
    'Beauty Brand Search',
    'Clean beauty brand with focus on natural ingredients.',
    ARRAY['https://instagram.com/glossier'],
    'scoring',
    12,
    5
);

-- Failed job (for retry testing)
INSERT INTO discovery_jobs (
    id, user_id, name, brand_description, reference_profiles, status
) VALUES (
    '44444444-4444-4444-4444-444444444444',
    '00000000-0000-0000-0000-000000000001',
    'Failed Discovery Test',
    'Test brand for failure scenarios.',
    ARRAY['https://instagram.com/invalid_profile_404'],
    'failed'
);

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these to verify seed data is correct
-- ============================================================================

-- SELECT * FROM v_job_summary;
-- SELECT * FROM v_complete_profiles WHERE job_id = '11111111-1111-1111-1111-111111111111';
-- SELECT * FROM v_high_score_profiles;
-- SELECT * FROM v_suspicious_profiles;
