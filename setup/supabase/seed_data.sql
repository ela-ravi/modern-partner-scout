-- ============================================================================
-- PartnerScout AI - Seed Data
-- ============================================================================
-- Run this AFTER creating the tables with all_migrations.sql
-- ============================================================================

-- ============================================================================
-- STEP 1: Create Demo User
-- ============================================================================

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
    is_super_admin,
    confirmation_token,
    recovery_token,
    email_change_token_new,
    email_change
) 
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'authenticated',
    'authenticated',
    'demo@partnerscout.ai',
    crypt('DemoPassword123!', gen_salt('bf')),
    NOW(),
    NOW(),
    NOW(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Demo User"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
WHERE NOT EXISTS (
    SELECT 1 FROM auth.users WHERE id = '11111111-1111-1111-1111-111111111111'
);

-- ============================================================================
-- STEP 2: Insert Discovery Jobs (all 6 statuses)
-- ============================================================================

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
-- Completed job with profiles
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'Sustainable Fashion Discovery',
    'Eco-friendly sustainable fashion brand targeting millennials who value ethical production.',
    ARRAY['https://instagram.com/everlane', 'https://instagram.com/reformation', 'https://instagram.com/patagonia'],
    'completed',
    5,
    5,
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days'
),
-- Scoring in progress
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
-- Pending job
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    'Tech Accessories Search',
    'Premium tech accessories for professionals.',
    ARRAY[]::TEXT[],
    'pending',
    0,
    0,
    NOW() - INTERVAL '3 hours',
    NOW() - INTERVAL '3 hours'
),
-- Analyzing job
(
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    '11111111-1111-1111-1111-111111111111',
    'Beauty Brand Discovery',
    'Clean beauty brand with natural ingredients.',
    ARRAY['https://instagram.com/glossier'],
    'analyzing',
    0,
    0,
    NOW() - INTERVAL '30 minutes',
    NOW() - INTERVAL '30 minutes'
),
-- Discovering job
(
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    '11111111-1111-1111-1111-111111111111',
    'Home Decor Partners',
    'Minimalist home decor brand.',
    ARRAY['https://instagram.com/westelm'],
    'discovering',
    2,
    0,
    NOW() - INTERVAL '15 minutes',
    NOW() - INTERVAL '15 minutes'
),
-- Failed job
(
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    '11111111-1111-1111-1111-111111111111',
    'Failed Discovery Test',
    'Test brand for failure scenarios.',
    ARRAY['https://instagram.com/invalid_profile_404'],
    'failed',
    0,
    0,
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STEP 3: Insert Brand DNA
-- ============================================================================

INSERT INTO brand_dna (
    id,
    job_id,
    hashtags,
    keywords,
    competitors,
    analysis,
    created_at
)
VALUES (
    'a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    ARRAY['#sustainablefashion', '#ecofriendly', '#ethicalfashion', '#slowfashion'],
    ARRAY['sustainable', 'ethical', 'eco-friendly', 'minimalist', 'organic'],
    ARRAY['everlane', 'reformation', 'patagonia'],
    '{"style": "minimalist", "values": ["sustainability", "transparency"], "target_audience": "eco-conscious millennials"}'::jsonb,
    NOW() - INTERVAL '2 days'
)
ON CONFLICT (job_id) DO NOTHING;

-- ============================================================================
-- STEP 4: Insert Discovered Profiles (mix of genuine and suspicious)
-- ============================================================================

INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, bio,
    followers, following, posts_count, engagement_rate,
    is_verified, is_business, external_url, business_email,
    business_category, following_ratio, status, created_at
)
VALUES
-- Profile 1: High-quality genuine (score ~87)
(
    'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/eco_boutique_nyc',
    'eco_boutique_nyc',
    'Eco Boutique NYC',
    'Sustainable fashion boutique in Brooklyn. Curated ethical brands.',
    45000, 1200, 520, 3.5,
    false, true, 'https://ecoboutique.nyc', 'hello@ecoboutique.nyc',
    'Clothing Store', 0.027, 'done', NOW() - INTERVAL '2 days'
),
-- Profile 2: Good quality genuine (score ~78)
(
    'a2a2a2a2-a2a2-a2a2-a2a2-a2a2a2a2a2a2',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/sustainable_style_co',
    'sustainable_style_co',
    'Sustainable Style Co',
    'Ethical fashion for the modern woman. Free shipping on orders $75+',
    28000, 890, 340, 4.2,
    false, true, 'https://sustainablestyle.co', 'contact@sustainablestyle.co',
    'Clothing Store', 0.032, 'done', NOW() - INTERVAL '2 days'
),
-- Profile 3: Suspicious (high following ratio, score ~32)
(
    'a3a3a3a3-a3a3-a3a3-a3a3-a3a3a3a3a3a3',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/fashion_deals_daily',
    'fashion_deals_daily',
    'Fashion Deals',
    'Best deals! DM for promos. Follow for follows!',
    52000, 48500, 45, 0.3,
    false, false, NULL, NULL,
    NULL, 0.933, 'done', NOW() - INTERVAL '2 days'
),
-- Profile 4: Fake/bot (score ~18)
(
    'a4a4a4a4-a4a4-a4a4-a4a4-a4a4a4a4a4a4',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/bot_follower_farm',
    'bot_follower_farm',
    'Get Followers Fast',
    'Get 10K followers in 24hrs! DM NOW!',
    85000, 78000, 12, 0.1,
    false, false, NULL, NULL,
    NULL, 0.918, 'skipped', NOW() - INTERVAL '2 days'
),
-- Profile 5: Verified excellent (score ~94)
(
    'a5a5a5a5-a5a5-a5a5-a5a5-a5a5a5a5a5a5',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'https://instagram.com/green_threads_la',
    'green_threads_la',
    'Green Threads LA',
    'Plant-based fashion brand. Made in LA. Organic cotton. Carbon neutral.',
    67000, 2100, 890, 5.1,
    true, true, 'https://greenthreads.la', 'partnerships@greenthreads.la',
    'Clothing Brand', 0.031, 'done', NOW() - INTERVAL '2 days'
)
ON CONFLICT (job_id, instagram_url) DO NOTHING;

-- ============================================================================
-- STEP 5: Insert Profile Scores (6 dimensions per PRD 5.3)
-- ============================================================================

INSERT INTO profile_scores (
    id, profile_id, score,
    visual_aesthetic_match, content_theme_alignment, engagement_rate_score,
    follower_quality, business_indicators, activity_recency,
    reasoning, created_at
)
VALUES
-- Score for eco_boutique_nyc (87 - Excellent)
(
    'b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1',
    'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1',
    87,
    92, 88, 82, 95, 90, 85,
    '{"summary": "Excellent match for sustainable fashion brand.", "recommendation": "Highly recommended for partnership."}'::jsonb,
    NOW() - INTERVAL '2 days'
),
-- Score for sustainable_style_co (78 - Good)
(
    'b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2',
    'a2a2a2a2-a2a2-a2a2-a2a2-a2a2a2a2a2a2',
    78,
    80, 82, 88, 90, 85, 75,
    '{"summary": "Good match with strong content alignment.", "recommendation": "Recommended for partnership."}'::jsonb,
    NOW() - INTERVAL '2 days'
),
-- Score for fashion_deals_daily (32 - Suspicious)
(
    'b3b3b3b3-b3b3-b3b3-b3b3-b3b3b3b3b3b3',
    'a3a3a3a3-a3a3-a3a3-a3a3-a3a3a3a3a3a3',
    32,
    25, 20, 15, 35, 20, 60,
    '{"summary": "Poor match. Multiple fake indicators detected.", "recommendation": "Skip - likely spam account."}'::jsonb,
    NOW() - INTERVAL '2 days'
),
-- Score for bot_follower_farm (18 - Fake)
(
    'b4b4b4b4-b4b4-b4b4-b4b4-b4b4b4b4b4b4',
    'a4a4a4a4-a4a4-a4a4-a4a4-a4a4a4a4a4a4',
    18,
    10, 5, 5, 10, 10, 40,
    '{"summary": "Fake/bot account detected.", "recommendation": "SKIP - Bot/fake account."}'::jsonb,
    NOW() - INTERVAL '2 days'
),
-- Score for green_threads_la (94 - Excellent)
(
    'b5b5b5b5-b5b5-b5b5-b5b5-b5b5b5b5b5b5',
    'a5a5a5a5-a5a5-a5a5-a5a5-a5a5a5a5a5a5',
    94,
    95, 96, 92, 98, 100, 90,
    '{"summary": "Exceptional match. Verified account with perfect alignment.", "recommendation": "Priority outreach."}'::jsonb,
    NOW() - INTERVAL '2 days'
)
ON CONFLICT (profile_id) DO NOTHING;

-- ============================================================================
-- STEP 6: Insert Profile Contacts
-- ============================================================================

INSERT INTO profile_contacts (id, profile_id, email, source, confidence, created_at)
VALUES
(
    'c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1',
    'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1',
    'hello@ecoboutique.nyc',
    'business_email',
    0.95,
    NOW() - INTERVAL '2 days'
),
(
    'c2c2c2c2-c2c2-c2c2-c2c2-c2c2c2c2c2c2',
    'a2a2a2a2-a2a2-a2a2-a2a2-a2a2a2a2a2a2',
    'contact@sustainablestyle.co',
    'business_email',
    0.92,
    NOW() - INTERVAL '2 days'
),
(
    'c5c5c5c5-c5c5-c5c5-c5c5-c5c5c5c5c5c5',
    'a5a5a5a5-a5a5-a5a5-a5a5-a5a5a5a5a5a5',
    'partnerships@greenthreads.la',
    'business_email',
    0.98,
    NOW() - INTERVAL '2 days'
)
ON CONFLICT (profile_id) DO NOTHING;

-- ============================================================================
-- VERIFICATION: Check what was inserted
-- ============================================================================

SELECT 'discovery_jobs' as table_name, COUNT(*) as count FROM discovery_jobs
UNION ALL
SELECT 'brand_dna', COUNT(*) FROM brand_dna
UNION ALL
SELECT 'discovered_profiles', COUNT(*) FROM discovered_profiles
UNION ALL
SELECT 'profile_scores', COUNT(*) FROM profile_scores
UNION ALL
SELECT 'profile_contacts', COUNT(*) FROM profile_contacts;
