#!/usr/bin/env python3
"""
Validation script for EPIC-2: Database Layer.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"VALIDATION: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=False, cwd=str(BACKEND_DIR))
    success = result.returncode == 0

    print(f"Result: {'PASS' if success else 'FAIL'}")
    return success


def validate_structure() -> bool:
    """Validate database layer structure exists."""
    required_files = [
        "app/db/__init__.py",
        "app/db/supabase_client.py",
        "app/db/sqlite_client.py",
        "app/db/factory.py",
        "app/models/__init__.py",
        "app/models/base.py",
        "app/models/user.py",
        "app/models/discovery.py",
        "app/models/profile.py",
        "app/repositories/__init__.py",
        "app/repositories/base.py",
        "app/repositories/discovery_repository.py",
        "app/repositories/profile_repository.py",
        "tests/unit/test_supabase_client.py",
        "tests/unit/test_sqlite_client.py",
        "tests/unit/test_models_base.py",
        "tests/unit/test_models_discovery.py",
        "tests/unit/test_models_profile.py",
        "tests/unit/test_repositories_base.py",
        "tests/integration/test_database.py",
    ]

    backend_dir = BACKEND_DIR

    print("\n" + "=" * 60)
    print("VALIDATION: Database Layer Structure")
    print("=" * 60)

    all_exist = True
    for file in required_files:
        path = backend_dir / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False

    print(f"\nResult: {'PASS' if all_exist else 'FAIL'}")
    return all_exist


def validate_sqlite_operations() -> bool:
    """Validate SQLite client operations work."""
    print("\n" + "=" * 60)
    print("VALIDATION: SQLite Operations")
    print("=" * 60)

    try:
        # Create a test database
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Import and test
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from app.db.sqlite_client import SQLiteClient

        client = SQLiteClient(path)

        # Test insert
        result = client.insert("discovery_jobs", {
            "user_id": "test-user",
            "status": "pending",
            "reference_profiles": "[]",
            "settings": "{}"
        })
        assert "id" in result, "Insert should return ID"

        # Test select
        records = client.select("discovery_jobs")
        assert len(records) == 1, "Should have 1 record"

        # Test update
        updated = client.update("discovery_jobs", result["id"], {"status": "completed"})
        assert updated["status"] == "completed", "Status should be updated"

        # Test delete
        deleted = client.delete("discovery_jobs", result["id"])
        assert deleted, "Delete should return True"

        # Cleanup
        os.unlink(path)

        print("  ✓ Insert operation")
        print("  ✓ Select operation")
        print("  ✓ Update operation")
        print("  ✓ Delete operation")
        print("\nResult: PASS")
        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        print("\nResult: FAIL")
        return False


def validate_supabase_migrations() -> bool:
    """Validate Supabase migration files exist and are valid."""
    print("Validating Supabase migrations...")

    migration_dir = REPO_ROOT / "setup" / "supabase" / "migrations"

    required_files = [
        "001_initial_schema.sql",
        "002_indexes.sql",
        "003_rls_policies.sql",
        "004_triggers.sql",
        "005_realtime.sql",
        "006_views.sql",
        "007_seed.sql",
        "README.md",
    ]

    all_exist = True
    for filename in required_files:
        filepath = migration_dir / filename
        exists = filepath.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")
        if not exists:
            all_exist = False

    for filename in required_files:
        if filename.endswith(".sql"):
            filepath = migration_dir / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                if "CREATE" not in content and "ALTER" not in content and "INSERT" not in content:
                    print(f"  ⚠ {filename} may be empty or invalid")

    print(f"\nResult: {'PASS' if all_exist else 'FAIL'}")
    return all_exist


# === MOCK DATA VALIDATION ===

def validate_mock_data_loading():
    """Validate that mock data loads correctly."""
    print("Testing mock data loading...")

    try:
        from tests.fixtures.mock_data import (
            load_mock_data,
            get_genuine_profiles,
            get_fake_profiles,
            PRD_JOB_STATUSES,
            PRD_PROFILE_STATUSES,
            PRD_SCORING_WEIGHTS,
        )

        data = load_mock_data()

        # Verify all entity types loaded
        assert len(data["users"]) >= 2, "Should have at least 2 users"
        assert len(data["discovery_jobs"]) >= 6, "Should have jobs covering all statuses"
        assert len(data["profiles"]) >= 5, "Should have diverse profiles"
        assert len(data["scores"]) >= 4, "Should have scores with various ranges"

        # Verify PRD status coverage
        job_statuses = {j["status"] for j in data["discovery_jobs"]}
        assert job_statuses == set(PRD_JOB_STATUSES), (
            f"Missing statuses: {set(PRD_JOB_STATUSES) - job_statuses}"
        )

        # Verify fake detection test data
        genuine = get_genuine_profiles()
        fake = get_fake_profiles()
        assert len(genuine) >= 3, "Should have genuine profiles for positive testing"
        assert len(fake) >= 1, "Should have fake profiles for fake detection testing"

        assert PRD_PROFILE_STATUSES and PRD_SCORING_WEIGHTS

        print("  ✓ Mock data loading validated")
        return True

    except Exception as e:
        print(f"  ✗ Mock data loading failed: {e}")
        return False


def validate_prd_schema_compliance():
    """Validate mock data matches PRD schema exactly."""
    print("Validating PRD schema compliance...")

    try:
        from tests.fixtures.mock_data import load_mock_data

        data = load_mock_data()

        # PRD 10.3: discovery_jobs required fields
        job_required_fields = [
            "id",
            "user_id",
            "name",
            "brand_description",
            "reference_profiles",
            "status",
            "profiles_discovered",
            "profiles_scored",
            "created_at",
            "updated_at",
        ]
        for job in data["discovery_jobs"]:
            for field in job_required_fields:
                assert field in job, f"Job missing PRD field: {field}"

        # PRD 10.5: discovered_profiles required fields
        profile_required_fields = [
            "id",
            "job_id",
            "instagram_url",
            "username",
            "followers",
            "following",
            "posts_count",
            "engagement_rate",
            "is_verified",
            "is_business",
            "following_ratio",
            "status",
        ]
        for profile in data["profiles"]:
            for field in profile_required_fields:
                assert field in profile, f"Profile missing PRD field: {field}"

        # PRD 10.6: profile_scores with 6 dimensions
        score_dimensions = [
            "visual_aesthetic_match",
            "content_theme_alignment",
            "engagement_rate_score",
            "follower_quality",
            "business_indicators",
            "activity_recency",
        ]
        for score in data["scores"]:
            for dimension in score_dimensions:
                assert dimension in score, f"Score missing PRD dimension: {dimension}"
                assert 0 <= score[dimension] <= 100, f"{dimension} must be 0-100"

        print("  ✓ PRD schema compliance validated")
        return True

    except Exception as e:
        print(f"  ✗ PRD schema compliance failed: {e}")
        return False


def validate_fake_detection_data():
    """Validate fake detection test data per PRD 5.3.1."""
    print("Validating fake detection data (PRD 5.3.1)...")

    try:
        from tests.fixtures.mock_data import load_mock_data

        data = load_mock_data()

        # Find profiles with fake indicators
        fake_indicators_found = {
            "high_following_ratio": False,
            "low_posts_high_followers": False,
            "low_engagement": False,
            "no_business_account": False,
        }

        for profile in data["profiles"]:
            if profile.get("following_ratio", 0) > 0.5:
                fake_indicators_found["high_following_ratio"] = True
            if profile.get("followers", 0) > 50000 and profile.get("posts_count", 100) < 20:
                fake_indicators_found["low_posts_high_followers"] = True
            if profile.get("engagement_rate", 5) < 1.0:
                fake_indicators_found["low_engagement"] = True
            if not profile.get("is_business", True):
                fake_indicators_found["no_business_account"] = True

        missing = [k for k, v in fake_indicators_found.items() if not v]
        assert not missing, f"Missing fake detection test cases: {missing}"

        # Verify scores for fake profiles are low
        for score in data["scores"]:
            if score.get("_test_purpose", "").startswith("very_low"):
                assert score["score"] < 30, "Fake profile should score below 30"
            if score.get("_test_purpose", "").startswith("low_score"):
                assert score["score"] < 50, "Suspicious profile should score below 50"

        print("  ✓ Fake detection data validated (PRD 5.3.1)")
        return True

    except Exception as e:
        print(f"  ✗ Fake detection data validation failed: {e}")
        return False


def validate_user_isolation_data():
    """Validate multi-user isolation test data per PRD 6."""
    print("Validating user isolation data (PRD Section 6)...")

    try:
        from tests.fixtures.mock_data import load_mock_data, get_jobs_for_user

        data = load_mock_data()

        # Verify multiple users exist
        assert len(data["users"]) >= 2, "Need at least 2 users for isolation tests"

        user1_id = data["users"][0]["id"]
        user2_id = data["users"][1]["id"]

        # Each user should have their own jobs
        user1_jobs = get_jobs_for_user(user1_id)
        user2_jobs = get_jobs_for_user(user2_id)

        assert len(user1_jobs) >= 1, "User 1 should have jobs"
        assert len(user2_jobs) >= 1, "User 2 should have jobs for isolation testing"

        # Verify no job belongs to multiple users
        job_user_map = {}
        for job in data["discovery_jobs"]:
            assert job["id"] not in job_user_map, "Duplicate job ID found"
            job_user_map[job["id"]] = job["user_id"]

        print("  ✓ User isolation data validated")
        return True

    except Exception as e:
        print(f"  ✗ User isolation data validation failed: {e}")
        return False


def validate_scoring_weights():
    """Validate score calculations match PRD weights."""
    print("Validating scoring weight calculations (PRD 5.3)...")

    try:
        from tests.fixtures.mock_data import load_mock_data, PRD_SCORING_WEIGHTS

        data = load_mock_data()

        for score_data in data["scores"]:
            calculated = sum(
                score_data.get(dim, 0) * weight
                for dim, weight in PRD_SCORING_WEIGHTS.items()
            )

            actual = score_data["score"]

            assert abs(calculated - actual) <= 2, (
                f"Score mismatch for {score_data['id']}: "
                f"calculated={calculated:.1f}, actual={actual}"
            )

        print("  ✓ Scoring weight calculations validated (PRD 5.3)")
        return True

    except Exception as e:
        print(f"  ✗ Scoring weight validation failed: {e}")
        return False


def run_mock_data_validations():
    """Run all mock data validations."""
    print("\n" + "=" * 50)
    print("MOCK DATA & PRD COMPLIANCE VALIDATION")
    print("=" * 50 + "\n")

    results = [
        ("Mock Data Loading", validate_mock_data_loading()),
        ("PRD Schema Compliance", validate_prd_schema_compliance()),
        ("Fake Detection Data (PRD 5.3.1)", validate_fake_detection_data()),
        ("User Isolation Data (PRD 6)", validate_user_isolation_data()),
        ("Scoring Weights (PRD 5.3)", validate_scoring_weights()),
    ]

    print("\n" + "-" * 50)
    print("MOCK DATA VALIDATION SUMMARY")
    print("-" * 50)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    return all_passed


def main() -> int:
    """Run all validations."""
    print("\n" + "#" * 60)
    print("# EPIC-2 VALIDATION: Database Layer")
    print("#" * 60)

    results = []

    # 1. Structure validation
    results.append(validate_structure())

    # 1.1 Supabase migrations validation
    results.append(validate_supabase_migrations())

    # 2. Run model tests
    model_tests = sorted(Path("tests/unit").glob("test_models_*.py"))
    results.append(run_command(
        [sys.executable, "-m", "pytest", *[str(p) for p in model_tests], "-v", "--tb=short"],
        "Model Unit Tests"
    ))

    # 3. Run repository tests
    repo_tests = sorted(Path("tests/unit").glob("test_repositories_*.py"))
    results.append(run_command(
        [sys.executable, "-m", "pytest", *[str(p) for p in repo_tests], "-v", "--tb=short"],
        "Repository Unit Tests"
    ))

    # 4. Run database client tests
    client_tests = sorted(Path("tests/unit").glob("test_*_client.py"))
    results.append(run_command(
        [sys.executable, "-m", "pytest", *[str(p) for p in client_tests], "-v", "--tb=short"],
        "Database Client Tests"
    ))

    # 5. SQLite operations test
    results.append(validate_sqlite_operations())

    # 6. Type checking
    results.append(run_command(
        [
            sys.executable,
            "-m",
            "mypy",
            "app/db/",
            "app/models/",
            "app/repositories/",
            "--ignore-missing-imports",
            "--follow-imports=skip",
        ],
        "Type Checking (mypy)"
    ))

    # 7. Mock data validation
    results.append(run_mock_data_validations())

    # 8. Integration test
    results.append(run_command(
        [sys.executable, "-m", "pytest", "tests/integration/test_database.py", "-v", "--tb=short"],
        "Integration Test"
    ))

    # Summary
    print("\n" + "#" * 60)
    print("# VALIDATION SUMMARY")
    print("#" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if all(results):
        print("\n✓ EPIC-2 VALIDATION PASSED")
        return 0
    else:
        print("\n✗ EPIC-2 VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
