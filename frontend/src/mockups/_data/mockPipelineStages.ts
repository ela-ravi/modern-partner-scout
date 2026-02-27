import type { PipelineStage } from '@/components/features/PipelineProgress'

export const MOCK_PIPELINE_STAGES: PipelineStage[] = [
  {
    id: 'analyzer',
    name: 'Brand Analyzer',
    status: 'completed',
    description: 'Extracting brand DNA from reference profiles',
  },
  {
    id: 'discovery',
    name: 'Discovery Engine',
    status: 'completed',
    description: 'Scanning Instagram for matching profiles',
    stats: { discovered: 35 },
  },
  {
    id: 'scoring',
    name: 'Scoring Agent',
    status: 'active',
    description: 'Analyzing profiles against brand DNA',
    progress: 63,
    stats: { scored: 22 },
  },
  {
    id: 'email',
    name: 'Email Extractor',
    status: 'active',
    description: 'Extracting contact emails from scored profiles',
    progress: 20,
    stats: { emails: 8 },
  },
]
