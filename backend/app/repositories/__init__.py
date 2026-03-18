"""
PartnerScout AI - Repositories Module

Provides repository classes for database operations on all entities.

Usage:
    from app.repositories import JobRepository, ProfileRepository
    
    job_repo = JobRepository()
    jobs = job_repo.list_by_user(user_id)
"""

from app.repositories.base_repo import BaseRepository
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository
from app.repositories.brand_repo import BrandRepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.contact_repo import ContactRepository

__all__ = [
    "BaseRepository",
    "JobRepository",
    "ProfileRepository",
    "BrandRepository",
    "ScoreRepository",
    "ContactRepository",
]
