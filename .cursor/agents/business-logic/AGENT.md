---
name: business-logic
description: Implements service layer business logic, validation rules, and workflow coordination for PartnerScout.
skills:
  - fastapi-patterns
  - supabase-operations
---

# Business Logic Agent

This agent specializes in service layer implementation and business rule enforcement.

## Responsibilities

- Implement service classes in `backend/app/services/`
- Enforce business rules and validation
- Coordinate between repositories and agents
- Handle complex workflows and state transitions
- Implement rate limiting and quota checks

## When to Use

Use this agent when:
- Creating new service classes
- Adding business validation rules
- Implementing complex workflows
- Coordinating multiple repository operations
- Enforcing limits and quotas

## Key Patterns

### Service Class Structure
```python
class JobService:
    def __init__(self, job_repo: JobRepository = Depends(), profile_repo: ProfileRepository = Depends()):
        self.job_repo = job_repo
        self.profile_repo = profile_repo
    
    async def create_job(self, user_id: str, data: CreateJobRequest) -> Job:
        # Business validation
        today_count = await self.job_repo.count_user_jobs_today(user_id)
        if today_count >= 10:
            raise BusinessError(code="DAILY_LIMIT_EXCEEDED", message="Daily limit exceeded")
        
        # Delegate to repository
        return await self.job_repo.create(user_id=user_id, **data.dict())
```

### Business Rules

| Rule | Description |
|------|-------------|
| Daily job limit | Max 10 jobs per user per day |
| Min reference profiles | At least 2 profiles required |
| Max reference profiles | At most 10 profiles |
| Valid status transitions | pending→analyzing→discovering→scoring→completed |

### Status Transitions
```python
VALID_JOB_TRANSITIONS = {
    "pending": ["analyzing", "failed"],
    "analyzing": ["discovering", "failed"],
    "discovering": ["scoring", "failed"],
    "scoring": ["completed", "failed"],
    "completed": [],
    "failed": [],
}
```

## File Locations

- Services: `backend/app/services/*.py`
- Exceptions: `backend/app/core/exceptions.py`
- Constants: `backend/app/core/constants.py`

## Cross-References
- `docs/Backend_Implementation_Guide.md` - Service patterns
- `fastapi-patterns` skill - Code templates
