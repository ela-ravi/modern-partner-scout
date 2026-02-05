#!/usr/bin/env python3
"""
Wrapper for setup validation script.

Run from backend directory:
    python scripts/validate_epic1.py

Or use the setup script directly:
    python ../setup/scripts/validate_epic1.py
"""
import runpy
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "setup" / "scripts" / "validate_epic1.py"

if not SCRIPT.exists():
    print(f"Error: {SCRIPT} not found")
    sys.exit(1)

runpy.run_path(str(SCRIPT), run_name="__main__")
