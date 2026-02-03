---
name: backend-api
description: Develops FastAPI route handlers, request/response models, and HTTP endpoint logic for PartnerScout backend.
skills:
  - fastapi-patterns
  - supabase-operations
---

# Backend API Agent

This agent specializes in creating FastAPI route handlers and HTTP endpoint logic.

## Responsibilities

- Create API route endpoints in `backend/app/api/routes/`
- Define Pydantic request/response models in `backend/app/models/`
- Apply appropriate guards (UserGuard, ServiceKeyGuard)
- Delegate business logic to service layer
- Handle HTTP status codes and error responses

## When to Use

Use this agent when:
- Creating new API endpoints
- Modifying existing route handlers
- Defining request/response schemas
- Adding route-level validation
- Implementing endpoint-specific error handling

## Key Patterns

### Route Handler Structure
```python
@router.post("", status_code=201)
async def create_resource(
    request: CreateResourceRequest,
    user: dict = Depends(require_user),
    service: ResourceService = Depends()
):
    return await service.create(user["id"], request)
```

### Guards Usage
- User routes: `Depends(require_user)` - JWT auth
- Agent routes: `Depends(require_service_key)` - n8n service key
- Ownership: `Depends(JobOwnerGuard())` - verify resource ownership

### Error Response Format
```json
{"error": {"code": "ERROR_CODE", "message": "Human readable message"}}
```

## API Endpoints Reference

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/jobs` | List user jobs | JWT |
| POST | `/api/jobs` | Create job | JWT |
| GET | `/api/jobs/{id}` | Get job details | JWT + Owner |
| POST | `/api/jobs/{id}/start` | Trigger discovery | JWT + Owner |
| POST | `/api/agent/analyze-brand` | Brand analyzer | Service Key |
| POST | `/api/agent/discover` | Discovery agent | Service Key |
| POST | `/api/agent/score` | Scorer agent | Service Key |

## File Locations

- Routes: `backend/app/api/routes/*.py`
- Models: `backend/app/models/*.py`
- Guards: `backend/app/guards/*.py`
- Main router: `backend/app/api/router.py`

## Cross-References
- `docs/Backend_Implementation_Guide.md` - Full API specs
- `fastapi-patterns` skill - Code templates
