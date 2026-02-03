---
name: n8n-workflows
description: Build n8n workflow orchestration for PartnerScout. Use for designing workflows, HTTP nodes, error handling, batch processing, and status updates.
version: 1.0.0
---

# n8n Workflows Skill

Patterns for n8n orchestration in PartnerScout.

## When to Use

- Designing workflow nodes and connections
- Configuring HTTP request nodes
- Implementing error handling
- Setting up batch processing
- Managing status updates

## Guidelines

1. **Use environment variables** for API URLs and keys
2. **Always include Error Trigger** for failure handling
3. **Use Split In Batches** for parallel processing
4. **Add Wait nodes** for rate limiting
5. **Update job status** at each phase transition

---

## Workflow Architecture

```
Webhook Trigger
    ↓
Update Status → "analyzing"
    ↓
Brand Analyzer Agent (HTTP)
    ↓
Update Status → "discovering"
    ↓
Discovery Agent (HTTP)
    ↓
Update Status → "scoring"
    ↓
Split In Batches (profiles)
    ↓
Scorer Agent (HTTP) ←──┐
    ↓                   │
Update Profile Status   │
    ↓                   │
Loop ───────────────────┘
    ↓
Update Status → "completed"
```

---

## Node Templates

### Webhook Trigger

```json
{
  "name": "Webhook Trigger",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "path": "discovery-workflow",
    "httpMethod": "POST",
    "responseMode": "onReceived",
    "responseCode": 202
  }
}
```

### HTTP Request to Agent

```json
{
  "name": "Brand Analyzer",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $env.API_BASE_URL }}/api/agent/analyze-brand",
    "method": "POST",
    "headers": {
      "X-Service-Key": "={{ $env.SERVICE_KEY }}",
      "Content-Type": "application/json"
    },
    "body": {
      "job_id": "={{ $json.job_id }}",
      "brand_description": "={{ $json.brand_description }}"
    },
    "options": { "timeout": 120000 }
  }
}
```

### Status Update Node

```json
{
  "name": "Update Job Status",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $env.API_BASE_URL }}/api/jobs/{{ $json.job_id }}/status",
    "method": "PATCH",
    "headers": { "X-Service-Key": "={{ $env.SERVICE_KEY }}" },
    "body": { "status": "analyzing" }
  }
}
```

### Split In Batches

```json
{
  "name": "Process Profiles",
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": { "batchSize": 5 }
}
```

### Error Handler

```json
{
  "name": "Handle Error",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $env.API_BASE_URL }}/api/jobs/{{ $json.job_id }}/status",
    "method": "PATCH",
    "headers": { "X-Service-Key": "={{ $env.SERVICE_KEY }}" },
    "body": { "status": "failed", "error_message": "={{ $json.error.message }}" }
  }
}
```

---

## Environment Variables

```bash
API_BASE_URL=http://localhost:8000
SERVICE_KEY=your-secret-service-key
```

---

## Python Fallback Script

```python
import httpx, asyncio, os

async def run_discovery(job_id: str):
    base_url = os.getenv("API_BASE_URL")
    headers = {"X-Service-Key": os.getenv("SERVICE_KEY")}
    
    async with httpx.AsyncClient() as client:
        await client.patch(f"{base_url}/api/jobs/{job_id}/status", json={"status": "analyzing"}, headers=headers)
        await client.post(f"{base_url}/api/agent/analyze-brand", json={"job_id": job_id}, headers=headers)
        
        await client.patch(f"{base_url}/api/jobs/{job_id}/status", json={"status": "discovering"}, headers=headers)
        profiles = await client.post(f"{base_url}/api/agent/discover", json={"job_id": job_id}, headers=headers)
        
        await client.patch(f"{base_url}/api/jobs/{job_id}/status", json={"status": "scoring"}, headers=headers)
        for profile in profiles.json()["profiles"]:
            await client.post(f"{base_url}/api/agent/score", json={"job_id": job_id, "profile_id": profile["id"]}, headers=headers)
            await asyncio.sleep(1)
        
        await client.patch(f"{base_url}/api/jobs/{job_id}/status", json={"status": "completed"}, headers=headers)
```

## Cross-References
- `docs/Orchestration_Guide.md`
