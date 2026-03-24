# Implementation Plan: Items 1, 5, 8

> ✅ **STATUS: COMPLETED** (February 2026)
>
> All three items have been implemented and validated:
> - Item 1: Cancel Job Endpoint - `POST /api/jobs/{job_id}/cancel`
> - Item 5: Job Creation Enhancements - `keywords`, `hashtags`, `min_score_threshold`
> - Item 8: Demo Mode - `POST /api/demo/start`

---

## 1. Job Control Endpoints (Cancel/Stop Job) ✅ COMPLETED

**Design Reference:** `ai-agent-processing-pipeline.html` (Stop button visible during pipeline execution)

### Goal
Allow users to stop a running discovery job mid-execution.

### API Design

```
POST /api/jobs/{job_id}/cancel
Authorization: Bearer <jwt_token>
Response: 200 OK
```

**Response Body:**
```json
{
  "status": "cancelled",
  "job_id": "uuid",
  "cancelled_at": "2026-02-06T12:00:00Z",
  "message": "Discovery job cancelled successfully"
}
```

**Error Cases:**
- `404 NOT_FOUND` - Job doesn't exist
- `400 BAD_REQUEST` - Job is not in a cancellable state (already completed/cancelled/failed)
- `403 FORBIDDEN` - User doesn't own this job

### Implementation Steps

#### Step 1: Add Route in `backend/app/api/routes/jobs.py`

```python
@router.post("/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_job(
    job_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Cancel a running discovery job."""
    service = get_job_service()
    result = service.cancel_job(str(job_id), str(current_user.id))
    return result
```

#### Step 2: Add Response Model in `backend/app/models/job.py`

```python
class JobCancelResponse(BaseModel):
    """Response model for cancelling a job."""
    status: str = "cancelled"
    job_id: UUID
    cancelled_at: datetime
    message: str = "Discovery job cancelled successfully"
```

#### Step 3: Add Service Method in `backend/app/services/job_service.py`

```python
def cancel_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
    """
    Cancel a running job.
    
    Args:
        job_id: Job UUID to cancel
        user_id: User ID (for ownership verification)
        
    Returns:
        Cancellation confirmation
        
    Raises:
        JobNotFoundError: If job is not found
        BusinessError: If job cannot be cancelled
    """
    # Get job and verify ownership
    job = self.job_repo.get_by_id(job_id)
    current_status = JobStatus(job["status"])
    
    # Check if job can be cancelled
    cancellable = JobStatus.active_statuses() | {JobStatus.PENDING}
    if current_status not in cancellable:
        raise BusinessError(
            message=f"Job cannot be cancelled from status '{current_status.value}'",
            details={"job_id": job_id, "current_status": current_status.value}
        )
    
    # Update status to cancelled
    updated_job = self.update_status(
        job_id=job_id,
        new_status=JobStatus.CANCELLED,
        validate_transition=True,
    )
    
    return {
        "status": "cancelled",
        "job_id": job_id,
        "cancelled_at": datetime.utcnow().isoformat(),
        "message": "Discovery job cancelled successfully",
    }
```

#### Step 4: Update State Transitions (Already Done!)

The `JobStatus.CANCELLED` already exists in `constants.py` and valid transitions from `PENDING`, `ANALYZING`, `DISCOVERING`, `SCORING` → `CANCELLED` are already defined.

#### Step 5: (Optional) Orchestrator Callback

If the job was running in the orchestration pipeline, we may need to:
- Signal the orchestrator to cancel (if supported)
- Or let the orchestrator poll for job status and abort

**Files to modify:**
1. `backend/app/api/routes/jobs.py` - Add route
2. `backend/app/models/job.py` - Add response model
3. `backend/app/services/job_service.py` - Add `cancel_job()` method

**Estimated effort:** ~30 minutes

---

## 5. Job Creation Enhancements (Keywords, Hashtags, Min Score) ✅ COMPLETED

**Design Reference:** `discovery-engine-step1.html` (Shows input fields for Target Keywords/Hashtags, Minimum Score slider)

### Goal
Allow users to provide target keywords/hashtags and minimum score threshold when creating a discovery job, instead of only relying on AI extraction.

### Current State

Current `CreateJobRequest` model:
```python
class CreateJobRequest(BaseModel):
    brand_description: str
    reference_profiles: List[str]
    name: Optional[str] = None
    follower_range_min: int = 5000
    follower_range_max: int = 500000
    discovery_limit: int = 50
```

Current `discovery_jobs` table:
```sql
CREATE TABLE discovery_jobs (
    ...
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL,
    follower_range_min INTEGER,
    follower_range_max INTEGER,
    discovery_limit INTEGER,
    ...
);
```

### Target State

Add 3 new fields:
- `keywords: List[str]` - User-provided target keywords
- `hashtags: List[str]` - User-provided target hashtags  
- `min_score_threshold: int` - Minimum score filter (0-100, default 50)

### Database Schema Changes

**Migration: `004_job_creation_enhancements.sql`**
```sql
-- Add keywords and hashtags arrays to discovery_jobs
ALTER TABLE discovery_jobs 
ADD COLUMN keywords TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE discovery_jobs 
ADD COLUMN hashtags TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE discovery_jobs 
ADD COLUMN min_score_threshold INTEGER NOT NULL DEFAULT 50 
    CHECK (min_score_threshold >= 0 AND min_score_threshold <= 100);

-- Add comments
COMMENT ON COLUMN discovery_jobs.keywords IS 'User-provided target keywords for discovery';
COMMENT ON COLUMN discovery_jobs.hashtags IS 'User-provided target hashtags for discovery';
COMMENT ON COLUMN discovery_jobs.min_score_threshold IS 'Minimum score threshold for profile filtering (0-100)';
```

### API Changes

**Updated `POST /api/jobs` Request:**
```json
{
  "brand_description": "Sustainable fashion brand...",
  "reference_profiles": ["https://instagram.com/brand1", "https://instagram.com/brand2"],
  "name": "Summer Campaign Partners",
  "follower_range_min": 10000,
  "follower_range_max": 500000,
  "discovery_limit": 50,
  "keywords": ["sustainable", "eco-friendly", "slow fashion"],
  "hashtags": ["#sustainablefashion", "#ecofashion", "#slowfashion"],
  "min_score_threshold": 60
}
```

**Updated Response includes new fields:**
```json
{
  "id": "uuid",
  "keywords": ["sustainable", "eco-friendly"],
  "hashtags": ["#sustainablefashion"],
  "min_score_threshold": 60,
  ...
}
```

### Implementation Steps

#### Step 1: Create Database Migration

Create `supabase/migrations/004_job_creation_enhancements.sql`:

```sql
-- Migration: 004_job_creation_enhancements.sql
-- Description: Add keywords, hashtags, and min_score_threshold to discovery_jobs

ALTER TABLE discovery_jobs 
ADD COLUMN keywords TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE discovery_jobs 
ADD COLUMN hashtags TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE discovery_jobs 
ADD COLUMN min_score_threshold INTEGER NOT NULL DEFAULT 50 
    CHECK (min_score_threshold >= 0 AND min_score_threshold <= 100);

COMMENT ON COLUMN discovery_jobs.keywords IS 'User-provided target keywords for discovery';
COMMENT ON COLUMN discovery_jobs.hashtags IS 'User-provided target hashtags for discovery';
COMMENT ON COLUMN discovery_jobs.min_score_threshold IS 'Minimum score filter threshold (0-100)';

-- Update the v_job_summary view to include new fields
DROP VIEW IF EXISTS v_job_summary;
CREATE VIEW v_job_summary AS
SELECT 
    dj.id AS job_id,
    dj.user_id,
    dj.name,
    dj.brand_description,
    dj.keywords,
    dj.hashtags,
    dj.min_score_threshold,
    dj.status,
    dj.profiles_discovered,
    dj.profiles_scored,
    dj.created_at,
    dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    AVG(ps.final_score)::INTEGER AS avg_score,
    MAX(ps.final_score) AS max_score,
    MIN(ps.final_score) AS min_score,
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;
```

#### Step 2: Update Request Model in `backend/app/models/job.py`

```python
class CreateJobRequest(BaseModel):
    """Request model for creating a new discovery job."""
    
    brand_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the brand and its values"
    )
    reference_profiles: List[str] = Field(
        ...,
        min_length=Defaults.MIN_REFERENCE_PROFILES,
        max_length=Defaults.MAX_REFERENCE_PROFILES,
        description="List of Instagram profile URLs to use as reference"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional name for the discovery job"
    )
    follower_range_min: int = Field(
        default=Defaults.DEFAULT_MIN_FOLLOWERS,
        ge=Defaults.MIN_FOLLOWERS,
        le=Defaults.MAX_FOLLOWERS,
        description="Minimum followers for discovered profiles"
    )
    follower_range_max: int = Field(
        default=Defaults.DEFAULT_MAX_FOLLOWERS,
        ge=Defaults.MIN_FOLLOWERS,
        le=Defaults.MAX_FOLLOWERS,
        description="Maximum followers for discovered profiles"
    )
    discovery_limit: int = Field(
        default=Defaults.DEFAULT_DISCOVERY_LIMIT,
        ge=1,
        le=Defaults.MAX_DISCOVERY_LIMIT,
        description="Maximum number of profiles to discover"
    )
    
    # NEW FIELDS
    keywords: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Target keywords for discovery (optional, AI will extract if empty)"
    )
    hashtags: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Target hashtags for discovery (optional, AI will extract if empty)"
    )
    min_score_threshold: int = Field(
        default=Defaults.DEFAULT_MIN_SCORE_THRESHOLD,
        ge=0,
        le=100,
        description="Minimum score threshold for profile filtering"
    )
    
    @field_validator("keywords", mode="before")
    @classmethod
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Clean and validate keywords."""
        if not v:
            return []
        return [kw.strip().lower() for kw in v if kw.strip()]
    
    @field_validator("hashtags", mode="before")
    @classmethod
    def validate_hashtags(cls, v: List[str]) -> List[str]:
        """Clean and normalize hashtags (ensure # prefix)."""
        if not v:
            return []
        normalized = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            normalized.append(tag)
        return normalized
```

#### Step 3: Update Response Models in `backend/app/models/job.py`

```python
class JobBase(BaseModel):
    """Base job model with common fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    brand_description: str
    reference_profiles: List[str]
    follower_range_min: int
    follower_range_max: int
    discovery_limit: int
    keywords: List[str] = Field(default_factory=list)  # NEW
    hashtags: List[str] = Field(default_factory=list)  # NEW
    min_score_threshold: int = 50  # NEW
    status: JobStatus
    profiles_discovered: int = 0
    profiles_scored: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
```

#### Step 4: Update Job Service in `backend/app/services/job_service.py`

```python
def create_job(
    self,
    user_id: str,
    brand_description: str,
    reference_profiles: List[str],
    name: Optional[str] = None,
    follower_range_min: int = 5000,
    follower_range_max: int = 500000,
    discovery_limit: int = 50,
    keywords: Optional[List[str]] = None,      # NEW
    hashtags: Optional[List[str]] = None,      # NEW
    min_score_threshold: int = 50,             # NEW
) -> Dict[str, Any]:
    """Create a new discovery job with daily limit enforcement."""
    
    # ... existing validation ...
    
    job = self.job_repo.create(
        user_id=user_id,
        brand_description=brand_description,
        reference_profiles=reference_profiles,
        name=name,
        follower_range_min=follower_range_min,
        follower_range_max=follower_range_max,
        discovery_limit=discovery_limit,
        keywords=keywords or [],           # NEW
        hashtags=hashtags or [],           # NEW
        min_score_threshold=min_score_threshold,  # NEW
    )
    
    return job
```

#### Step 5: Update Job Repository in `backend/app/repositories/job_repo.py`

```python
def create(
    self,
    user_id: str,
    brand_description: str,
    reference_profiles: List[str],
    name: Optional[str] = None,
    follower_range_min: int = 5000,
    follower_range_max: int = 500000,
    discovery_limit: int = 50,
    keywords: Optional[List[str]] = None,
    hashtags: Optional[List[str]] = None,
    min_score_threshold: int = 50,
) -> Dict[str, Any]:
    """Create a new discovery job."""
    
    data = {
        "user_id": user_id,
        "brand_description": brand_description,
        "reference_profiles": reference_profiles,
        "name": name,
        "follower_range_min": follower_range_min,
        "follower_range_max": follower_range_max,
        "discovery_limit": discovery_limit,
        "keywords": keywords or [],
        "hashtags": hashtags or [],
        "min_score_threshold": min_score_threshold,
        "status": JobStatus.PENDING.value,
    }
    
    # ... insert into DB ...
```

#### Step 6: Update API Route in `backend/app/api/routes/jobs.py`

```python
@router.post("", response_model=Job, status_code=201)
async def create_job(
    request: CreateJobRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Create a new discovery job."""
    service = get_job_service()
    job = service.create_job(
        user_id=str(current_user.id),
        brand_description=request.brand_description,
        reference_profiles=request.reference_profiles,
        name=request.name,
        follower_range_min=request.follower_range_min,
        follower_range_max=request.follower_range_max,
        discovery_limit=request.discovery_limit,
        keywords=request.keywords,              # NEW
        hashtags=request.hashtags,              # NEW
        min_score_threshold=request.min_score_threshold,  # NEW
    )
    return job
```

#### Step 7: Update Orchestrator Webhook Payload

In `trigger_discovery()` method, include new fields:

```python
payload = {
    "job_id": job_id,
    "user_id": user_id,
    "brand_description": job["brand_description"],
    "reference_profiles": job["reference_profiles"],
    "follower_range_min": job["follower_range_min"],
    "follower_range_max": job["follower_range_max"],
    "discovery_limit": job["discovery_limit"],
    "keywords": job.get("keywords", []),           # NEW
    "hashtags": job.get("hashtags", []),           # NEW
    "min_score_threshold": job.get("min_score_threshold", 50),  # NEW
}
```

#### Step 8: Update Constants

In `backend/app/core/constants.py`:
```python
class Defaults:
    # ... existing ...
    MAX_KEYWORDS = 20
    MAX_HASHTAGS = 20
    DEFAULT_MIN_SCORE_THRESHOLD = 50
```

**Files to modify:**
1. `supabase/migrations/004_job_creation_enhancements.sql` - New migration
2. `backend/app/models/job.py` - Add fields to CreateJobRequest, JobBase
3. `backend/app/services/job_service.py` - Add params to create_job()
4. `backend/app/repositories/job_repo.py` - Add params to create()
5. `backend/app/api/routes/jobs.py` - Pass new fields
6. `backend/app/core/constants.py` - Add new defaults

**Estimated effort:** ~1 hour

---

## 8. Demo/Seed Data Endpoint ✅ COMPLETED

**Design Reference:** `empty-dashboard.html` (Shows "Watch Demo" button when no sessions exist)

### Goal
Create a demo job with pre-seeded profiles so users can experience the product without waiting for actual discovery.

### API Design

```
POST /api/demo/start
Authorization: Bearer <jwt_token> (optional - could work for anonymous demo)
Response: 201 Created
```

**Response Body:**
```json
{
  "job_id": "demo-uuid",
  "status": "completed",
  "message": "Demo job created with 10 sample profiles",
  "profiles_count": 10,
  "redirect_url": "/jobs/demo-uuid"
}
```

### Implementation Steps

#### Step 1: Create Demo Data Seed File

Create `backend/app/data/demo_seed.py`:

```python
"""Demo seed data for Watch Demo feature."""

DEMO_BRAND_DESCRIPTION = """
EcoLife is a sustainable lifestyle brand focused on eco-friendly products 
and mindful living. We promote minimalist aesthetics, organic materials, 
and environmental consciousness through our curated collection of home 
goods and personal care items.
"""

DEMO_BRAND_DNA = {
    "hashtags": ["#sustainable", "#ecofriendly", "#minimalist", "#zerowaste"],
    "keywords": ["sustainable", "eco", "organic", "minimalist", "green living"],
    "visual_themes": ["clean aesthetics", "nature", "neutral colors", "minimal"],
    "content_pillars": ["sustainability tips", "product showcases", "lifestyle", "DIY"],
    "target_audience_description": "Environmentally conscious millennials and Gen-Z"
}

DEMO_PROFILES = [
    {
        "username": "eco_lifestyle_jane",
        "full_name": "Jane Green",
        "bio": "🌿 Living sustainably | Sharing eco-tips daily | Collab: jane@ecolife.co",
        "followers_count": 45000,
        "following_count": 890,
        "posts_count": 342,
        "engagement_rate": 4.2,
        "is_verified": False,
        "is_business_account": True,
        "score": 92,
        "recommendation": "highly_recommended",
        "contact_email": "jane@ecolife.co",
        "dimension_scores": {
            "visual_aesthetic_match": 95,
            "content_theme_alignment": 90,
            "engagement_rate_score": 88,
            "follower_quality": 92,
            "business_indicators": 90,
            "activity_recency": 95,
        }
    },
    {
        "username": "minimal_home_studio",
        "full_name": "Minimal Home Studio",
        "bio": "✨ Curated minimalist spaces | Interior inspo | DM for collabs",
        "followers_count": 128000,
        "following_count": 450,
        "posts_count": 567,
        "engagement_rate": 3.8,
        "is_verified": True,
        "is_business_account": True,
        "score": 88,
        "recommendation": "highly_recommended",
        "contact_email": "hello@minimalhome.co",
        "dimension_scores": {
            "visual_aesthetic_match": 92,
            "content_theme_alignment": 85,
            "engagement_rate_score": 82,
            "follower_quality": 90,
            "business_indicators": 88,
            "activity_recency": 90,
        }
    },
    {
        "username": "green_living_tips",
        "full_name": "Sarah's Green Journey",
        "bio": "🌱 Zero waste advocate | Mom of 2 | Tips for sustainable families",
        "followers_count": 67000,
        "following_count": 1200,
        "posts_count": 890,
        "engagement_rate": 5.1,
        "is_verified": False,
        "is_business_account": False,
        "score": 85,
        "recommendation": "recommended",
        "contact_email": None,
        "dimension_scores": {
            "visual_aesthetic_match": 78,
            "content_theme_alignment": 95,
            "engagement_rate_score": 92,
            "follower_quality": 80,
            "business_indicators": 70,
            "activity_recency": 88,
        }
    },
    # Add 7 more profiles with varying scores (75, 72, 68, 65, 58, 52, 45)
    # to show the full range of recommendations
]
```

#### Step 2: Create Demo Service `backend/app/services/demo_service.py`

```python
"""Demo service for creating seeded demo jobs."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from app.core.constants import JobStatus, ProfileStatus
from app.repositories import JobRepository, ProfileRepository
from app.repositories.brand_dna_repo import BrandDNARepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.contact_repo import ContactRepository


class DemoService:
    """Service for creating demo jobs with seeded data."""
    
    def __init__(self):
        self.job_repo = JobRepository()
        self.profile_repo = ProfileRepository()
        self.brand_dna_repo = BrandDNARepository()
        self.score_repo = ScoreRepository()
        self.contact_repo = ContactRepository()
    
    def create_demo_job(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a demo job with pre-seeded profiles.
        
        Args:
            user_id: Optional user ID (uses demo user if not provided)
            
        Returns:
            Demo job details with redirect URL
        """
        from app.data.demo_seed import (
            DEMO_BRAND_DESCRIPTION, 
            DEMO_BRAND_DNA, 
            DEMO_PROFILES
        )
        
        # Use provided user_id or generate demo user
        effective_user_id = user_id or str(uuid4())
        
        # Create job directly in completed state
        job = self.job_repo.create(
            user_id=effective_user_id,
            brand_description=DEMO_BRAND_DESCRIPTION.strip(),
            reference_profiles=[
                "https://instagram.com/ecolife_brand",
                "https://instagram.com/sustainable_co"
            ],
            name="[DEMO] Sustainable Lifestyle Partners",
            follower_range_min=5000,
            follower_range_max=500000,
            discovery_limit=10,
            keywords=DEMO_BRAND_DNA["keywords"],
            hashtags=DEMO_BRAND_DNA["hashtags"],
            min_score_threshold=50,
        )
        
        job_id = job["id"]
        
        # Mark job as completed immediately
        self.job_repo.update_status(
            id=job_id,
            status=JobStatus.COMPLETED,
        )
        
        # Insert brand DNA
        self.brand_dna_repo.create(
            job_id=job_id,
            hashtags=DEMO_BRAND_DNA["hashtags"],
            keywords=DEMO_BRAND_DNA["keywords"],
            visual_themes=DEMO_BRAND_DNA["visual_themes"],
            content_pillars=DEMO_BRAND_DNA["content_pillars"],
            target_audience_description=DEMO_BRAND_DNA["target_audience_description"],
        )
        
        # Insert demo profiles with scores and contacts
        for profile_data in DEMO_PROFILES:
            profile = self.profile_repo.create(
                job_id=job_id,
                instagram_url=f"https://instagram.com/{profile_data['username']}",
                username=profile_data["username"],
                full_name=profile_data["full_name"],
                bio=profile_data["bio"],
                followers_count=profile_data["followers_count"],
                following_count=profile_data.get("following_count"),
                posts_count=profile_data.get("posts_count"),
                engagement_rate=profile_data["engagement_rate"],
                is_verified=profile_data["is_verified"],
                is_business_account=profile_data.get("is_business_account", False),
                status=ProfileStatus.SCORED.value,
            )
            
            profile_id = profile["id"]
            
            # Insert score
            dims = profile_data.get("dimension_scores", {})
            self.score_repo.create(
                profile_id=profile_id,
                final_score=profile_data["score"],
                recommendation=profile_data["recommendation"],
                visual_aesthetic_match=dims.get("visual_aesthetic_match", 75),
                content_theme_alignment=dims.get("content_theme_alignment", 75),
                engagement_rate_score=dims.get("engagement_rate_score", 75),
                follower_quality=dims.get("follower_quality", 75),
                business_indicators=dims.get("business_indicators", 75),
                activity_recency=dims.get("activity_recency", 75),
                reasoning={"demo": True, "note": "Pre-seeded demo data"},
            )
            
            # Insert contact if email available
            if profile_data.get("contact_email"):
                self.contact_repo.create(
                    profile_id=profile_id,
                    email=profile_data["contact_email"],
                    email_source="bio",
                )
        
        return {
            "job_id": job_id,
            "status": "completed",
            "message": f"Demo job created with {len(DEMO_PROFILES)} sample profiles",
            "profiles_count": len(DEMO_PROFILES),
            "redirect_url": f"/jobs/{job_id}",
            "is_demo": True,
        }
```

#### Step 3: Create Routes File `backend/app/api/routes/demo.py`

```python
"""Demo routes for Watch Demo feature."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.auth.deps import get_optional_current_user
from app.services.demo_service import DemoService


router = APIRouter(prefix="/demo", tags=["demo"])


class DemoStartResponse(BaseModel):
    """Response model for starting a demo."""
    job_id: UUID
    status: str
    message: str
    profiles_count: int
    redirect_url: str
    is_demo: bool = True


@router.post("/start", response_model=DemoStartResponse, status_code=201)
async def start_demo(
    current_user = Depends(get_optional_current_user),
):
    """
    Create a demo job with pre-seeded profiles.
    
    Works for both authenticated and anonymous users.
    The demo job is immediately in 'completed' status with
    10 sample profiles pre-scored for exploration.
    """
    try:
        service = DemoService()
        user_id = str(current_user.id) if current_user else None
        result = service.create_demo_job(user_id=user_id)
        return DemoStartResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create demo job: {str(e)}"
        )


@router.delete("/cleanup", status_code=204)
async def cleanup_demo_jobs(
    current_user = Depends(get_optional_current_user),
):
    """
    Delete all demo jobs for the current user.
    
    Useful for cleaning up after demo exploration.
    """
    # Implementation: Delete jobs where name starts with "[DEMO]"
    pass
```

#### Step 4: Register Route in `backend/app/main.py`

```python
from app.api.routes import demo

# Add to existing router registrations
app.include_router(demo.router, prefix="/api")
```

#### Step 5: Add Authentication Helper

If not exists, create `get_optional_current_user` in `backend/app/auth/deps.py`:

```python
async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[AuthenticatedUser]:
    """
    Get current user if authenticated, None otherwise.
    
    Unlike get_current_user, this doesn't raise on missing auth.
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
```

**Files to create/modify:**
1. `backend/app/data/__init__.py` - Create package
2. `backend/app/data/demo_seed.py` - Demo data definitions
3. `backend/app/services/demo_service.py` - Demo service
4. `backend/app/api/routes/demo.py` - Demo routes
5. `backend/app/main.py` - Register demo router
6. `backend/app/auth/deps.py` - Add optional auth helper (if needed)

**Estimated effort:** ~1.5 hours

---

## Summary

| Item | Description | Complexity | Effort |
|------|-------------|------------|--------|
| 1. Job Control | Cancel/stop running jobs | Low | 30 min |
| 5. Job Creation Enhancements | Keywords, hashtags, min_score | Medium | 1 hour |
| 8. Demo/Seed Data | Pre-seeded demo job | Medium | 1.5 hours |

**Total estimated time:** ~3 hours

### Recommended Implementation Order

1. **Job Creation Enhancements** - Schema changes first (migration)
2. **Job Control (Cancel)** - Quick win, simple addition
3. **Demo Mode** - Depends on #5 for keywords/hashtags support

### Dependency Graph

```
Job Creation Enhancements (#5)
         │
         ▼
    Demo Mode (#8) ──── uses keywords/hashtags
         
Cancel Job (#1) ──── independent, can be done anytime
```

---

*Last updated: February 2026*
