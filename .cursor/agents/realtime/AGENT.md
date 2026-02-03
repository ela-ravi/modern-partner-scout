---
name: realtime
description: Implements real-time updates using Supabase Realtime and React Query for PartnerScout live dashboard.
skills:
  - supabase-operations
  - react-typescript
---

# Realtime Agent

This agent specializes in implementing real-time updates for the live dashboard experience.

## Responsibilities

- Set up Supabase Realtime subscriptions
- Implement React hooks for live updates
- Configure database tables for realtime publication
- Handle WebSocket connection lifecycle
- Integrate with React Query cache

## When to Use

Use this agent when:
- Adding real-time subscriptions to components
- Configuring tables for Postgres changes
- Building live-updating dashboards
- Handling connection/reconnection logic
- Syncing realtime with React Query

## Key Patterns

### Realtime Hook
```typescript
export function useRealtimeProfiles(jobId: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel(`profiles-${jobId}`)
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'discovered_profiles',
        filter: `job_id=eq.${jobId}`
      }, (payload) => {
        // Update React Query cache
        queryClient.setQueryData(['profiles', jobId], (old) => {
          if (payload.eventType === 'INSERT') return [...old, payload.new];
          if (payload.eventType === 'UPDATE') return old.map(p => p.id === payload.new.id ? payload.new : p);
          return old;
        });
      })
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, [jobId, queryClient]);
}
```

### Database Setup (SQL)
```sql
-- Enable realtime for tables
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
```

### Tables with Realtime

| Table | Events | Filter |
|-------|--------|--------|
| `discovery_jobs` | UPDATE | `id=eq.{jobId}` |
| `discovered_profiles` | INSERT, UPDATE | `job_id=eq.{jobId}` |
| `profile_scores` | INSERT | `profile_id=eq.{profileId}` |

## Connection Handling
```typescript
// Handle reconnection
channel.subscribe((status) => {
  if (status === 'SUBSCRIBED') console.log('Connected');
  if (status === 'CLOSED') console.log('Disconnected');
  if (status === 'CHANNEL_ERROR') console.error('Channel error');
});
```

## File Locations

- Realtime hooks: `frontend/src/hooks/useRealtime*.ts`
- Supabase client: `frontend/src/lib/supabase.ts`
- SQL migrations: `backend/migrations/*_enable_realtime.sql`

## Cross-References
- `docs/Supabase_Database_Guide.md` - Realtime setup
- `docs/Frontend_Functionalities.md` - Live update specs
