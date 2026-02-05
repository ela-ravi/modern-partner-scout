"""
Mock data loader utilities for PRD-aligned fixtures.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent


def load_json_file(filename: str) -> dict[str, Any]:
    """Load a JSON file from the mock_data directory."""
    path = BASE_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_data() -> dict[str, Any]:
    """Load all mock data files into a single dictionary."""
    return {
        "users": load_json_file("users.json")["users"],
        "discovery_jobs": load_json_file("discovery_jobs.json")["discovery_jobs"],
        "brand_dna": load_json_file("brand_dna.json")["brand_dna"],
        "profiles": load_json_file("profiles.json")["profiles"],
        "scores": load_json_file("scores.json")["scores"],
        "contacts": load_json_file("contacts.json")["contacts"],
    }


def get_user(user_id: str) -> dict[str, Any] | None:
    """Get a specific user by ID."""
    users = load_json_file("users.json")["users"]
    return next((u for u in users if u["id"] == user_id), None)


def get_job(job_id: str) -> dict[str, Any] | None:
    """Get a specific discovery job by ID."""
    jobs = load_json_file("discovery_jobs.json")["discovery_jobs"]
    return next((j for j in jobs if j["id"] == job_id), None)


def get_jobs_for_user(user_id: str) -> list[dict[str, Any]]:
    """Get all jobs for a specific user."""
    jobs = load_json_file("discovery_jobs.json")["discovery_jobs"]
    return [j for j in jobs if j["user_id"] == user_id]


def get_profiles_for_job(job_id: str) -> list[dict[str, Any]]:
    """Get all profiles for a specific job."""
    profiles = load_json_file("profiles.json")["profiles"]
    return [p for p in profiles if p["job_id"] == job_id]


def get_score_for_profile(profile_id: str) -> dict[str, Any] | None:
    """Get the score for a specific profile."""
    scores = load_json_file("scores.json")["scores"]
    return next((s for s in scores if s["profile_id"] == profile_id), None)


def get_brand_dna_for_job(job_id: str) -> dict[str, Any] | None:
    """Get brand DNA for a specific job."""
    dna_list = load_json_file("brand_dna.json")["brand_dna"]
    return next((d for d in dna_list if d["job_id"] == job_id), None)


def get_profiles_by_status(status: str) -> list[dict[str, Any]]:
    """Get all profiles with a specific status."""
    profiles = load_json_file("profiles.json")["profiles"]
    return [p for p in profiles if p["status"] == status]


def get_genuine_profiles() -> list[dict[str, Any]]:
    """Get profiles expected to score above 50 (genuine profiles)."""
    profiles = load_json_file("profiles.json")["profiles"]
    return [p for p in profiles if p.get("_expected_score_range", [0, 0])[0] >= 50]


def get_fake_profiles() -> list[dict[str, Any]]:
    """Get profiles expected to score below 50 (fake/suspicious profiles)."""
    profiles = load_json_file("profiles.json")["profiles"]
    return [p for p in profiles if p.get("_expected_score_range", [100, 100])[1] < 50]


# PRD Reference constants for validation
PRD_JOB_STATUSES = ["pending", "analyzing", "discovering", "scoring", "completed", "failed"]
PRD_PROFILE_STATUSES = ["new", "processing", "done", "skipped"]
PRD_SCORING_WEIGHTS = {
    "visual_aesthetic_match": 0.25,
    "content_theme_alignment": 0.20,
    "engagement_rate_score": 0.15,
    "follower_quality": 0.15,
    "business_indicators": 0.15,
    "activity_recency": 0.10,
}
