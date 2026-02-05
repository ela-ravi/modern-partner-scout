"""
PartnerScout AI Backend Application.
"""

__version__ = "0.1.0"

# Ensure app.db can be referenced for patching in tests.
from app import db as db  # noqa: F401
