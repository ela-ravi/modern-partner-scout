# N8N Workflows for PartnerScout AI

This directory contains N8N workflow exports for the PartnerScout AI orchestration layer.

## Quick Start

### 1. Prerequisites

- N8N installed and running ([Installation Guide](https://docs.n8n.io/hosting/))
- FastAPI backend running on `http://localhost:8000`
- Supabase database configured

### 2. Environment Variables

Set these in N8N Settings > Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `FASTAPI_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `N8N_SERVICE_KEY` | Service key for API auth | `your-secret-key-123` |

**Important:** The `N8N_SERVICE_KEY` must match the value in your backend `.env` file.

### 3. Import Workflow

1. Open N8N dashboard
2. Go to **Workflows** > **Import from File**
3. Select `workflows/partner-discovery.json`
4. Click **Import**

### 4. Activate Workflow

1. Open the imported workflow
2. Click the **Inactive** toggle to **Active**
3. Note the webhook URL displayed

### 5. Test the Workflow

**Option A: Manual Trigger**
1. Click "Execute Workflow" in N8N
2. Watch nodes execute in sequence

**Option B: Webhook**
```bash
curl -X POST https://your-n8n-instance/webhook/start-discovery \
  -H "Content-Type: application/json" \
  -d '{"job_id": "your-job-id", "user_id": "your-user-id"}'
```

## Workflows

| File | Description |
|------|-------------|
| `partner-discovery.json` | Main discovery workflow (21 nodes) |

## Documentation

For complete documentation including all node specifications:
- **Orchestration Guide:** `../docs/Orchestration.md`
- **Agent APIs:** `../docs/Agents_Documentation.md`
- **Database Schema:** `../docs/Supabase_Database_Guide.md`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not triggering | Check webhook URL and N8N is running |
| 401 errors | Verify `N8N_SERVICE_KEY` matches backend |
| Timeout errors | Increase node timeout in settings |

## Folder Structure

```
n8n/
├── README.md                           # This file
└── workflows/
    └── partner-discovery.json          # Main workflow (to be exported)
```

---

*See `docs/Orchestration.md` Section 3 for complete N8N implementation guide.*

