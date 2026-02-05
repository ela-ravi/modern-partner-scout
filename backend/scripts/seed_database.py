#!/usr/bin/env python3
"""
Wrapper for setup seed script.

Run from backend directory:
    python scripts/seed_database.py [--reset] [--verify] [--tables ...]

Or use the setup script directly:
    python ../setup/scripts/seed_database.py [--reset] [--verify] [--tables ...]
"""
import runpy
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "setup" / "scripts" / "seed_database.py"

if not SCRIPT.exists():
    print(f"Error: {SCRIPT} not found")
    sys.exit(1)

runpy.run_path(str(SCRIPT), run_name="__main__")
