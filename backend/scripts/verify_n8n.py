#!/usr/bin/env python3
"""
N8N Environment Verification Script

STORY-4.1.1: Verifies N8N is running and accessible.
Validates configuration required for PartnerScout workflow orchestration.

Usage:
    python -m scripts.verify_n8n
"""

import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv()

# Default N8N URL when not in env
DEFAULT_N8N_URL = "http://localhost:5678"

# Use ASCII checkmark for Windows compatibility (cp1252 can't encode \u2713)
_OK = "[OK]"
_NOK = "[FAIL]"
_WARN = "[WARN]"


def get_n8n_base_url() -> str:
    """Extract N8N base URL from N8N_WEBHOOK_URL or use default."""
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    if webhook_url and not webhook_url.startswith("your-"):
        parsed = urlparse(webhook_url)
        return f"{parsed.scheme}://{parsed.netloc}"
    return DEFAULT_N8N_URL


def check_n8n_env_vars() -> bool:
    """Check that N8N-related environment variables are configured."""
    service_key = os.getenv("N8N_SERVICE_KEY", "")
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")

    issues = []

    if not service_key or service_key.startswith("your-"):
        issues.append("N8N_SERVICE_KEY is not set or uses placeholder value")

    if not webhook_url or webhook_url.startswith("your-"):
        print(
            f"{_WARN} N8N_WEBHOOK_URL not set - using default {DEFAULT_N8N_URL}/webhook/..."
        )
    else:
        print(f"{_OK} N8N_WEBHOOK_URL: {webhook_url}")

    if issues:
        print(f"{_NOK} Configuration issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   Update backend/.env - N8N_SERVICE_KEY must be set.")
        return False

    print(f"{_OK} N8N_SERVICE_KEY is configured")
    return True


def check_n8n_connectivity() -> bool:
    """Test connectivity to N8N instance."""
    base_url = get_n8n_base_url()

    try:
        import httpx

        # Try /healthz first (if enabled), fallback to root
        endpoints = ["/healthz", "/"]
        last_error = None

        for path in endpoints:
            url = f"{base_url.rstrip('/')}{path}"
            try:
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(url)
                    if response.status_code in (200, 302, 307):
                        print(f"{_OK} N8N is running and accessible at {base_url}")
                        return True
                    last_error = f"HTTP {response.status_code}"
            except Exception as e:
                last_error = str(e)

        print(f"{_NOK} Cannot connect to N8N at {base_url}")
        print(f"   Error: {last_error}")
        print("\n   Ensure N8N is running:")
        print("   - Docker: docker compose -f docker-compose.n8n.yml up -d")
        print("   - npm:    n8n start")
        return False

    except ImportError:
        print(f"{_NOK} httpx not installed - run: pip install httpx")
        return False


def main() -> int:
    """Run all N8N verification checks."""
    print("=" * 60)
    print("PartnerScout AI - N8N Environment Verification")
    print("STORY-4.1.1: Setup N8N Environment")
    print("=" * 60)
    print()

    # Check 1: Environment variables
    print("[1/2] Checking N8N configuration...")
    if not check_n8n_env_vars():
        print()
        sys.exit(1)
    print()

    # Check 2: Connectivity
    print("[2/2] Testing N8N connectivity...")
    if not check_n8n_connectivity():
        print()
        sys.exit(1)
    print()

    print("=" * 60)
    print(f"{_OK} N8N environment verification complete!")
    print("  Access N8N at:", get_n8n_base_url())
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
