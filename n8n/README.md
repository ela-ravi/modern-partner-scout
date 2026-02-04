# N8N Workflows for PartnerScout AI

This directory contains N8N workflow exports and setup for the PartnerScout AI orchestration layer.

**STORY-4.1.1: Setup N8N Environment**

---

## Quick Start

### Option A: Docker (Recommended)

1. **Configure environment** (from project root):
   ```bash
   cp n8n/.env.example .env.n8n
   # Edit .env.n8n: set FASTAPI_BASE_URL and N8N_SERVICE_KEY
   ```

2. **Start N8N**:
   ```bash
   docker compose -f docker-compose.n8n.yml --env-file .env.n8n up -d
   ```

3. **Validate**: Open http://localhost:5678

### Option B: npm (Local)

1. **Install N8N**:
   ```bash
   npm install -g n8n
   ```

2. **Set environment variables** (before starting):
   ```bash
   export FASTAPI_BASE_URL=http://localhost:8000
   export N8N_SERVICE_KEY=your-service-key  # Must match backend .env
   ```

3. **Start N8N**:
   ```bash
   n8n start
   ```

4. **Validate**: Open http://localhost:5678

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FASTAPI_BASE_URL` | Backend API base URL (no trailing slash) | `http://localhost:8000` or `http://host.docker.internal:8000` |
| `N8N_SERVICE_KEY` | Service key for API auth - **must match backend** | `test-service-key-12345` |

**Important:** `N8N_SERVICE_KEY` must match `N8N_SERVICE_KEY` in `backend/.env`. The backend validates this key for status update and agent API calls from N8N.

---

## Validation

### 1. Access N8N UI

```
http://localhost:5678
```

Expected: N8N dashboard loads, no errors.

### 2. Verify Configuration (N8N UI)

1. Open N8N → **Settings** → **Variables**
2. Ensure `FASTAPI_BASE_URL` and `N8N_SERVICE_KEY` are set (or use env vars passed to container)

### 3. Verify Backend Connectivity

Run the verification script from project root:

```bash
cd backend
python -m scripts.verify_n8n
```

Expected: `N8N is running and accessible at http://localhost:5678`

---

## Import Workflow

1. Open N8N dashboard
2. Go to **Workflows** → **Import from File**
3. Select `workflows/partner-discovery.json`
4. Click **Import**
5. Activate the workflow (toggle **Inactive** → **Active**)

## Partner Discovery Workflow (STORY-4.1.2)

- The exported workflow lives at `workflows/partner-discovery.json` and contains 21 nodes that mirror the orchestration described in `docs/Orchestration.md`.
- Trigger the workflow via the `Webhook Trigger` (`/start-discovery`) from the frontend or use the `Manual Trigger` with sample payloads for local testing.
- Every HTTP Request node relies on `FASTAPI_BASE_URL` and `N8N_SERVICE_KEY`; confirm both variables are present in N8N **Settings → Variables** before executing.
- The workflow automatically handles status transitions, discovery/scoring loops, completion, and error recovery updates against the FastAPI backend.

---

## Folder Structure

```
n8n/
├── README.md              # This file
├── .env.example           # Environment template for Docker
└── workflows/
    ├── .gitkeep
    └── partner-discovery.json   # Main workflow (exported from N8N)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot access http://localhost:5678 | Ensure Docker container is running: `docker ps` |
| 401 from FastAPI | Verify `N8N_SERVICE_KEY` matches in backend `.env` |
| Connection refused to FastAPI | Use `host.docker.internal:8000` (Docker on Windows/Mac) |
| Workflow not triggering | Check webhook URL, ensure workflow is **Active** |

---

## Testing

Run N8N-related tests from the backend:

```bash
cd backend

# Unit tests (always run)
python -m pytest tests/test_n8n_setup.py -v -m "unit"

# Integration test (requires N8N running - skips if not)
python -m pytest tests/test_n8n_setup.py -v -m "n8n"

# Workflow validation tests (STORY-4.1.2)
python -m pytest tests/test_n8n_workflow.py -v
```

---

## Documentation

- **Orchestration Guide:** `../docs/Orchestration.md`
- **Agent APIs:** `../docs/Agents_Documentation.md`
- **Database Schema:** `../docs/Supabase_Database_Guide.md`
