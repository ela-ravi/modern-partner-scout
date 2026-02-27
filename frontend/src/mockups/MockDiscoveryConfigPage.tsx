import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Card } from '@/components/ui/Card'
import { Stepper, type Step } from '@/components/ui/Stepper'
import { FollowerPresets } from '@/components/composite/FollowerPresets'
import { MockDashboardLayout } from './MockDashboardLayout'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import EditIcon from '@mui/icons-material/Edit'
import InfoIcon from '@mui/icons-material/Info'
import AccessTimeIcon from '@mui/icons-material/AccessTime'

// Pre-filled mock form data
const mockFormData = {
  name: 'Summer 2026 Skincare Campaign',
  brandDescription: 'Premium organic skincare brand targeting Gen Z and millennials who value clean beauty, sustainability, and minimalist aesthetics.',
  referenceProfiles: [
    'https://instagram.com/glossier',
    'https://instagram.com/tatcha',
    'https://instagram.com/drunk_elephant',
  ],
  keywords: ['skincare', 'clean beauty', 'organic', 'glow', 'self-care'],
  hashtags: ['#skincare', '#cleanbeauty', '#glowup', '#selfcare', '#organicbeauty'],
  discoveryLimit: 50,
  minScoreThreshold: 60,
  targetCountry: 'United States',
  minFollowers: 10000,
  maxFollowers: 500000,
}

export default function MockDiscoveryConfigPage() {
  const [step, setStep] = useState<'config' | 'review'>('config')

  const steps: Step[] = [
    { label: 'Configure', status: step === 'config' ? 'active' : 'complete' },
    { label: 'Launch', status: step === 'review' ? 'active' : 'upcoming' },
  ]

  // Config Step
  if (step === 'config') {
    return (
      <MockDashboardLayout activePath="/mockups/discovery-config">
        <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
          <Stepper steps={steps} hideLabelsOnMobile className="mb-8" />

          <div>
            <h1 className="text-2xl font-bold text-apple-text">New Discovery Session</h1>
            <p className="text-apple-text-secondary mt-1">Configure your partner discovery campaign</p>
          </div>

          <form onSubmit={(e) => { e.preventDefault(); setStep('review') }} className="space-y-6">
            {/* Basic Information */}
            <Card>
              <h2 className="text-lg font-semibold text-apple-text mb-4">Basic Information</h2>
              <div className="space-y-4">
                <Input
                  label="Campaign Name"
                  placeholder="e.g., Summer 2026 Influencer Campaign"
                  defaultValue={mockFormData.name}
                  required
                />
                <Textarea
                  label="Brand Description"
                  placeholder="Describe your brand, products, and target audience..."
                  defaultValue={mockFormData.brandDescription}
                  helperText="This helps our AI find better matches"
                  maxLength={500}
                />
              </div>
            </Card>

            {/* Reference Profiles */}
            <Card>
              <h2 className="text-lg font-semibold text-apple-text mb-4">Reference Profiles</h2>
              <p className="text-sm text-apple-text-secondary mb-4">
                Add 2-10 Instagram profiles that represent your ideal partners
              </p>

              <div className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="https://instagram.com/username"
                    className="flex-1"
                  />
                  <Button type="button" variant="secondary">Add</Button>
                </div>

                <div className="space-y-2">
                  {mockFormData.referenceProfiles.map((url) => (
                    <div key={url} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-apple-text truncate flex-1">{url}</span>
                      <button type="button" className="text-apple-text-tertiary hover:text-apple-red ml-2" aria-label={`Remove ${url}`}>
                        x
                      </button>
                    </div>
                  ))}
                </div>

                <p className="text-xs text-apple-text-tertiary">
                  {mockFormData.referenceProfiles.length}/10 profiles added
                </p>
              </div>
            </Card>

            {/* Discovery Terms */}
            <Card>
              <h2 className="text-lg font-semibold text-apple-text mb-4">Discovery Terms</h2>
              <div className="space-y-4">
                <div>
                  <span className="block text-sm font-medium text-apple-text mb-1">Keywords</span>
                  <div className="flex flex-wrap gap-2 p-3 border border-apple-border rounded-xl min-h-[44px]">
                    {mockFormData.keywords.map((kw) => (
                      <span key={kw} className="inline-flex items-center gap-1 px-2.5 py-1 bg-gray-100 rounded-md text-sm text-apple-text">
                        {kw}
                        <button type="button" className="text-apple-text-tertiary hover:text-apple-red text-xs">x</button>
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-apple-text-tertiary mt-1">Topics and themes related to your brand</p>
                </div>

                <div>
                  <span className="block text-sm font-medium text-apple-text mb-1">Hashtags</span>
                  <div className="flex flex-wrap gap-2 p-3 border border-apple-border rounded-xl min-h-[44px]">
                    {mockFormData.hashtags.map((tag) => (
                      <span key={tag} className="inline-flex items-center gap-1 px-2.5 py-1 bg-apple-blue/10 text-apple-blue rounded-md text-sm">
                        {tag}
                        <button type="button" className="text-apple-blue/60 hover:text-apple-red text-xs">x</button>
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-apple-text-tertiary mt-1">Hashtags your ideal partners use</p>
                </div>
              </div>
            </Card>

            {/* Discovery Settings */}
            <Card>
              <h2 className="text-lg font-semibold text-apple-text mb-4">Discovery Settings</h2>
              <div className="space-y-6">
                {/* Discovery Limit (static slider representation) */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-apple-text">Discovery Limit</span>
                    <span className="text-sm font-semibold text-apple-blue">{mockFormData.discoveryLimit}</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-apple-blue rounded-full" style={{ width: `${(mockFormData.discoveryLimit / 100) * 100}%` }} />
                  </div>
                  <p className="text-xs text-apple-text-tertiary mt-1">Maximum number of profiles to discover</p>
                </div>

                {/* Min Score (static slider representation) */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-apple-text">Minimum Score Threshold</span>
                    <span className="text-sm font-semibold text-apple-blue">{mockFormData.minScoreThreshold}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-apple-blue rounded-full" style={{ width: `${mockFormData.minScoreThreshold}%` }} />
                  </div>
                  <p className="text-xs text-apple-text-tertiary mt-1">Only show profiles scoring above this value</p>
                </div>

                <Input
                  label="Target Country / Region"
                  defaultValue={mockFormData.targetCountry}
                  placeholder="e.g., India, USA, Germany"
                  helperText="Optional — profiles from this region get priority in scoring"
                />

                {/* Follower Presets */}
                <div className="space-y-3">
                  <span className="block text-sm font-medium text-apple-text">Follower Range</span>
                  <FollowerPresets
                    onSelect={() => {}}
                    activePreset="mid-tier"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Input type="number" label="Min Followers" defaultValue={mockFormData.minFollowers} />
                  <Input type="number" label="Max Followers" defaultValue={mockFormData.maxFollowers} />
                </div>
              </div>
            </Card>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <Link to="/mockups/sessions">
                <Button type="button" variant="secondary">Cancel</Button>
              </Link>
              <Button type="submit" rightIcon={<ArrowForwardIcon />}>
                Review & Launch
              </Button>
            </div>
          </form>
        </div>
      </MockDashboardLayout>
    )
  }

  // Review Step
  return (
    <MockDashboardLayout activePath="/mockups/discovery-config">
      <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
        <Stepper steps={steps} hideLabelsOnMobile className="mb-8" />

        <div>
          <h1 className="text-2xl font-bold text-apple-text">Review Configuration</h1>
          <p className="text-apple-text-secondary mt-1">Verify your settings before launching the discovery</p>
        </div>

        {/* Estimated Time */}
        <div className="flex items-center gap-2 text-apple-text-secondary">
          <AccessTimeIcon className="w-5 h-5" />
          <span className="text-sm font-medium">Estimated Time: ~3-5 minutes</span>
        </div>

        {/* Info Note */}
        <div className="flex items-start gap-3 p-4 bg-apple-blue/5 border border-apple-blue/20 rounded-xl" role="note">
          <InfoIcon className="w-5 h-5 text-apple-blue flex-shrink-0 mt-0.5" />
          <p className="text-sm text-apple-text-secondary">
            Once launched, you&apos;ll see profiles appear in real-time as our AI discovers and scores them. You can pause or cancel the discovery at any time from the dashboard.
          </p>
        </div>

        {/* Basic Info Card */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-apple-text">Basic Information</h2>
            <Button variant="ghost" size="sm" leftIcon={<EditIcon />} onClick={() => setStep('config')}>Edit</Button>
          </div>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm text-apple-text-secondary">Campaign Name</dt>
              <dd className="text-apple-text font-medium">{mockFormData.name}</dd>
            </div>
            <div>
              <dt className="text-sm text-apple-text-secondary">Brand Description</dt>
              <dd className="text-apple-text">{mockFormData.brandDescription}</dd>
            </div>
          </dl>
        </Card>

        {/* Reference Profiles Card */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-apple-text">Reference Profiles</h2>
            <Button variant="ghost" size="sm" leftIcon={<EditIcon />} onClick={() => setStep('config')}>Edit</Button>
          </div>
          <ul className="space-y-1">
            {mockFormData.referenceProfiles.map((url) => (
              <li key={url} className="text-sm text-apple-text truncate">{url}</li>
            ))}
          </ul>
        </Card>

        {/* Discovery Terms Card */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-apple-text">Discovery Terms</h2>
            <Button variant="ghost" size="sm" leftIcon={<EditIcon />} onClick={() => setStep('config')}>Edit</Button>
          </div>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm text-apple-text-secondary">Keywords</dt>
              <dd className="flex flex-wrap gap-2 mt-1">
                {mockFormData.keywords.map((kw) => (
                  <span key={kw} className="px-2 py-0.5 bg-gray-100 rounded text-sm">{kw}</span>
                ))}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-apple-text-secondary">Hashtags</dt>
              <dd className="flex flex-wrap gap-2 mt-1">
                {mockFormData.hashtags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 bg-apple-blue/10 text-apple-blue rounded text-sm">{tag}</span>
                ))}
              </dd>
            </div>
          </dl>
        </Card>

        {/* Settings Card */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-apple-text">Discovery Settings</h2>
            <Button variant="ghost" size="sm" leftIcon={<EditIcon />} onClick={() => setStep('config')}>Edit</Button>
          </div>
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-apple-text-secondary">Discovery Limit</dt>
              <dd className="text-apple-text font-medium">{mockFormData.discoveryLimit} profiles</dd>
            </div>
            <div>
              <dt className="text-sm text-apple-text-secondary">Min Score</dt>
              <dd className="text-apple-text font-medium">{mockFormData.minScoreThreshold}%</dd>
            </div>
            <div>
              <dt className="text-sm text-apple-text-secondary">Follower Range</dt>
              <dd className="text-apple-text font-medium">
                {mockFormData.minFollowers.toLocaleString()} - {mockFormData.maxFollowers.toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-apple-text-secondary">Target Country</dt>
              <dd className="text-apple-text font-medium">{mockFormData.targetCountry}</dd>
            </div>
          </dl>
        </Card>

        {/* Actions */}
        <div className="flex justify-between">
          <Button type="button" variant="secondary" leftIcon={<ArrowBackIcon />} onClick={() => setStep('config')}>
            Back to Edit
          </Button>
          <Link to="/mockups/processing">
            <Button leftIcon={<RocketLaunchIcon />}>Launch Discovery</Button>
          </Link>
        </div>
      </div>
    </MockDashboardLayout>
  )
}
