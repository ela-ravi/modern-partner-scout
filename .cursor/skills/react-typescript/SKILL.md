---
name: react-typescript
description: Build React/TypeScript frontend components with proper patterns. Use this skill when implementing React components, custom hooks, React Query, state management, or Tailwind styling for the PartnerScout dashboard.
---

This skill guides React/TypeScript frontend development for PartnerScout, including component patterns, hooks, and React Query usage.

## Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── ProfileCard.tsx
│   ├── ScoreBadge.tsx
│   ├── ProgressBar.tsx
│   └── ui/              # Base UI components
├── pages/               # Route pages
│   ├── Dashboard.tsx
│   ├── SessionList.tsx
│   └── Login.tsx
├── hooks/               # Custom React hooks
│   ├── useJobs.ts
│   ├── useProfiles.ts
│   └── useRealtimeProfiles.ts
├── services/            # API client functions
│   └── api.ts
├── types/               # TypeScript definitions
│   └── database.types.ts
├── lib/                 # Utilities
│   └── supabase.ts
└── App.tsx
```

## Component Patterns

### Functional Component with Props

```tsx
// components/ProfileCard.tsx
import { DiscoveredProfile, ProfileScore } from '../types/database.types'

interface ProfileCardProps {
  profile: DiscoveredProfile
  score?: ProfileScore | null
  onSelect?: (profile: DiscoveredProfile) => void
}

export function ProfileCard({ profile, score, onSelect }: ProfileCardProps) {
  return (
    <div 
      className="bg-white rounded-lg shadow-md p-4 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onSelect?.(profile)}
    >
      <div className="flex items-center gap-3">
        <img 
          src={profile.profile_picture_url || '/default-avatar.png'} 
          alt={profile.username}
          className="w-12 h-12 rounded-full object-cover"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">@{profile.username}</h3>
          <p className="text-sm text-gray-500">{profile.full_name}</p>
        </div>
        {score && <ScoreBadge score={score.score} />}
      </div>
      
      <p className="mt-2 text-sm text-gray-600 line-clamp-2">{profile.bio}</p>
      
      <div className="mt-3 flex gap-4 text-sm text-gray-500">
        <span>{profile.followers.toLocaleString()} followers</span>
        <span>{profile.engagement_rate?.toFixed(1)}% engagement</span>
      </div>
    </div>
  )
}
```

### Score Badge Component

```tsx
// components/ScoreBadge.tsx
interface ScoreBadgeProps {
  score: number
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const getColorClass = (score: number) => {
    if (score >= 85) return 'bg-green-500'
    if (score >= 70) return 'bg-blue-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className={`${getColorClass(score)} text-white text-sm font-bold px-2 py-1 rounded`}>
      {score}
    </div>
  )
}
```

## Custom Hooks

### Data Fetching Hook with React Query

```tsx
// hooks/useJobs.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'
import type { DiscoveryJob } from '../types/database.types'

export function useJobs() {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: async (): Promise<DiscoveryJob[]> => {
      const { data, error } = await supabase
        .from('discovery_jobs')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    }
  })
}

export function useJob(jobId: string) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('discovery_jobs')
        .select(`
          *,
          brand_dna (*),
          discovered_profiles (
            *,
            profile_scores (*),
            profile_contacts (*)
          )
        `)
        .eq('id', jobId)
        .single()
      
      if (error) throw error
      return data
    },
    enabled: !!jobId
  })
}

export function useCreateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (input: { brand_description: string; reference_profiles: string[] }) => {
      const { data, error } = await supabase
        .from('discovery_jobs')
        .insert(input)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    }
  })
}
```

### Realtime Subscription Hook

```tsx
// hooks/useRealtimeProfiles.ts
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { DiscoveredProfile } from '../types/database.types'

export function useRealtimeProfiles(jobId: string) {
  const [profiles, setProfiles] = useState<DiscoveredProfile[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!jobId) return

    // Initial fetch
    const fetchProfiles = async () => {
      const { data } = await supabase
        .from('discovered_profiles')
        .select('*, profile_scores(*), profile_contacts(*)')
        .eq('job_id', jobId)
        .order('created_at', { ascending: false })
      
      if (data) setProfiles(data)
      setLoading(false)
    }
    fetchProfiles()

    // Subscribe to realtime changes
    const channel = supabase
      .channel(`profiles-${jobId}`)
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'discovered_profiles',
        filter: `job_id=eq.${jobId}`
      }, (payload) => {
        setProfiles(prev => [payload.new as DiscoveredProfile, ...prev])
      })
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'discovered_profiles',
        filter: `job_id=eq.${jobId}`
      }, (payload) => {
        setProfiles(prev => prev.map(p => 
          p.id === payload.new.id ? { ...p, ...payload.new } : p
        ))
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [jobId])

  return { profiles, loading }
}
```

## Page Components

### Dashboard Page

```tsx
// pages/Dashboard.tsx
import { useState } from 'react'
import { useJob } from '../hooks/useJobs'
import { useRealtimeProfiles } from '../hooks/useRealtimeProfiles'
import { ProfileCard } from '../components/ProfileCard'
import { ProfileDetailModal } from '../components/ProfileDetailModal'
import type { DiscoveredProfile } from '../types/database.types'

type TabType = 'new' | 'processing' | 'done'

export function Dashboard({ jobId }: { jobId: string }) {
  const { data: job, isLoading: jobLoading } = useJob(jobId)
  const { profiles, loading: profilesLoading } = useRealtimeProfiles(jobId)
  const [activeTab, setActiveTab] = useState<TabType>('done')
  const [selectedProfile, setSelectedProfile] = useState<DiscoveredProfile | null>(null)

  const filteredProfiles = profiles.filter(p => p.status === activeTab)

  if (jobLoading || profilesLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Progress Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{job?.name || 'Discovery Session'}</h1>
        <p className="text-gray-600">
          Discovered: {job?.profiles_discovered} | Scored: {job?.profiles_scored}
        </p>
        <StatusBadge status={job?.status} />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(['new', 'processing', 'done'] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === tab 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tab.toUpperCase()} ({profiles.filter(p => p.status === tab).length})
          </button>
        ))}
      </div>

      {/* Profile Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredProfiles.map(profile => (
          <ProfileCard
            key={profile.id}
            profile={profile}
            score={profile.profile_scores?.[0]}
            onSelect={setSelectedProfile}
          />
        ))}
      </div>

      {/* Detail Modal */}
      {selectedProfile && (
        <ProfileDetailModal
          profile={selectedProfile}
          onClose={() => setSelectedProfile(null)}
        />
      )}
    </div>
  )
}
```

## Loading States

### Skeleton Loader

```tsx
// components/ProfileCardSkeleton.tsx
export function ProfileCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-gray-200 rounded-full" />
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
          <div className="h-3 bg-gray-200 rounded w-32" />
        </div>
      </div>
      <div className="mt-3 h-12 bg-gray-200 rounded" />
    </div>
  )
}
```

## Form Handling

```tsx
// components/CreateSessionForm.tsx
import { useState } from 'react'
import { useCreateJob } from '../hooks/useJobs'

export function CreateSessionForm({ onSuccess }: { onSuccess: () => void }) {
  const [description, setDescription] = useState('')
  const [profiles, setProfiles] = useState<string[]>(['', ''])
  const createJob = useCreateJob()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validProfiles = profiles.filter(p => p.trim())
    if (validProfiles.length < 2) {
      alert('Please add at least 2 reference profiles')
      return
    }

    try {
      await createJob.mutateAsync({
        brand_description: description,
        reference_profiles: validProfiles
      })
      onSuccess()
    } catch (error) {
      console.error('Failed to create job:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Brand Description
        </label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          required
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Reference Profiles (2-10)
        </label>
        {profiles.map((profile, i) => (
          <input
            key={i}
            type="url"
            value={profile}
            onChange={e => {
              const newProfiles = [...profiles]
              newProfiles[i] = e.target.value
              setProfiles(newProfiles)
            }}
            placeholder="https://instagram.com/username"
            className="mt-2 block w-full rounded-md border-gray-300 shadow-sm"
          />
        ))}
        <button
          type="button"
          onClick={() => setProfiles([...profiles, ''])}
          className="mt-2 text-sm text-blue-600 hover:underline"
        >
          + Add another profile
        </button>
      </div>

      <button
        type="submit"
        disabled={createJob.isPending}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {createJob.isPending ? 'Creating...' : 'Create Session'}
      </button>
    </form>
  )
}
```

## Error Handling

```tsx
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">
          Something went wrong. Please refresh the page.
        </div>
      )
    }
    return this.props.children
  }
}
```

## Dependencies

```json
{
  "@tanstack/react-query": "^5.0.0",
  "@supabase/supabase-js": "^2.0.0",
  "react-router-dom": "^6.0.0"
}
```

## Best Practices

1. **Strict TypeScript**: Never use `any` type
2. **Interface over type**: Use interfaces for object shapes
3. **Destructure props**: In function parameters
4. **React Query**: For all server state
5. **Supabase Realtime**: For live updates
6. **Tailwind CSS**: For all styling
7. **Loading states**: Show skeletons, not spinners
8. **Error boundaries**: Wrap major sections
