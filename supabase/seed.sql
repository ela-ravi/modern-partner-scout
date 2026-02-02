-- ============================================================================
-- PartnerScout AI - Seed Data
-- Description: Sample data for development and testing
-- Run AFTER applying all migrations (001, 002, 003)
-- ============================================================================

-- ============================================================================
-- SAMPLE DISCOVERY JOB
-- ============================================================================

INSERT INTO discovery_jobs (
    id,
    user_id,
    name,
    brand_description,
    reference_profiles,
    follower_range_min,
    follower_range_max,
    discovery_limit,
    status,
    profiles_discovered,
    profiles_scored
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    NULL,  -- Will be NULL until you have auth.users set up; replace with actual user_id
    'Sustainable Fashion Discovery',
    'Sustainable fashion brand focused on eco-friendly materials and ethical production. We target conscious consumers aged 25-40 who value quality over quantity and care about environmental impact.',
    ARRAY[
        'https://instagram.com/everlane', 
        'https://instagram.com/reformation', 
        'https://instagram.com/patagonia'
    ],
    10000,
    500000,
    50,
    'completed',
    3,
    3
) ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SAMPLE BRAND DNA
-- ============================================================================

INSERT INTO brand_dna (
    id,
    job_id,
    hashtags,
    keywords,
    visual_themes,
    content_pillars,
    target_audience_description
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    ARRAY[
        '#sustainablefashion', 
        '#slowfashion', 
        '#ethicalfashion', 
        '#ecofriendly', 
        '#consciousfashion', 
        '#sustainablestyle', 
        '#greenfashion', 
        '#fairfashion'
    ],
    ARRAY[
        'sustainable', 
        'ethical', 
        'eco-friendly', 
        'organic', 
        'fair trade', 
        'conscious', 
        'minimal waste', 
        'recycled materials'
    ],
    ARRAY[
        'minimalist aesthetic', 
        'earth tones', 
        'natural textures', 
        'clean backgrounds', 
        'lifestyle shots'
    ],
    ARRAY[
        'sustainability education', 
        'behind-the-scenes production', 
        'styling tips', 
        'brand values', 
        'customer stories'
    ],
    'Environmentally conscious millennials and Gen Z, primarily women aged 25-40, who prioritize quality and ethics over fast fashion'
) ON CONFLICT (job_id) DO NOTHING;

-- ============================================================================
-- SAMPLE DISCOVERED PROFILES
-- ============================================================================

-- Profile 1: High score partner (excellent match)
INSERT INTO discovered_profiles (
    id,
    job_id,
    instagram_url,
    username,
    full_name,
    bio,
    profile_picture_url,
    followers_count,
    following_count,
    posts_count,
    engagement_rate,
    following_ratio,
    is_verified,
    is_business_account,
    external_url,
    business_email,
    business_category,
    status
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/eco_style_blogger',
    'eco_style_blogger',
    'Emma Green',
    'Sustainable fashion advocate 🌿 | Helping you build a conscious wardrobe | Slow fashion tips & ethical brands | DM for collabs | emma@ecostyle.com',
    'https://example.com/avatars/emma.jpg',
    125000,
    850,
    320,
    2.80,
    0.007,
    false,
    true,
    'https://ecostyle.blog',
    'emma@ecostyle.com',
    'Blogger/Creator',
    'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- Profile 2: Medium score partner (good match)
INSERT INTO discovered_profiles (
    id,
    job_id,
    instagram_url,
    username,
    full_name,
    bio,
    profile_picture_url,
    followers_count,
    following_count,
    posts_count,
    engagement_rate,
    following_ratio,
    is_verified,
    is_business_account,
    external_url,
    business_email,
    business_category,
    status
) VALUES (
    '44444444-4444-4444-4444-444444444444',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/mindful_minimalist',
    'mindful_minimalist',
    'Sarah Chen',
    'Living with less ✨ | Capsule wardrobe tips | Sustainable living | Minimalist lifestyle | Contact via link 👇',
    'https://example.com/avatars/sarah.jpg',
    75000,
    420,
    180,
    2.10,
    0.006,
    false,
    true,
    'https://linktree.com/mindfulminimalist',
    NULL,
    'Personal Blog',
    'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- Profile 3: Lower score partner (still above threshold)
INSERT INTO discovered_profiles (
    id,
    job_id,
    instagram_url,
    username,
    full_name,
    bio,
    profile_picture_url,
    followers_count,
    following_count,
    posts_count,
    engagement_rate,
    following_ratio,
    is_verified,
    is_business_account,
    external_url,
    business_email,
    business_category,
    status
) VALUES (
    '55555555-5555-5555-5555-555555555555',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/green_lifestyle_tips',
    'green_lifestyle_tips',
    'Alex Martinez',
    'Eco-conscious living 🌎 | Fashion | Home | Travel | Tips for sustainable lifestyle | PR inquiries welcome',
    'https://example.com/avatars/alex.jpg',
    45000,
    1200,
    450,
    1.50,
    0.027,
    false,
    false,
    NULL,
    NULL,
    NULL,
    'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- ============================================================================
-- SAMPLE PROFILE SCORES
-- ============================================================================

-- Score for eco_style_blogger (high score - highly recommended)
INSERT INTO profile_scores (
    id,
    profile_id,
    visual_aesthetic_match,
    content_theme_alignment,
    engagement_rate_score,
    follower_quality,
    business_indicators,
    activity_recency,
    final_score,
    recommendation,
    reasoning,
    is_fake_suspected
) VALUES (
    '66666666-6666-6666-6666-666666666666',
    '33333333-3333-3333-3333-333333333333',
    88,
    92,
    85,
    78,
    95,
    90,
    88,
    'highly_recommended',
    '{
        "visual": "Clean, minimalist aesthetic with earth tones matching brand identity perfectly",
        "content": "Strong focus on sustainable fashion education and conscious consumption",
        "engagement": "Healthy 2.8% engagement rate with authentic, thoughtful comments",
        "followers": "Quality audience with genuine interest in sustainability topics",
        "business": "Professional setup with clear contact info and business email in bio",
        "activity": "Consistent posting schedule with recent content (3-4 posts/week)",
        "summary": "Excellent match for partnership. Strong alignment with brand values and engaged audience.",
        "recommendation": "Highly recommended for outreach - ideal partnership candidate"
    }'::jsonb,
    false
) ON CONFLICT (profile_id) DO NOTHING;

-- Score for mindful_minimalist (medium score - recommended)
INSERT INTO profile_scores (
    id,
    profile_id,
    visual_aesthetic_match,
    content_theme_alignment,
    engagement_rate_score,
    follower_quality,
    business_indicators,
    activity_recency,
    final_score,
    recommendation,
    reasoning,
    is_fake_suspected
) VALUES (
    '77777777-7777-7777-7777-777777777777',
    '44444444-4444-4444-4444-444444444444',
    75,
    82,
    70,
    72,
    80,
    85,
    76,
    'recommended',
    '{
        "visual": "Good aesthetic alignment with minimal, clean visuals",
        "content": "Capsule wardrobe focus aligns well with sustainable fashion messaging",
        "engagement": "Moderate 2.1% engagement rate - slightly below optimal",
        "followers": "Decent audience quality, some inactive followers detected",
        "business": "Business account with linktree for contact",
        "activity": "Regular posting with good content consistency",
        "summary": "Good match with room for growth. Content aligns with brand values.",
        "recommendation": "Recommended for outreach - solid partnership potential"
    }'::jsonb,
    false
) ON CONFLICT (profile_id) DO NOTHING;

-- Score for green_lifestyle_tips (lower score - consider)
INSERT INTO profile_scores (
    id,
    profile_id,
    visual_aesthetic_match,
    content_theme_alignment,
    engagement_rate_score,
    follower_quality,
    business_indicators,
    activity_recency,
    final_score,
    recommendation,
    reasoning,
    is_fake_suspected
) VALUES (
    '88888888-8888-8888-8888-888888888888',
    '55555555-5555-5555-5555-555555555555',
    62,
    68,
    55,
    58,
    50,
    75,
    61,
    'consider',
    '{
        "visual": "Varied aesthetic, not as focused on fashion specifically",
        "content": "Broader lifestyle content where fashion is secondary topic",
        "engagement": "Lower engagement at 1.5% - below industry average",
        "followers": "Mixed audience quality, higher following ratio raises concerns",
        "business": "No clear business contact or professional setup",
        "activity": "Good posting frequency but inconsistent quality",
        "summary": "Moderate match. Content is relevant but not highly focused on fashion.",
        "recommendation": "Consider for outreach if other options are limited"
    }'::jsonb,
    false
) ON CONFLICT (profile_id) DO NOTHING;

-- ============================================================================
-- SAMPLE PROFILE CONTACTS
-- ============================================================================

-- Contact for eco_style_blogger
INSERT INTO profile_contacts (
    id,
    profile_id,
    email,
    email_source,
    phone,
    website,
    other_contacts
) VALUES (
    '99999999-9999-9999-9999-999999999999',
    '33333333-3333-3333-3333-333333333333',
    'emma@ecostyle.com',
    'bio',
    NULL,
    'https://ecostyle.blog',
    '{"instagram_dm": true}'::jsonb
) ON CONFLICT (profile_id) DO NOTHING;

-- Contact for mindful_minimalist
INSERT INTO profile_contacts (
    id,
    profile_id,
    email,
    email_source,
    phone,
    website,
    other_contacts
) VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-bbbbbbbbbbbb',
    '44444444-4444-4444-4444-444444444444',
    NULL,
    NULL,
    NULL,
    'https://linktree.com/mindfulminimalist',
    '{"linktree": "https://linktree.com/mindfulminimalist"}'::jsonb
) ON CONFLICT (profile_id) DO NOTHING;

-- No contact for green_lifestyle_tips (demonstrates missing contact scenario)

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- After running this seed file, verify with:
--
-- SELECT COUNT(*) as jobs FROM discovery_jobs;               -- Expected: 1
-- SELECT COUNT(*) as brand_dnas FROM brand_dna;              -- Expected: 1
-- SELECT COUNT(*) as profiles FROM discovered_profiles;       -- Expected: 3
-- SELECT COUNT(*) as scores FROM profile_scores;              -- Expected: 3
-- SELECT COUNT(*) as contacts FROM profile_contacts;          -- Expected: 2
--
-- View complete profiles with scores:
-- SELECT username, final_score, recommendation, contact_email 
-- FROM v_complete_profiles 
-- WHERE job_id = '11111111-1111-1111-1111-111111111111'
-- ORDER BY final_score DESC;
--
-- View job summary:
-- SELECT * FROM v_job_summary WHERE job_id = '11111111-1111-1111-1111-111111111111';
