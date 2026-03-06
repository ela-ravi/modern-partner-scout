"""
Health Check Routes

Provides health check endpoints for monitoring and load balancer probes.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    timestamp: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        HealthResponse: Current health status of the API.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint.

    Checks connectivity to all dependent services.

    Returns:
        DetailedHealthResponse: Detailed health status including service connectivity.
    """
    import os

    services: dict = {}

    # --- Apify ---
    apify_key = os.environ.get("APIFY_API_KEY", "")
    if not apify_key or apify_key == "your-apify-api-key":
        services["apify"] = "not_configured"
    else:
        services["apify_key_prefix"] = apify_key[:12] + "..."
        try:
            from app.services.apify_service import get_apify_service
            svc = get_apify_service()
            services["apify_configured"] = svc.is_configured()
            # Quick connectivity check via REST
            import urllib.request, json as _json
            test_url = f"https://api.apify.com/v2/users/me?token={apify_key}"
            resp = urllib.request.urlopen(
                urllib.request.Request(test_url), timeout=10
            )
            user_data = _json.loads(resp.read())
            plan = user_data.get("data", {}).get("plan", {}).get("id", "?")
            username = user_data.get("data", {}).get("username", "?")
            services["apify"] = f"healthy (plan={plan}, user={username})"

            # Check recent actor runs
            runs_url = f"https://api.apify.com/v2/actor-runs?token={apify_key}&limit=5&desc=true"
            runs_resp = urllib.request.urlopen(
                urllib.request.Request(runs_url), timeout=10
            )
            runs_data = _json.loads(runs_resp.read())
            runs = runs_data.get("data", {}).get("items", [])
            services["apify_recent_runs"] = len(runs)
            if runs:
                latest = runs[0]
                services["apify_last_run"] = (
                    f"{latest.get('status')} at {latest.get('startedAt', '?')}"
                )
        except Exception as e:
            services["apify"] = f"error: {str(e)[:120]}"

    # --- LLM ---
    llm_provider = os.environ.get("LLM_PROVIDER", "?")
    services["llm_provider"] = llm_provider
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    services["gemini_key_set"] = bool(gemini_key and len(gemini_key) > 5)

    # --- Database ---
    try:
        from app.core.config import settings as _settings
        services["supabase_url"] = _settings.supabase.url[:40] + "..."
        services["database"] = "configured"
    except Exception as e:
        services["database"] = f"error: {str(e)[:80]}"

    overall_status = "healthy" if "error" not in str(services.get("apify", "")) else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services
    )


@router.get("/health/apify-test")
async def apify_pipeline_test():
    """
    Test each Apify-powered discovery method used by the pipeline.

    Tests: profile scraper, hashtag scraper, search scraper, tagged scraper.
    Returns step-by-step results showing exactly what works and what doesn't.
    """
    import traceback
    from app.services.apify_service import get_apify_service

    result: dict = {"tests": {}}
    svc = get_apify_service()

    # Test 1: Profile scraper (used by brand analysis + discovery)
    try:
        profiles = await svc.scrape_profiles(["argosfragrances"], results_limit=1)
        p = profiles[0] if profiles else {}
        related = p.get("relatedProfiles", [])
        result["tests"]["profile_scraper"] = {
            "status": "OK",
            "profiles_returned": len(profiles),
            "username": p.get("username"),
            "followers": p.get("followersCount"),
            "related_profiles_count": len(related),
            "related_sample": [r.get("username", r) if isinstance(r, dict) else r for r in related[:3]],
        }
    except Exception as e:
        result["tests"]["profile_scraper"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc()[-300:],
        }

    # Test 2: Hashtag scraper (used by discovery rounds 4+)
    try:
        hashtag_results = await svc.search_hashtags(["perfume"], limit_per_hashtag=5)
        posts = hashtag_results.get("perfume", [])
        usernames = set()
        for post in posts:
            owner = post.get("ownerUsername") or (post.get("owner", {}) or {}).get("username")
            if owner:
                usernames.add(owner)
        result["tests"]["hashtag_scraper"] = {
            "status": "OK",
            "posts_returned": len(posts),
            "unique_usernames": len(usernames),
            "sample_usernames": list(usernames)[:5],
            "sample_post_keys": list(posts[0].keys()) if posts else [],
        }
    except Exception as e:
        result["tests"]["hashtag_scraper"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc()[-300:],
        }

    # Test 3: Search scraper (used by keyword user search in round 2)
    try:
        search_results = await svc.search_users(
            keywords=["perfume distributor"],
            limit_per_keyword=5,
        )
        result["tests"]["search_scraper"] = {
            "status": "OK",
            "users_returned": len(search_results),
            "sample_users": [
                r.get("username") or r.get("userName") or "?"
                for r in search_results[:5]
            ],
            "sample_keys": list(search_results[0].keys()) if search_results else [],
        }
    except Exception as e:
        result["tests"]["search_scraper"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc()[-300:],
        }

    # Test 4: Tagged scraper (used by round 1)
    try:
        taggers = await svc.search_tagged_posts(
            usernames=["argosfragrances"],
            results_limit=10,
        )
        result["tests"]["tagged_scraper"] = {
            "status": "OK",
            "taggers_found": len(taggers),
            "sample_taggers": taggers[:5],
        }
    except Exception as e:
        result["tests"]["tagged_scraper"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc()[-300:],
        }

    # Summary
    statuses = {k: v.get("status") for k, v in result["tests"].items()}
    result["summary"] = statuses
    result["all_ok"] = all(s == "OK" for s in statuses.values())

    return result
