# PartnerScout AI – Database Implementation Index

> Single entry point for database implementation. Canonical plan: **Jira structure** ([Database_Implementation_Jira_Plan.md](Database_Implementation_Jira_Plan.md)). Same 11 steps; migrations live in `supabase/migrations/`.

---

## Plan Documents

| Document | Purpose | When to use |
|----------|---------|-------------|
| **[Database_Implementation_Jira_Plan.md](Database_Implementation_Jira_Plan.md)** | Enterprise plan: EPIC → FEATURE → STORY → TASK → SUBTASK. Jira keys (DB-EPIC-001, DB-TASK-001, DB-SUB-001…). PRD checklist, step–task mapping. | Product/Jira tracking, sprint planning, acceptance criteria. |
| **[Database_Implementation_Step_By_Step.md](Database_Implementation_Step_By_Step.md)** | Step-by-step guide: What / Why / How / Verification per step. Beginner-friendly. | Manual execution in Supabase SQL Editor; learning the schema. |

Both describe the **same 11 steps** and schema. Order is fixed: Step 1 → Step 11 (dependencies: enums before tables, tables before indexes/triggers/RLS/realtime).

---

## Jira Hierarchy (from Jira Plan)

| Level | Description | Example |
|-------|-------------|---------|
| **EPIC** | DB-EPIC-001 PartnerScout Database Foundation | Section 10 |
| **FEATURE** | DB-FEAT-001 … 005 (Setup, Extensions, Core Schema, Performance, Security & Realtime) | |
| **STORY** | DB-STORY-001 … 005 (Project, Extensions, Tables, Performance, RLS) | |
| **TASK** | DB-TASK-001 … 011 (one per Step 1–11) | |
| **SUBTASK** | DB-SUB-001 … 051 | |

**Step–Task mapping:** Step 1 → DB-TASK-001, Step 2 → DB-TASK-002, … Step 11 → DB-TASK-011.

---

## Implementation Artifacts

| Location | Contents |
|----------|----------|
| **[supabase/README.md](../supabase/README.md)** | How to run migrations (SQL Editor or CLI), verification, step–task–migration map. |
| **supabase/migrations/** | Numbered SQL files (20260201000001 … 000010). Steps 2–11; Step 1 is manual (create Supabase project). |

---

## Schema (same in both plans and migrations)

```
auth.users (Supabase Auth)
    └── discovery_jobs (1:many, user_id FK)
            ├── brand_dna (1:1, job_id FK)
            └── discovered_profiles (1:many, job_id FK)
                    ├── profile_scores (1:1, profile_id FK)
                    └── profile_contacts (1:1, profile_id FK)
```

---

## Validation

| Document | Purpose |
|----------|---------|
| **[validations/Database_PRD_Validation_Report.md](validations/Database_PRD_Validation_Report.md)** | Confirms migrations match [Partner_Scout_AI_PRD.md](Partner_Scout_AI_PRD.md) Section 10 (tables, columns, RLS, indexes). |

PRD Validation Checklist in the Jira plan (Section “PRD Validation Checklist”) maps PRD sections to FEATURE/TASK.

---

## Phase Boundary

**Phase 1: Database only.** Backend (FastAPI), APIs, n8n, and frontend are out of scope until the database phase is confirmed complete. Next: [Backend_Implementation_Jira_Plan.md](Backend_Implementation_Jira_Plan.md).

---

*Last updated: February 2026*
