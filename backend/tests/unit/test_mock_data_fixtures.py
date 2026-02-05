"""
Unit tests for mock data fixtures and loader utilities.
"""


def test_load_mock_data_has_required_sections():
    from tests.fixtures.mock_data import load_mock_data

    data = load_mock_data()
    assert "users" in data
    assert "discovery_jobs" in data
    assert "brand_dna" in data
    assert "profiles" in data
    assert "scores" in data
    assert "contacts" in data


def test_mock_data_status_coverage():
    from tests.fixtures.mock_data import PRD_JOB_STATUSES, PRD_PROFILE_STATUSES, load_mock_data

    data = load_mock_data()
    job_statuses = {j["status"] for j in data["discovery_jobs"]}
    profile_statuses = {p["status"] for p in data["profiles"]}

    assert set(PRD_JOB_STATUSES) == job_statuses
    assert set(PRD_PROFILE_STATUSES).issubset(profile_statuses)
