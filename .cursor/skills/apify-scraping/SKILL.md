---
name: apify-scraping
description: Instagram data extraction using Apify for PartnerScout. Use for profile scraping, hashtag discovery, field mapping, fake detection signals, and error handling.
version: 1.0.0
---

# Apify Scraping Skill

Patterns for Apify Instagram scraping in PartnerScout.

## When to Use

- Configuring Apify Instagram actors
- Mapping response fields to database
- Calculating derived metrics
- Extracting fake detection signals
- Handling rate limiting and errors

## Guidelines

1. **Store profile data at discovery time** (not at scoring)
2. **Calculate following_ratio and engagement_rate**
3. **Extract business indicators** for fake detection
4. **Handle missing fields** gracefully
5. **Respect rate limits**

---

## Apify Actors

| Actor | Purpose |
|-------|---------|
| `apify/instagram-profile-scraper` | Scrape profile data |
| `apify/instagram-hashtag-scraper` | Find profiles by hashtag |
| `apify/instagram-post-scraper` | Scrape recent posts |

---

## Code Templates

### Apify Client

```python
from apify_client import ApifyClient
from app.core.config import settings

class ApifyService:
    def __init__(self):
        self.client = ApifyClient(settings.APIFY_API_KEY)
    
    async def scrape_profiles(self, urls: list[str]) -> list[dict]:
        run_input = {"directUrls": urls, "resultsLimit": len(urls), "resultsType": "details"}
        run = self.client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
        
        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(self._map_profile(item))
        return results
    
    async def discover_by_hashtags(self, hashtags: list[str], limit: int = 50) -> list[dict]:
        run_input = {"hashtags": hashtags, "resultsLimit": limit * 2, "resultsType": "posts"}
        run = self.client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
        
        profiles = {}
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            owner = item.get("ownerUsername")
            if owner and owner not in profiles:
                profiles[owner] = f"https://instagram.com/{owner}"
        
        return await self.scrape_profiles(list(profiles.values())[:limit])
```

### Field Mapping

```python
def _map_profile(self, raw: dict) -> dict:
    followers = raw.get("followersCount", 0) or 0
    following = raw.get("followsCount", 0) or 0
    
    following_ratio = round(following / followers, 2) if followers > 0 else None
    engagement_rate = self._calculate_engagement_rate(raw)
    
    return {
        "instagram_url": f"https://instagram.com/{raw.get('username', '')}",
        "username": raw.get("username", ""),
        "full_name": raw.get("fullName"),
        "bio": raw.get("biography"),
        "followers": followers,
        "following": following,
        "posts_count": raw.get("postsCount", 0),
        "engagement_rate": engagement_rate,
        "is_verified": raw.get("verified", False),
        "is_business": raw.get("isBusinessAccount", False),
        "external_url": raw.get("externalUrl"),
        "business_email": raw.get("businessEmail"),
        "following_ratio": following_ratio,
    }

def _calculate_engagement_rate(self, raw: dict) -> float | None:
    followers = raw.get("followersCount", 0) or 0
    if followers < 100:
        return None
    
    posts = raw.get("latestPosts", [])[:12]
    if not posts:
        return None
    
    total = sum((p.get("likesCount", 0) or 0) + (p.get("commentsCount", 0) or 0) for p in posts)
    return round((total / len(posts) / followers) * 100, 2)
```

### Fake Detection

```python
def extract_fake_signals(self, profile: dict) -> dict:
    followers = profile.get("followers", 0)
    following_ratio = profile.get("following_ratio")
    engagement_rate = profile.get("engagement_rate")
    posts_count = profile.get("posts_count", 0)
    
    signals = {
        "high_following_ratio": following_ratio and following_ratio > 2.0,
        "low_post_count": followers > 5000 and posts_count < 20,
        "low_engagement": engagement_rate and engagement_rate < 1.0,
        "no_business_account": not profile.get("is_business"),
        "no_external_url": not profile.get("external_url"),
    }
    
    penalty = 0
    if signals["high_following_ratio"]: penalty += 30
    if signals["low_post_count"]: penalty += 25
    if signals["low_engagement"]: penalty += 20
    if signals["no_business_account"]: penalty += 10
    
    return {"signals": signals, "penalty": min(penalty, 100), "is_likely_fake": penalty >= 50}
```

---

## Field Mapping Reference

| Apify Field | Database Field |
|-------------|----------------|
| `username` | `username` |
| `fullName` | `full_name` |
| `biography` | `bio` |
| `followersCount` | `followers` |
| `followsCount` | `following` |
| `postsCount` | `posts_count` |
| `verified` | `is_verified` |
| `isBusinessAccount` | `is_business` |
| `externalUrl` | `external_url` |
| `businessEmail` | `business_email` |
| `latestPosts` | (for engagement calc) |

## Environment Variables

```bash
APIFY_API_KEY=apify_api_xxxxx
```

## Cross-References
- `docs/Apify_Fake_Detection_Guide.md`
