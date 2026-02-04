"""
Tests for STORY-4.1.2: Build Discovery Workflow.

Validates the n8n workflow JSON, ensuring it matches the documented
Partner Discovery orchestration design and references existing backend APIs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pytest
from fastapi.routing import APIRoute

from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = PROJECT_ROOT / "n8n" / "workflows" / "partner-discovery.json"


@pytest.fixture(scope="module")
def workflow() -> dict:
    """Load the workflow JSON once per test module."""
    assert WORKFLOW_PATH.exists(), f"Workflow JSON missing at {WORKFLOW_PATH}"
    with WORKFLOW_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _get_node(workflow: dict, name: str) -> dict:
    """Helper to fetch a node by name with a friendly assertion."""
    for node in workflow["nodes"]:
        if node["name"] == name:
            return node
    raise AssertionError(f"Node '{name}' not found in workflow.")


def _get_registered_routes() -> dict[str, set[str]]:
    """Return FastAPI registered paths mapped to their HTTP methods."""
    routes: dict[str, set[str]] = {}
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.setdefault(route.path, set()).update(route.methods or set())
    return routes


def test_workflow_contains_expected_nodes(workflow: dict) -> None:
    """Workflow has exactly 21 nodes with the documented names."""
    node_names = {node["name"] for node in workflow["nodes"]}
    assert len(workflow["nodes"]) == 21, "Workflow must include 21 nodes."
    expected_names = {
        "Webhook Trigger",
        "Manual Trigger",
        "Validate Input",
        "Return 400 Error",
        "Set Job Analyzing",
        "Brand Analyzer Agent",
        "Set Job Discovering",
        "Discovery Agent",
        "Set Job Scoring",
        "Split Profiles",
        "Set Profile Processing",
        "Scorer Agent",
        "Set Profile Done",
        "Wait",
        "Merge Results",
        "Filter High Scores",
        "Set Job Completed",
        "Respond Success",
        "Error Trigger",
        "Format Error",
        "Set Job Failed",
    }
    missing = expected_names - node_names
    extras = node_names - expected_names
    assert not missing, f"Missing nodes: {sorted(missing)}"
    assert not extras, f"Unexpected extra nodes present: {sorted(extras)}"


def test_trigger_nodes_configured_correctly(workflow: dict) -> None:
    """Validate both trigger nodes for correct configuration."""
    webhook = _get_node(workflow, "Webhook Trigger")
    assert webhook["parameters"]["path"] == "start-discovery"
    assert webhook["parameters"]["httpMethod"] == "POST"
    assert webhook["parameters"]["responseCode"] == 202

    manual = _get_node(workflow, "Manual Trigger")
    assert manual["type"] == "n8n-nodes-base.manualTrigger"


def test_validation_branch_returns_400(workflow: dict) -> None:
    """The validation branch should return a 400 response with a consistent payload."""
    validate_node = _get_node(workflow, "Validate Input")
    conditions = validate_node["parameters"]["conditions"]["conditions"]
    assert len(conditions) == 1
    cond = conditions[0]
    assert cond["operator"]["operation"] == "isNotEmpty"
    assert cond["leftValue"] == "={{ $json.body.job_id }}"

    error_node = _get_node(workflow, "Return 400 Error")
    assert error_node["parameters"]["responseCode"] == 400
    response_body = error_node["parameters"]["responseBody"]
    assert "INVALID_INPUT" in response_body
    assert "job_id is required" in response_body


def test_http_nodes_target_backend_routes(workflow: dict) -> None:
    """Ensure HTTP nodes point at the documented FastAPI routes."""
    routes = _get_registered_routes()
    expected_routes: dict[str, Iterable[str]] = {
        "/api/jobs/{job_id}/status": {"PATCH"},
        "/api/profiles/{profile_id}/status": {"PATCH"},
        "/api/agent/analyze-brand": {"POST"},
        "/api/agent/discover": {"POST"},
        "/api/agent/score": {"POST"},
    }
    for path, methods in expected_routes.items():
        assert path in routes, f"Route {path} not registered in FastAPI app."
        for method in methods:
            assert method in routes[path], f"Route {path} missing method {method}"

    http_nodes = [
        "Set Job Analyzing",
        "Brand Analyzer Agent",
        "Set Job Discovering",
        "Discovery Agent",
        "Set Job Scoring",
        "Set Profile Processing",
        "Scorer Agent",
        "Set Profile Done",
        "Set Job Completed",
        "Set Job Failed",
    ]
    for node_name in http_nodes:
        node = _get_node(workflow, node_name)
        params = node["parameters"]
        assert params["sendHeaders"] is True
        headers = params["headerParameters"]["parameters"]
        header_names = {header["name"] for header in headers}
        assert "X-Service-Key" in header_names
        assert "Content-Type" in header_names
        url = params["url"]
        assert "={{ $env.FASTAPI_BASE_URL }}" in url, f"{node_name} url must use FASTAPI_BASE_URL"
        assert "/api/" in url, f"{node_name} should target a backend API path."


def test_batch_processing_configuration(workflow: dict) -> None:
    """Batch handling nodes should match documented configuration."""
    split_node = _get_node(workflow, "Split Profiles")
    assert split_node["parameters"]["batchSize"] == 5

    wait_node = _get_node(workflow, "Wait")
    assert wait_node["parameters"]["amount"] == 1
    assert wait_node["parameters"]["unit"] == "seconds"

    filter_node = _get_node(workflow, "Filter High Scores")
    condition = filter_node["parameters"]["conditions"]["conditions"][0]
    assert condition["operator"]["operation"] == "gte"
    assert condition["rightValue"] == 50


def test_error_handling_nodes(workflow: dict) -> None:
    """Error branch should propagate formatted messages to status endpoint."""
    error_trigger = _get_node(workflow, "Error Trigger")
    assert error_trigger["type"] == "n8n-nodes-base.errorTrigger"

    format_error = _get_node(workflow, "Format Error")
    raw_json = format_error["parameters"]["jsonOutput"]
    assert "error_message" in raw_json
    assert "Unknown error occurred" in raw_json

    set_failed = _get_node(workflow, "Set Job Failed")
    body = set_failed["parameters"]["jsonBody"]
    assert "\"status\": \"failed\"" in body
    assert "\"error_message\"" in body
