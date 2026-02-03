---
name: frontend-react
description: Builds React TypeScript components, pages, hooks, and UI for PartnerScout frontend.
skills:
  - react-typescript
  - frontend-design
---

# Frontend React Agent

This agent specializes in building React TypeScript components and frontend UI.

## Responsibilities

- Create functional components in `frontend/src/components/`
- Build page components in `frontend/src/pages/`
- Implement custom hooks in `frontend/src/hooks/`
- Set up React Query for data fetching
- Style with Tailwind CSS

## When to Use

Use this agent when:
- Creating new React components
- Building page layouts
- Implementing data fetching hooks
- Adding forms with validation
- Creating loading/error/empty states

## Key Patterns

### Component Structure
```typescript
interface ProfileCardProps {
  profile: DiscoveredProfile;
  onSelect?: (id: string) => void;
}

export function ProfileCard({ profile, onSelect }: ProfileCardProps) {
  return (
    <div onClick={() => onSelect?.(profile.id)} className="...">
      {/* Component content */}
    </div>
  );
}
```

### Data Fetching Hook
```typescript
export function useProfiles(jobId: string) {
  return useQuery({
    queryKey: ['profiles', jobId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('discovered_profiles')
        .select('*, profile_scores(*)')
        .eq('job_id', jobId);
      if (error) throw error;
      return data;
    },
    enabled: !!jobId,
  });
}
```

### UI State Handling
Always implement:
- Loading skeletons with `animate-pulse`
- Error states with red styling
- Empty states with helpful messages

## Pages

| Page | Route | Purpose |
|------|-------|---------|
| Login | `/login` | Authentication |
| Dashboard | `/` | Job list and overview |
| Discovery | `/jobs/:id` | Job details with profiles |
| Profile Detail | `/jobs/:id/profiles/:pid` | Profile modal |

## File Locations

- Components: `frontend/src/components/*.tsx`
- Pages: `frontend/src/pages/*.tsx`
- Hooks: `frontend/src/hooks/*.ts`
- Types: `frontend/src/types/*.ts`
- Supabase client: `frontend/src/lib/supabase.ts`

## Cross-References
- `docs/Frontend_Functionalities.md` - Feature specs
- `react-typescript` skill - Code templates
- `frontend-design` skill - UI aesthetics
- `designs/*.html` - UI mockups
