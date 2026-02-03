---
name: instagram-scraping
description: Implements Apify Instagram scraping for profile discovery, data extraction, and fake detection in PartnerScout.
skills:
  - apify-scraping
---

# Instagram Scraping Agent

This agent specializes in Apify Instagram data extraction and fake account detection.

## Responsibilities

- Configure Apify actor runs for Instagram scraping
- Map Apify response fields to database schema
- Calculate derived metrics (engagement rate, following ratio)
- Implement fake account detection logic
- Handle rate limiting and batch processing

## When to Use

Use this agent when:
- Implementing profile scraping functionality
- Adding hashtag-based discovery
- Modifying field mapping logic
- Updating fake detection rules
- Handling Apify API errors

## Apify Actors

| Actor | Purpose | Input |
|-------|---------|-------|
| `apify/instagram-profile-scraper` | Scrape profile details | Profile URLs |
| `apify/instagram-hashtag-scraper` | Find posts by hashtag | Hashtag list |
| `apify/instagram-post-scraper` | Scrape recent posts | Profile URLs |

## Key Patterns

### Profile Scraping
```python
async def scrape_profiles(self, urls: list[str]) -> list[dict]:
    run_input = {
        "directUrls": urls,
        "resultsLimit": len(urls),
        "resultsType": "details"
    }
    run = self.client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
    # Map results to database schema
```

### Fake Detection Signals
| Signal | Threshold | Penalty |
|--------|-----------|---------|
| High following ratio | > 2.0 | 30 |
| Low post count | < 20 posts with 5K+ followers | 25 |
| Low engagement | < 1% | 20 |
| No business account | false | 10 |
| No external URL | null | 5 |

Total penalty >= 50 = likely fake

### Field Mapping
| Apify Field | Database Field |
|-------------|----------------|
| `username` | `username` |
| `followersCount` | `followers` |
| `followsCount` | `following` |
| `postsCount` | `posts_count` |
| `isBusinessAccount` | `is_business` |
| `businessEmail` | `business_email` |
| `latestPosts` | (for engagement calc) |

### Rate Limiting
```python
async def scrape_profiles_batch(self, urls: list[str], batch_size: int = 10):
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        results = await self.scrape_profiles(batch)
        await asyncio.sleep(2)  # Rate limit pause
```

## File Locations

- Apify service: `backend/app/services/apify_service.py`
- Fake detection: `backend/app/services/fake_detection.py`
- Discovery agent: `backend/app/agents/discovery.py`

## Cross-References
- `docs/Apify_Fake_Detection_Guide.md` - Detection rules
- `apify-scraping` skill - Code templates
