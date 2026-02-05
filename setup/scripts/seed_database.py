#!/usr/bin/env python3
"""
Database seed script for PartnerScout AI.

Seeds the database with PRD-aligned mock data for testing and demos.

Usage:
    # Seed with default mock data
    python scripts/seed_database.py

    # Seed specific tables only
    python scripts/seed_database.py --tables users,discovery_jobs

    # Clear and reseed
    python scripts/seed_database.py --reset

    # Verify seeded data against PRD
    python scripts/seed_database.py --verify
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.logging import get_logger
from app.db.factory import get_db_client
from app.db.supabase_client import SupabaseClient
from tests.fixtures.mock_data import (
    PRD_JOB_STATUSES,
    PRD_PROFILE_STATUSES,
    PRD_SCORING_WEIGHTS,
    load_mock_data,
)

logger = get_logger(__name__)


def _strip_meta(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if not k.startswith("_")}


def _is_supabase(db_client: Any) -> bool:
    return isinstance(db_client, SupabaseClient)


def _serialize_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def _transform_job_for_sqlite(job: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(job)
    settings = {
        "name": data.pop("name", None),
        "brand_description": data.pop("brand_description", None),
        "profiles_discovered": data.pop("profiles_discovered", 0),
        "profiles_scored": data.pop("profiles_scored", 0),
    }
    data["reference_profiles"] = _serialize_json(data.get("reference_profiles", []))
    data["settings"] = _serialize_json(settings)
    return data


def _transform_brand_dna_for_sqlite(dna: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(dna)
    data["hashtags"] = _serialize_json(data.get("hashtags", []))
    data["keywords"] = _serialize_json(data.get("keywords", []))
    data["competitors"] = _serialize_json(data.get("competitors", []))
    embedding_vector = data.pop("embedding_vector", [])
    data["embedding"] = _serialize_json(embedding_vector)
    data["analysis"] = _serialize_json(data.get("analysis", {}))
    return data


def _transform_profile_for_sqlite(profile: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(profile)
    return {
        "id": data.get("id"),
        "job_id": data.get("job_id"),
        "username": data.get("username"),
        "profile_url": data.get("instagram_url"),
        "display_name": data.get("full_name"),
        "bio": data.get("bio"),
        "follower_count": data.get("followers", 0),
        "following_count": data.get("following", 0),
        "post_count": data.get("posts_count", 0),
        "profile_pic_url": data.get("profile_picture_url"),
        "is_verified": data.get("is_verified", False),
        "is_business": data.get("is_business", False),
        "status": data.get("status", "new"),
        "discovered_at": data.get("discovered_at"),
    }


def _transform_score_for_sqlite(score: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(score)
    category_scores = {
        "visual_aesthetic_match": data.get("visual_aesthetic_match", 0),
        "content_theme_alignment": data.get("content_theme_alignment", 0),
        "engagement_rate_score": data.get("engagement_rate_score", 0),
        "follower_quality": data.get("follower_quality", 0),
        "business_indicators": data.get("business_indicators", 0),
        "activity_recency": data.get("activity_recency", 0),
    }
    metadata = {"test_purpose": score.get("_test_purpose")}
    return {
        "id": data.get("id"),
        "profile_id": data.get("profile_id"),
        "overall_score": data.get("score"),
        "category_scores": _serialize_json(category_scores),
        "reasoning": _serialize_json(data.get("reasoning", {})),
        "metadata": _serialize_json(metadata),
        "scored_at": data.get("created_at"),
    }


def _transform_contact_for_sqlite(contact: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(contact)
    return {
        "id": data.get("id"),
        "profile_id": data.get("profile_id"),
        "email": data.get("email"),
        "source": data.get("source"),
        "confidence": data.get("confidence", 0.0),
        "extracted_at": data.get("extracted_at"),
    }


def _transform_user_for_sqlite(user: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(user)
    user_metadata = {
        "full_name": data.get("full_name"),
        "avatar_url": data.get("avatar_url"),
    }
    return {
        "id": data.get("id"),
        "email": data.get("email"),
        "user_metadata": _serialize_json(user_metadata),
        "created_at": data.get("created_at"),
    }


def _transform_brand_dna_for_supabase(dna: dict[str, Any]) -> dict[str, Any]:
    data = _strip_meta(dna)
    embedding_vector = data.pop("embedding_vector", [])
    data.setdefault("competitors", [])
    data.setdefault("analysis", {})
    data["embedding"] = embedding_vector
    return data


async def seed_users(db_client: Any, users: list[dict[str, Any]]) -> dict[str, str]:
    """Seed users table / auth users. Returns mapping from fixture id to real id."""
    logger.info("Seeding users", count=len(users))
    id_map: dict[str, str] = {}

    if _is_supabase(db_client):
        for user in users:
            data = _strip_meta(user)
            email = data["email"]
            password = "TempPass123!"
            try:
                response = db_client.auth.admin.create_user(
                    {"email": email, "password": password, "email_confirm": True}
                )
                supa_user = response.user or response
                id_map[data["id"]] = supa_user.id
            except Exception:
                # Attempt to find existing user by listing
                try:
                    existing = db_client.auth.admin.list_users()
                    match = next((u for u in existing if u.email == email), None)
                    if match:
                        id_map[data["id"]] = match.id
                    else:
                        raise
                except Exception as exc:
                    logger.error("Failed to create/find user", email=email, error=str(exc))
                    raise
        return id_map

    for user in users:
        data = _transform_user_for_sqlite(user)
        db_client.insert("users", data)
        id_map[user["id"]] = user["id"]

    return id_map


async def seed_discovery_jobs(
    db_client: Any,
    jobs: list[dict[str, Any]],
    user_id_map: dict[str, str],
) -> None:
    logger.info("Seeding discovery_jobs", count=len(jobs))
    for job in jobs:
        data = _strip_meta(job)
        data["user_id"] = user_id_map.get(data["user_id"], data["user_id"])
        if _is_supabase(db_client):
            db_client.insert("discovery_jobs", data)
        else:
            db_client.insert("discovery_jobs", _transform_job_for_sqlite(data))
    logger.info("✓ Discovery jobs seeded")


async def seed_brand_dna(db_client: Any, dna_list: list[dict[str, Any]]) -> None:
    logger.info("Seeding brand_dna", count=len(dna_list))
    for dna in dna_list:
        if _is_supabase(db_client):
            db_client.insert("brand_dna", _transform_brand_dna_for_supabase(dna))
        else:
            db_client.insert("brand_dna", _transform_brand_dna_for_sqlite(dna))
    logger.info("✓ Brand DNA seeded")


async def seed_profiles(db_client: Any, profiles: list[dict[str, Any]]) -> None:
    logger.info("Seeding discovered_profiles", count=len(profiles))
    for profile in profiles:
        if _is_supabase(db_client):
            db_client.insert("discovered_profiles", _strip_meta(profile))
        else:
            db_client.insert("discovered_profiles", _transform_profile_for_sqlite(profile))
    logger.info("✓ Profiles seeded")


async def seed_scores(db_client: Any, scores: list[dict[str, Any]]) -> None:
    logger.info("Seeding profile_scores", count=len(scores))
    for score in scores:
        if _is_supabase(db_client):
            db_client.insert("profile_scores", _strip_meta(score))
        else:
            db_client.insert("profile_scores", _transform_score_for_sqlite(score))
    logger.info("✓ Profile scores seeded")


async def seed_contacts(db_client: Any, contacts: list[dict[str, Any]]) -> None:
    logger.info("Seeding profile_contacts", count=len(contacts))
    for contact in contacts:
        if _is_supabase(db_client):
            db_client.insert("profile_contacts", _strip_meta(contact))
        else:
            db_client.insert("profile_contacts", _transform_contact_for_sqlite(contact))
    logger.info("✓ Profile contacts seeded")


def _reset_tables_sqlite(db_client: Any, tables: list[str]) -> None:
    for table in tables:
        db_client.execute(f"DELETE FROM {table}")


def _reset_tables_supabase(db_client: SupabaseClient, tables: list[str]) -> None:
    for table in tables:
        db_client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()


async def reset_database(db_client: Any) -> None:
    logger.info("Resetting database (truncate)")
    tables = [
        "profile_contacts",
        "profile_scores",
        "discovered_profiles",
        "brand_dna",
        "discovery_jobs",
    ]

    if _is_supabase(db_client):
        _reset_tables_supabase(db_client, tables)
    else:
        _reset_tables_sqlite(db_client, tables)


async def verify_seeded_data(db_client: Any) -> bool:
    logger.info("Verifying seeded data against PRD...")
    errors: list[str] = []

    jobs = db_client.select("discovery_jobs")
    profiles = db_client.select("discovered_profiles")

    job_statuses = {j["status"] for j in jobs}
    missing_statuses = set(PRD_JOB_STATUSES) - job_statuses
    if missing_statuses:
        errors.append(f"Missing job statuses in seed data: {missing_statuses}")

    profile_statuses = {p["status"] for p in profiles}
    missing_profile_statuses = set(PRD_PROFILE_STATUSES) - profile_statuses
    if missing_profile_statuses:
        errors.append(f"Missing profile statuses in seed data: {missing_profile_statuses}")

    if errors:
        for error in errors:
            logger.error(error)
        return False

    logger.info("✓ Seeded data verified")
    return True


async def main(args: argparse.Namespace) -> int:
    db_client = get_db_client()
    data = load_mock_data()

    if args.reset:
        await reset_database(db_client)

    if args.verify:
        success = await verify_seeded_data(db_client)
        return 0 if success else 1

    tables_to_seed = args.tables.split(",") if args.tables else [
        "users",
        "discovery_jobs",
        "brand_dna",
        "profiles",
        "scores",
        "contacts",
    ]

    user_id_map: dict[str, str] = {}
    if "users" in tables_to_seed:
        user_id_map = await seed_users(db_client, data["users"])

    if "discovery_jobs" in tables_to_seed:
        await seed_discovery_jobs(db_client, data["discovery_jobs"], user_id_map)

    if "brand_dna" in tables_to_seed:
        await seed_brand_dna(db_client, data["brand_dna"])

    if "profiles" in tables_to_seed:
        await seed_profiles(db_client, data["profiles"])

    if "scores" in tables_to_seed:
        await seed_scores(db_client, data["scores"])

    if "contacts" in tables_to_seed:
        await seed_contacts(db_client, data["contacts"])

    await verify_seeded_data(db_client)
    logger.info("Database seeding completed successfully!")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with mock data")
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of tables to seed (default: all)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all data before seeding",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify existing data against PRD (no seeding)",
    )

    args = parser.parse_args()
    exit_code = asyncio.run(main(args))
    sys.exit(exit_code)
