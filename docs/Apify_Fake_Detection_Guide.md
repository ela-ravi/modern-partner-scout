# Fake vs Genuine Instagram Profile Detection using Apify

This guide explains how to use the Apify Instagram Profile Scraper to detect fake/bot accounts and identify genuine profiles for partnership outreach.

---

## Overview

The detection algorithm analyzes several signals from Instagram profile data to calculate an authenticity score (0-100). Profiles scoring below 50 are flagged as potentially fake.

---

## Step 1: Run Apify Instagram Scraper

Replace `YOUR_APIFY_API_KEY` with your actual key.

### Option A: Scrape Single Profile

```bash
curl -X POST "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token=YOUR_APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "usernames": ["luxe_boutique_paris"],
    "resultsLimit": 30
  }'
```

### Option B: Scrape Multiple Profiles (Compare Reference vs Candidate)

```bash
curl -X POST "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token=YOUR_APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "usernames": [
      "daboraparis",
      "jovabordeaux",
      "perflounge_eu",
      "suspect_fake_account123"
    ],
    "resultsLimit": 30
  }'
```

### Response (you'll get a run ID):

```json
{
  "data": {
    "id": "abc123xyz",
    "status": "RUNNING",
    "defaultDatasetId": "dataset123"
  }
}
```

---

## Step 2: Check Run Status

```bash
curl "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs/abc123xyz?token=YOUR_APIFY_API_KEY"
```

Wait until status is `"SUCCEEDED"`.

---

## Step 3: Get Results

```bash
curl "https://api.apify.com/v2/datasets/dataset123/items?token=YOUR_APIFY_API_KEY" \
  -o instagram_profiles.json
```

This downloads the scraped data to `instagram_profiles.json`.

---

## Step 4: Analyze for Fake vs Genuine

### Quick Script

Save this as `analyze_profile.sh`:

```bash
#!/bin/bash
# Usage: ./analyze_profile.sh instagram_profiles.json

FILE=$1

echo "======================================"
echo "FAKE vs GENUINE PROFILE ANALYZER"
echo "======================================"

# Parse each profile using jq
cat $FILE | jq -r '.[] | @base64' | while read profile; do
  _decode() {
    echo "$profile" | base64 --decode | jq -r "$1"
  }

  USERNAME=$(_decode '.username')
  FOLLOWERS=$(_decode '.followersCount')
  FOLLOWING=$(_decode '.followsCount // .followingCount // 0')
  POSTS=$(_decode '.postsCount // 0')
  IS_BUSINESS=$(_decode '.isBusinessAccount // false')
  HAS_EMAIL=$(_decode 'if .businessEmail then "Yes" else "No" end')
  HAS_WEBSITE=$(_decode 'if .externalUrl then "Yes" else "No" end')
  BIO=$(_decode '.biography // ""')

  echo ""
  echo "📱 @$USERNAME"
  echo "───────────────────────────────"
  echo "Followers: $FOLLOWERS"
  echo "Following: $FOLLOWING"
  echo "Posts: $POSTS"
  echo "Business Account: $IS_BUSINESS"
  echo "Has Email: $HAS_EMAIL"
  echo "Has Website: $HAS_WEBSITE"

  # Calculate ratios
  if [ "$FOLLOWERS" -gt 0 ]; then
    RATIO=$(echo "scale=2; $FOLLOWING / $FOLLOWERS" | bc)
  else
    RATIO=999
  fi

  echo ""
  echo "🔍 ANALYSIS:"

  SCORE=100
  FLAGS=""

  # Check 1: Following/Follower ratio
  if (( $(echo "$RATIO > 2" | bc -l) )); then
    FLAGS="$FLAGS ❌ High following/follower ratio ($RATIO) - SUSPICIOUS"
    SCORE=$((SCORE - 30))
  elif (( $(echo "$RATIO > 1.5" | bc -l) )); then
    FLAGS="$FLAGS ⚠️ Elevated following/follower ratio ($RATIO)"
    SCORE=$((SCORE - 15))
  else
    FLAGS="$FLAGS ✅ Normal following/follower ratio ($RATIO)"
  fi

  # Check 2: Posts vs Followers
  if [ "$FOLLOWERS" -gt 5000 ] && [ "$POSTS" -lt 20 ]; then
    FLAGS="$FLAGS\n❌ Too few posts ($POSTS) for follower count ($FOLLOWERS) - SUSPICIOUS"
    SCORE=$((SCORE - 25))
  elif [ "$POSTS" -gt 50 ]; then
    FLAGS="$FLAGS\n✅ Good post history ($POSTS posts)"
  fi

  # Check 3: Business indicators
  if [ "$IS_BUSINESS" = "true" ]; then
    FLAGS="$FLAGS\n✅ Business account verified"
    SCORE=$((SCORE + 5))
  fi

  if [ "$HAS_EMAIL" = "Yes" ]; then
    FLAGS="$FLAGS\n✅ Email available"
    SCORE=$((SCORE + 5))
  else
    FLAGS="$FLAGS\n⚠️ No email found"
  fi

  if [ "$HAS_WEBSITE" = "Yes" ]; then
    FLAGS="$FLAGS\n✅ Website linked"
    SCORE=$((SCORE + 5))
  else
    FLAGS="$FLAGS\n⚠️ No website"
  fi

  # Cap score
  if [ $SCORE -gt 100 ]; then SCORE=100; fi
  if [ $SCORE -lt 0 ]; then SCORE=0; fi

  echo -e "$FLAGS"
  echo ""

  # Verdict
  if [ $SCORE -ge 70 ]; then
    echo "✅ VERDICT: GENUINE PROFILE (Score: $SCORE/100)"
  elif [ $SCORE -ge 50 ]; then
    echo "⚠️ VERDICT: POSSIBLY GENUINE (Score: $SCORE/100)"
  else
    echo "❌ VERDICT: LIKELY FAKE (Score: $SCORE/100)"
  fi

  echo "======================================"
done
```

### Run it:

```bash
chmod +x analyze_profile.sh
./analyze_profile.sh instagram_profiles.json
```

---

## Alternative: One-Liner Quick Check

If you just want to quickly check one profile's key metrics:

```bash
# After downloading instagram_profiles.json
cat instagram_profiles.json | jq '.[] | {
  username: .username,
  followers: .followersCount,
  following: (.followsCount // .followingCount),
  posts: .postsCount,
  ratio: ((.followsCount // .followingCount) / .followersCount),
  is_business: .isBusinessAccount,
  has_email: (.businessEmail != null),
  has_website: (.externalUrl != null),
  verdict: (
    if ((.followsCount // .followingCount) / .followersCount) > 2 then "🚨 LIKELY FAKE"
    elif ((.followsCount // .followingCount) / .followersCount) > 1.5 then "⚠️ SUSPICIOUS"
    else "✅ LOOKS GENUINE"
    end
  )
}'
```

---

## Complete Test Flow (Copy-Paste Ready)

```bash
# 1. Set your API key
export APIFY_KEY="your_key_here"

# 2. Run scraper (test with known luxury boutiques)
RUN_RESPONSE=$(curl -s -X POST "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token=$APIFY_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "usernames": ["daboraparis", "nose_paris", "jovoy_paris"],
    "resultsLimit": 20
  }')

# 3. Extract run ID and dataset ID
RUN_ID=$(echo $RUN_RESPONSE | jq -r '.data.id')
DATASET_ID=$(echo $RUN_RESPONSE | jq -r '.data.defaultDatasetId')

echo "Run ID: $RUN_ID"
echo "Dataset ID: $DATASET_ID"

# 4. Wait for completion (check every 10 seconds)
while true; do
  STATUS=$(curl -s "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs/$RUN_ID?token=$APIFY_KEY" | jq -r '.data.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "SUCCEEDED" ]; then break; fi
  if [ "$STATUS" = "FAILED" ]; then echo "Run failed!"; exit 1; fi
  sleep 10
done

# 5. Download results
curl -s "https://api.apify.com/v2/datasets/$DATASET_ID/items?token=$APIFY_KEY" -o profiles.json

# 6. Quick analysis
echo ""
echo "=== PROFILE ANALYSIS ==="
cat profiles.json | jq '.[] | {
  username: .username,
  followers: .followersCount,
  following: (.followsCount // .followingCount // 0),
  posts: .postsCount,
  ratio: (((.followsCount // .followingCount // 1) / (.followersCount // 1)) | . * 100 | floor / 100),
  business: .isBusinessAccount,
  email: .businessEmail,
  website: .externalUrl,
  category: .businessCategoryName
}'
```

---

## Fake Profile Red Flags Cheat Sheet

| Signal | Genuine | Suspicious | Likely Fake |
|--------|---------|------------|-------------|
| Following/Follower Ratio | < 1.0 | 1.0 - 2.0 | > 2.0 |
| Posts vs Followers | 50+ posts for 5K followers | 20-50 posts | < 20 posts for 5K+ |
| Business Account | Yes | - | No |
| Email Available | Yes | - | No |
| Website Linked | Yes | - | No |
| Engagement Rate | > 2% | 1-2% | < 1% |
| Bio Quality | Detailed, professional | Generic | Empty/spam |
| Post Consistency | Regular (2-5/week) | Irregular | Burst then silent |

---

## Scoring Algorithm

```
Base Score: 100

Penalties:
- Following/Follower ratio > 2.0:     -30 points
- Following/Follower ratio > 1.5:     -15 points
- Too few posts for followers:        -25 points

Bonuses:
- Business account verified:          +5 points
- Email available:                    +5 points
- Website linked:                     +5 points

Final Score: Capped between 0-100

Verdict:
- Score >= 70: ✅ GENUINE PROFILE
- Score >= 50: ⚠️ POSSIBLY GENUINE
- Score < 50:  ❌ LIKELY FAKE
```

---

## Sample Output

### Genuine Profile Example

```
📱 @daboraparis
───────────────────────────────────
Followers: 28500
Following: 1200
Posts: 456
Business Account: true
Has Email: Yes
Has Website: Yes

🔍 ANALYSIS:
✅ Normal following/follower ratio (0.04)
✅ Good post history (456 posts)
✅ Business account verified
✅ Email available
✅ Website linked

✅ VERDICT: GENUINE PROFILE (Score: 100/100)
======================================
```

### Fake Profile Example

```
📱 @random_bot_12345
───────────────────────────────────
Followers: 15000
Following: 45000
Posts: 12
Business Account: false
Has Email: No
Has Website: No

🔍 ANALYSIS:
❌ High following/follower ratio (3.0) - SUSPICIOUS
❌ Too few posts (12) for follower count (15000) - SUSPICIOUS
⚠️ No email found
⚠️ No website

❌ VERDICT: LIKELY FAKE (Score: 25/100)
======================================
```

---

## Apify Output Fields Used

| Apify Field | Description | Used For |
|-------------|-------------|----------|
| `username` | Instagram handle | Identification |
| `followersCount` | Follower count | Ratio calculation |
| `followsCount` | Following count | Ratio calculation |
| `postsCount` | Total posts | Activity check |
| `isBusinessAccount` | Business account flag | Trust signal |
| `businessEmail` | Contact email | Trust signal |
| `externalUrl` | Website link | Trust signal |
| `businessCategoryName` | Business category | Context |
| `biography` | Profile bio | Quality check |

---

## Integration with PartnerScout AI

This detection logic is integrated into the **Scorer Agent** as the `follower_quality` dimension (15% weight). See:

- [Agents_Documentation.md](./Agents_Documentation.md) - Section 4: Scorer Agent
- [Backend_Implementation_Guide.md](./Backend_Implementation_Guide.md) - Section 5.4: scoring.yaml
- [Supabase_Database_Guide.md](./Supabase_Database_Guide.md) - Section 3.5: Fake Detection




