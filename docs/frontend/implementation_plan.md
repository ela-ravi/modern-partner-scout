# Implementation Plan: Documentation & Code Alignment Fixes

This plan addresses the gaps identified in the [Cross-Documentation Alignment Report](cross_docs_alignment.md). Key fixes include adding missing fields (`cover_image_url`, `recent_posts`), persisting scored content, and unifying the 6-dimension scoring system across the stack.

## Proposed Changes

### 1. Documentation Phase (Harmonization) [COMPLETED]
Update existing docs to match the finalized technical spec.

#### [MODIFY] [Supabase_Database_Guide.md](../Supabase_Database_Guide.md) [COMPLETED]
- Update `discovered_profiles` table definition to include `cover_image_url` (text) and `recent_posts` (jsonb).
- Update ERD/Schema descriptions.

#### [MODIFY] [Backend_Implementation_Guide.md](../Backend_Implementation_Guide.md) [COMPLETED]
- Update `Profile` and `CompleteProfile` model descriptions.
- Reference the 6-dimension scoring model consistently.

---

### 2. Database Phase [COMPLETED]
Apply structural changes to Supabase.

#### [NEW] `supabase/migrations/20260207_add_cover_and_posts_to_profiles.sql` [COMPLETED]
- `ALTER TABLE discovered_profiles ADD COLUMN cover_image_url TEXT;`
- `ALTER TABLE discovered_profiles ADD COLUMN recent_posts JSONB DEFAULT '[]'::jsonb;`
- Refresh `v_complete_profiles` view to include these new columns.

---

### 3. Backend Phase [COMPLETED]
Update FastAPI models and agent logic.

#### [MODIFY] [profile.py](../../backend/app/models/profile.py) [COMPLETED]
- Add `cover_image_url` and `recent_posts` to `ProfileBase` and `CompleteProfile`.

#### [MODIFY] [profile_repo.py](../../backend/app/repositories/profile_repo.py) [COMPLETED]
- Ensure CRUD operations handle the new fields.

#### [MODIFY] [scorer.py](../../backend/app/agents/scorer.py) [COMPLETED]
- Update the scoring logic to extract `recent_posts` from Apify and save them to the database during the scoring phase.

---

### 4. Frontend Phase [COMPLETED]
Update React components and TypeScript types.

#### [MODIFY] [index.ts](../../frontend/src/types/index.ts) [COMPLETED]
- Update `DiscoveredProfile` and `CompleteProfile` interfaces with `cover_image_url` and `recent_posts`.

#### [MODIFY] [ProfileCard.tsx](../../frontend/src/components/dashboard/ProfileCard.tsx) [COMPLETED]
- Use `cover_image_url` as the background or top image of the profile card.

#### [MODIFY] [ProfileDetailModal.tsx](../../frontend/src/components/dashboard/ProfileDetailModal.tsx) [COMPLETED]
- Render all 6 scoring dimensions (Visual, Content, Engagement, Quality, Business, Recency).
- Display the list of `recent_posts` (thumbnails + captions) saved in the database.

---

## Verification Plan

### Automated Tests
- **Backend**:
  - `pytest backend/tests/test_models.py` - Verify Pydantic validation.
  - `pytest backend/tests/test_repositories.py` - Verify DB persistence.
- **Frontend**:
  - Browser script to verify that `cover_image_url` and `recent_posts` are rendered in the DOM.

### Manual Verification
- **SQL Check**: Run `\d discovered_profiles` in Supabase SQL editor to verify columns.
- **API Check**: Use Swagger (`/docs`) to verify that the `GET /api/jobs/{id}` response includes the new fields.
- **UI Check**: Open the dashboard, click on a profile, and verify the modal displays posts and 6 dimensions.
