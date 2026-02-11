"""
PartnerScout AI - Profile Routes

API endpoints for profile-level actions (bookmarking).

Endpoints:
- PATCH /api/profiles/{profile_id}/bookmark - Toggle bookmark status
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import HttpStatus
from app.core.exceptions import ProfileNotFoundError
from app.guards.ownership import verify_profile_owner_user_only
from app.models.profile import BookmarkResponse
from app.repositories.profile_repo import ProfileRepository

logger = logging.getLogger(__name__)
router = APIRouter()


def get_profile_repository() -> ProfileRepository:
    return ProfileRepository()


@router.patch(
    "/profiles/{profile_id}/bookmark",
    response_model=BookmarkResponse,
    summary="Toggle profile bookmark",
    description="Toggle the bookmark status of a discovered profile.",
    responses={
        200: {"description": "Bookmark toggled successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Profile not found"},
    },
)
async def toggle_bookmark(
    profile_id: str,
    profile: dict = Depends(verify_profile_owner_user_only),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> BookmarkResponse:
    """Toggle the bookmark status of a profile."""
    try:
        updated = profile_repo.toggle_bookmark(profile_id)
        return BookmarkResponse(
            id=UUID(updated["id"]),
            is_bookmarked=updated["is_bookmarked"],
        )
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND, detail=str(e)
        )
