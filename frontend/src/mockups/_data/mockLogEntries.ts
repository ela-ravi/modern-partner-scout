import type { LogEntry } from '@/components/composite/ActivityLog'

export const MOCK_LOG_ENTRIES: LogEntry[] = [
  { id: 'log-01', timestamp: '14:32:10', type: 'info', message: 'Pipeline started for "Fitness Brand Collab Q3"' },
  { id: 'log-02', timestamp: '14:32:12', type: 'info', message: 'Brand analysis started...' },
  { id: 'log-03', timestamp: '14:33:45', type: 'success', message: 'Brand DNA extracted: 8 hashtags, 12 keywords' },
  { id: 'log-04', timestamp: '14:33:48', type: 'info', message: 'Profile discovery started...' },
  { id: 'log-05', timestamp: '14:34:22', type: 'success', message: 'Discovered @fitnesswithkate (85.2K followers)' },
  { id: 'log-06', timestamp: '14:34:45', type: 'success', message: 'Discovered @crossfitjake (42.1K followers)' },
  { id: 'log-07', timestamp: '14:35:10', type: 'success', message: 'Discovered @hiitqueen (156.8K followers)' },
  { id: 'log-08', timestamp: '14:35:38', type: 'warning', message: 'Skipped @botaccount123 (fake detection: ratio 4.2)' },
  { id: 'log-09', timestamp: '14:36:02', type: 'success', message: 'Discovered @yogaandstrength (33.5K followers)' },
  { id: 'log-10', timestamp: '14:36:30', type: 'info', message: 'Profile scoring started...' },
  { id: 'log-11', timestamp: '14:37:15', type: 'success', message: 'Profile scored', score: 87 },
  { id: 'log-12', timestamp: '14:37:48', type: 'success', message: 'Profile scored', score: 72 },
  { id: 'log-13', timestamp: '14:38:20', type: 'success', message: 'Profile scored', score: 91 },
  { id: 'log-14', timestamp: '14:38:55', type: 'warning', message: 'Low score profile filtered (score: 28)' },
  { id: 'log-15', timestamp: '14:39:10', type: 'info', message: '22 of 30 profiles scored • Email extraction in progress...' },
]
