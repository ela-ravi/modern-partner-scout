---
name: fastapi-patterns
description: Build FastAPI backend services with proper layered architecture. Use this skill when implementing API routes, guards, services, repositories, Pydantic models, or error handling for the PartnerScout backend.
---

This skill guides the development of FastAPI backend services for PartnerScout, following a layered architecture with guards, services, and repositories.

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Guards Layer                            │
│  (guards/auth.py, guards/validation.py, guards/ownership.py)│
│  - Authentication (JWT, Service Key)                         │
│  - Input validation                                          │
│  - Resource ownership verification                           │
├─────────────────────────────────────────────────────────────┤
│                      API Layer                               │
│  (routes/jobs.py, routes/agents.py, routes/email.py)        │
│  - HTTP request/response handling                            │
│  - Route definitions                                         │
│  - Response formatting                                       │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer (Business Logic)            │
│  (services/job_service.py, services/scoring_service.py)     │
│  - All business rules                                        │
│  - Workflow orchestration                                    │
│  - Data transformation                                       │
├─────────────────────────────────────────────────────────────┤
│                    Repository Layer                          │
│  (repositories/job_repo.py, repositories/profile_repo.py)  │
│  - Database operations only                                  │
│  - No business logic                                         │
│  - Query builders                                            │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
backend/app/
├── main.py                    # FastAPI app entry point
├── core/
│   ├── config.py              # Environment variables
│   ├── constants.py           # Enums, error codes
│   └── exceptions.py          # Custom exceptions
├── guards/
│   ├── auth.py                # AuthGuard, UserGuard, ServiceKeyGuard
│   ├── ownership.py           # JobOwnerGuard, ProfileOwnerGuard
│   └── validation.py          # StatusTransitionGuard
├── api/
│   └── routes/
│       ├── jobs.py            # /api/jobs/* endpoints
│       ├── agents.py          # /api/agent/* endpoints
│       └── email.py           # /api/email/* endpoints
├── services/
│   ├── job_service.py         # Job business logic
│   └── scoring_service.py     # Scoring calculations
├── repositories/
│   ├── base_repo.py           # Base repository class
│   └── job_repo.py            # Job CRUD operations
└── models/
    ├── job.py                 # Job Pydantic models
    └── profile.py             # Profile Pydantic models
```

## Guard Pattern

Guards validate requests before route handlers:

```python
# guards/auth.py
from fastapi import Header, HTTPException
from app.core.constants import ErrorCodes, HttpStatus
from app.core.config import settings
import jwt

class UserGuard:
    """Validates Supabase JWT and extracts user context."""
    
    async def __call__(self, authorization: str = Header(...)):
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=HttpStatus.UNAUTHORIZED,
                detail={"code": ErrorCodes.INVALID_TOKEN, "message": "Bearer token required"}
            )
        
        token = authorization.replace("Bearer ", "")
        
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            return {"id": payload.get("sub"), "email": payload.get("email")}
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HttpStatus.UNAUTHORIZED,
                detail={"code": ErrorCodes.TOKEN_EXPIRED, "message": "Token expired"}
            )

require_user = UserGuard()


class ServiceKeyGuard:
    """Validates X-Service-Key header for n8n/orchestrator requests."""
    
    async def __call__(self, x_service_key: str = Header(..., alias="X-Service-Key")):
        if x_service_key != settings.N8N_SERVICE_KEY:
            raise HTTPException(
                status_code=HttpStatus.UNAUTHORIZED,
                detail={"code": ErrorCodes.INVALID_SERVICE_KEY, "message": "Invalid service key"}
            )
        return True

require_service_key = ServiceKeyGuard()
```

## Ownership Guard

```python
# guards/ownership.py
from fastapi import Depends, HTTPException
from app.guards.auth import require_user
from app.repositories.job_repo import JobRepository
from app.core.constants import ErrorCodes, HttpStatus

class JobOwnerGuard:
    """Verifies the authenticated user owns the requested job."""
    
    def __init__(self, job_repo: JobRepository = Depends()):
        self.job_repo = job_repo
    
    async def __call__(self, job_id: str, user: dict = Depends(require_user)):
        job = await self.job_repo.get_by_id(job_id)
        
        if not job:
            raise HTTPException(
                status_code=HttpStatus.NOT_FOUND,
                detail={"code": ErrorCodes.JOB_NOT_FOUND, "message": f"Job {job_id} not found"}
            )
        
        if job.user_id != user["id"]:
            raise HTTPException(
                status_code=HttpStatus.FORBIDDEN,
                detail={"code": ErrorCodes.FORBIDDEN, "message": "Access denied"}
            )
        
        return job
```

## Route Handler Pattern

Routes should be thin and delegate to services:

```python
# routes/jobs.py
from fastapi import APIRouter, Depends
from app.guards.auth import require_user
from app.guards.ownership import JobOwnerGuard
from app.services.job_service import JobService
from app.models.job import CreateJobRequest, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("")
async def list_jobs(
    user: dict = Depends(require_user),
    job_service: JobService = Depends()
):
    """List all jobs for the authenticated user."""
    return await job_service.list_user_jobs(user["id"])

@router.post("", status_code=201)
async def create_job(
    request: CreateJobRequest,
    user: dict = Depends(require_user),
    job_service: JobService = Depends()
):
    """Create new discovery job."""
    return await job_service.create_job(user["id"], request)

@router.get("/{job_id}")
async def get_job(
    job = Depends(JobOwnerGuard()),
    job_service: JobService = Depends()
):
    """Get job details with profiles."""
    return await job_service.get_job_with_profiles(job)

@router.post("/{job_id}/start", status_code=202)
async def start_job(
    job = Depends(JobOwnerGuard()),
    job_service: JobService = Depends()
):
    """Start discovery workflow."""
    return await job_service.trigger_discovery(job)

@router.delete("/{job_id}")
async def delete_job(
    job = Depends(JobOwnerGuard()),
    job_service: JobService = Depends()
):
    """Delete job and all related data."""
    return await job_service.delete_job(job)
```

## Service Layer Pattern

Services contain all business logic:

```python
# services/job_service.py
from fastapi import Depends
from app.repositories.job_repo import JobRepository
from app.core.constants import JobStatus, ErrorCodes, Defaults
from app.core.exceptions import BusinessError

class JobService:
    def __init__(self, job_repo: JobRepository = Depends()):
        self.job_repo = job_repo
    
    async def create_job(self, user_id: str, data: CreateJobRequest) -> Job:
        # Business rule: Check profile count
        if len(data.reference_profiles) < Defaults.MIN_REFERENCE_PROFILES:
            raise BusinessError(
                code=ErrorCodes.INSUFFICIENT_PROFILES,
                message=f"At least {Defaults.MIN_REFERENCE_PROFILES} profiles required"
            )
        
        return await self.job_repo.create(
            user_id=user_id,
            brand_description=data.brand_description,
            reference_profiles=data.reference_profiles
        )
    
    async def trigger_discovery(self, job: Job) -> dict:
        # Business rule: Can only start pending jobs
        if job.status != JobStatus.PENDING:
            raise BusinessError(
                code=ErrorCodes.JOB_ALREADY_STARTED,
                message=f"Job is already in '{job.status}' status"
            )
        
        # Call n8n webhook
        # ...
        return {"status": "accepted", "job_id": str(job.id)}
```

## Pydantic Models

```python
# models/job.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DISCOVERING = "discovering"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"

class CreateJobRequest(BaseModel):
    brand_description: str = Field(..., min_length=10)
    reference_profiles: List[str] = Field(..., min_items=2, max_items=10)
    name: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    user_id: str
    name: Optional[str]
    brand_description: str
    status: JobStatus
    profiles_discovered: int
    profiles_scored: int
    created_at: datetime
    updated_at: datetime
```

## Error Handling

Consistent error response format:

```python
# core/exceptions.py
from fastapi import HTTPException
from app.core.constants import HttpStatus

class BusinessError(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = HttpStatus.BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message}
        )

class NotFoundError(BusinessError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} {id} not found",
            status_code=HttpStatus.NOT_FOUND
        )
```

## Constants

```python
# core/constants.py
from enum import Enum

class HttpStatus:
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

class ErrorCodes:
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    FORBIDDEN = "FORBIDDEN"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    JOB_ALREADY_STARTED = "JOB_ALREADY_STARTED"

class JobStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DISCOVERING = "discovering"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"

VALID_JOB_TRANSITIONS = {
    JobStatus.PENDING: [JobStatus.ANALYZING, JobStatus.FAILED],
    JobStatus.ANALYZING: [JobStatus.DISCOVERING, JobStatus.FAILED],
    JobStatus.DISCOVERING: [JobStatus.SCORING, JobStatus.FAILED],
    JobStatus.SCORING: [JobStatus.COMPLETED, JobStatus.FAILED],
    JobStatus.COMPLETED: [],
    JobStatus.FAILED: [JobStatus.PENDING],
}
```

## Main App Setup

```python
# main.py
from fastapi import FastAPI
from app.api.routes import jobs, agents, email

app = FastAPI(title="PartnerScout API")

app.include_router(jobs.router)
app.include_router(agents.router)
app.include_router(email.router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
```

## Dependencies

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
PyJWT>=2.8.0
httpx>=0.26.0
```

## Best Practices

1. **Thin Routes**: Routes delegate to services immediately
2. **Guards First**: Validate auth/ownership before business logic
3. **Services Own Logic**: All business rules in service layer
4. **Consistent Errors**: Use standard error response format
5. **Type Everything**: Pydantic models for all request/response
6. **Dependency Injection**: Use FastAPI Depends() pattern
7. **Async All The Way**: Async functions for all I/O
