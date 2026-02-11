import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { TagInput } from '@/components/ui/TagInput'
import { Slider } from '@/components/ui/Slider'
import { Card } from '@/components/ui/Card'
import { Stepper, type Step } from '@/components/ui/Stepper'
import { FollowerPresets, getActivePreset } from '@/components/composite/FollowerPresets'
import { useCreateJob } from '@/hooks/jobs'
import { jobsService } from '@/services/jobs'
import { useToast } from '@/components/ui/Toast'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import EditIcon from '@mui/icons-material/Edit'
import InfoIcon from '@mui/icons-material/Info'
import AccessTimeIcon from '@mui/icons-material/AccessTime'

// Validation schema
const discoveryConfigSchema = z.object({
  name: z.string().min(1, 'Campaign name is required').max(100, 'Name too long'),
  brandDescription: z.string().max(500, 'Description too long').optional(),
  referenceProfiles: z
    .array(z.string().url('Enter valid Instagram URLs'))
    .min(2, 'At least 2 reference profiles required')
    .max(10, 'Maximum 10 reference profiles'),
  keywords: z.array(z.string()).optional(),
  hashtags: z.array(z.string().regex(/^#/, 'Hashtags must start with #')).optional(),
  discoveryLimit: z.number().min(10).max(100),
  minScoreThreshold: z.number().min(0).max(100),
  targetCountry: z.string().max(100).optional(),
  minFollowers: z.number().min(0).optional(),
  maxFollowers: z.number().min(0).optional(),
})

type DiscoveryConfigFormData = z.infer<typeof discoveryConfigSchema>

const defaultValues: DiscoveryConfigFormData = {
  name: '',
  brandDescription: '',
  referenceProfiles: [],
  keywords: [],
  hashtags: [],
  discoveryLimit: 50,
  minScoreThreshold: 60,
  targetCountry: '',
  minFollowers: 1000,
  maxFollowers: 500000,
}

export default function DiscoveryConfigPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const createJob = useCreateJob()
  const [step, setStep] = useState<'config' | 'review'>('config')
  const [profileInput, setProfileInput] = useState('')

  const form = useForm<DiscoveryConfigFormData>({
    resolver: zodResolver(discoveryConfigSchema),
    defaultValues,
    mode: 'onChange',
  })

  const { control, handleSubmit, watch, formState: { errors, isValid }, setValue, getValues } = form
  const watchedValues = watch()

  // Calculate active preset based on current follower range values
  const activePreset = useMemo(
    () => getActivePreset(watchedValues.minFollowers || 0, watchedValues.maxFollowers || 0),
    [watchedValues.minFollowers, watchedValues.maxFollowers]
  )

  // Handle preset selection
  const handlePresetSelect = (min: number, max: number) => {
    setValue('minFollowers', min, { shouldValidate: true })
    setValue('maxFollowers', max, { shouldValidate: true })
  }

  // Stepper steps based on current step
  const steps: Step[] = useMemo(() => [
    { 
      label: 'Configure', 
      status: step === 'config' ? 'active' : 'complete' 
    },
    { 
      label: 'Launch', 
      status: step === 'review' ? 'active' : 'upcoming' 
    },
  ], [step])

  // Handle adding reference profile
  const handleAddProfile = () => {
    const trimmed = profileInput.trim()
    if (!trimmed) return

    // Basic URL validation
    try {
      new URL(trimmed)
      const current = getValues('referenceProfiles')
      if (current.length < 10 && !current.includes(trimmed)) {
        setValue('referenceProfiles', [...current, trimmed], { shouldValidate: true })
        setProfileInput('')
      }
    } catch {
      toast.error('Please enter a valid URL')
    }
  }

  const handleRemoveProfile = (index: number) => {
    const current = getValues('referenceProfiles')
    setValue(
      'referenceProfiles',
      current.filter((_, i) => i !== index),
      { shouldValidate: true }
    )
  }

  const handleLaunch = async (data: DiscoveryConfigFormData) => {
    try {
      const result = await createJob.mutateAsync({
        name: data.name,
        brand_description: data.brandDescription || data.name,
        reference_profiles: data.referenceProfiles,
        follower_range_min: data.minFollowers,
        follower_range_max: data.maxFollowers,
        discovery_limit: data.discoveryLimit,
        keywords: data.keywords,
        hashtags: data.hashtags,
        min_score_threshold: data.minScoreThreshold,
        ...(data.targetCountry ? { target_country: data.targetCountry } : {}),
      })

      // Start the orchestration pipeline
      try {
        await jobsService.start(result.id)
      } catch (startError) {
        console.warn('Job start returned error (may still be running):', startError)
      }

      toast.success('Discovery session launched!')
      navigate(`/jobs/${result.id}/processing`)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create session')
    }
  }

  // Config Step
  if (step === 'config') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Stepper */}
        <Stepper steps={steps} hideLabelsOnMobile className="mb-8" />

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-apple-text">New Discovery Session</h1>
          <p className="text-apple-text-secondary mt-1">
            Configure your partner discovery campaign
          </p>
        </div>

        <form onSubmit={handleSubmit(() => setStep('review'))} className="space-y-6">
          {/* Campaign Name */}
          <Card>
            <h2 className="text-lg font-semibold text-apple-text mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Campaign Name"
                    placeholder="e.g., Summer 2026 Influencer Campaign"
                    error={errors.name?.message}
                    required
                  />
                )}
              />

              <Controller
                name="brandDescription"
                control={control}
                render={({ field }) => (
                  <Textarea
                    {...field}
                    label="Brand Description"
                    placeholder="Describe your brand, products, and target audience..."
                    helperText="This helps our AI find better matches"
                    maxLength={500}
                  />
                )}
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
                  value={profileInput}
                  onChange={(e) => setProfileInput(e.target.value)}
                  placeholder="https://instagram.com/username"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAddProfile()
                    }
                  }}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddProfile}
                  disabled={!profileInput.trim()}
                >
                  Add
                </Button>
              </div>

              {/* Profile list */}
              {watchedValues.referenceProfiles.length > 0 && (
                <div className="space-y-2">
                  {watchedValues.referenceProfiles.map((url, index) => (
                    <div
                      key={url}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="text-sm text-apple-text truncate flex-1">
                        {url}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveProfile(index)}
                        className="text-apple-text-tertiary hover:text-apple-red ml-2"
                        aria-label={`Remove ${url}`}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {errors.referenceProfiles && (
                <p className="text-sm text-apple-red" role="alert">
                  {errors.referenceProfiles.message}
                </p>
              )}

              <p className="text-xs text-apple-text-tertiary">
                {watchedValues.referenceProfiles.length}/10 profiles added
              </p>
            </div>
          </Card>

          {/* Keywords & Hashtags */}
          <Card>
            <h2 className="text-lg font-semibold text-apple-text mb-4">Discovery Terms</h2>

            <div className="space-y-4">
              <Controller
                name="keywords"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    label="Keywords"
                    placeholder="Type keyword and press Enter"
                    helperText="Topics and themes related to your brand"
                    maxTags={20}
                  />
                )}
              />

              <Controller
                name="hashtags"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    label="Hashtags"
                    placeholder="Type hashtag (with #) and press Enter"
                    helperText="Hashtags your ideal partners use"
                    maxTags={20}
                    validate={(tag) => tag.startsWith('#') || 'Hashtags must start with #'}
                  />
                )}
              />
            </div>
          </Card>

          {/* Discovery Settings */}
          <Card>
            <h2 className="text-lg font-semibold text-apple-text mb-4">Discovery Settings</h2>

            <div className="space-y-6">
              <Controller
                name="discoveryLimit"
                control={control}
                render={({ field }) => (
                  <Slider
                    value={[field.value]}
                    onValueChange={([value]) => field.onChange(value)}
                    min={10}
                    max={100}
                    step={10}
                    label="Discovery Limit"
                    helperText="Maximum number of profiles to discover"
                  />
                )}
              />

              <Controller
                name="minScoreThreshold"
                control={control}
                render={({ field }) => (
                  <Slider
                    value={[field.value]}
                    onValueChange={([value]) => field.onChange(value)}
                    min={0}
                    max={100}
                    step={5}
                    label="Minimum Score Threshold"
                    helperText="Only show profiles scoring above this value"
                    formatValue={(v) => `${v}%`}
                  />
                )}
              />

              <Controller
                name="targetCountry"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Target Country / Region"
                    placeholder="e.g., India, USA, Germany"
                    helperText="Optional — profiles from this region get priority in scoring"
                  />
                )}
              />

              {/* Follower Range Presets */}
              <div className="space-y-3">
                <span className="block text-sm font-medium text-apple-text" id="follower-range-label">
                  Follower Range
                </span>
                <FollowerPresets
                  onSelect={handlePresetSelect}
                  activePreset={activePreset}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Controller
                  name="minFollowers"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      type="number"
                      label="Min Followers"
                      placeholder="1000"
                      onChange={(e) => field.onChange(Number(e.target.value) || 0)}
                    />
                  )}
                />

                <Controller
                  name="maxFollowers"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      type="number"
                      label="Max Followers"
                      placeholder="500000"
                      onChange={(e) => field.onChange(Number(e.target.value) || 0)}
                    />
                  )}
                />
              </div>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/sessions')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              rightIcon={<ArrowForwardIcon />}
              disabled={!isValid}
            >
              Review & Launch
            </Button>
          </div>
        </form>
      </div>
    )
  }

  // Review Step
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Stepper */}
      <Stepper steps={steps} hideLabelsOnMobile className="mb-8" />

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-apple-text">Review Configuration</h1>
        <p className="text-apple-text-secondary mt-1">
          Verify your settings before launching the discovery
        </p>
      </div>

      {/* Estimated Time */}
      <div className="flex items-center gap-2 text-apple-text-secondary" data-testid="estimated-time">
        <AccessTimeIcon className="w-5 h-5" />
        <span className="text-sm font-medium">Estimated Time: ~3-5 minutes</span>
      </div>

      {/* Info Note */}
      <div 
        className="flex items-start gap-3 p-4 bg-apple-blue/5 border border-apple-blue/20 rounded-xl"
        data-testid="info-note"
        role="note"
      >
        <InfoIcon className="w-5 h-5 text-apple-blue flex-shrink-0 mt-0.5" />
        <p className="text-sm text-apple-text-secondary">
          Once launched, you&apos;ll see profiles appear in real-time as our AI discovers and scores them. 
          You can pause or cancel the discovery at any time from the dashboard.
        </p>
      </div>

      {/* Review Cards */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-apple-text">Basic Information</h2>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<EditIcon />}
            onClick={() => setStep('config')}
          >
            Edit
          </Button>
        </div>
        <dl className="space-y-2">
          <div>
            <dt className="text-sm text-apple-text-secondary">Campaign Name</dt>
            <dd className="text-apple-text font-medium">{watchedValues.name}</dd>
          </div>
          {watchedValues.brandDescription && (
            <div>
              <dt className="text-sm text-apple-text-secondary">Brand Description</dt>
              <dd className="text-apple-text">{watchedValues.brandDescription}</dd>
            </div>
          )}
        </dl>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-apple-text">Reference Profiles</h2>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<EditIcon />}
            onClick={() => setStep('config')}
          >
            Edit
          </Button>
        </div>
        <ul className="space-y-1">
          {watchedValues.referenceProfiles.map((url) => (
            <li key={url} className="text-sm text-apple-text truncate">
              {url}
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-apple-text">Discovery Terms</h2>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<EditIcon />}
            onClick={() => setStep('config')}
          >
            Edit
          </Button>
        </div>
        <dl className="space-y-3">
          <div>
            <dt className="text-sm text-apple-text-secondary">Keywords</dt>
            <dd className="flex flex-wrap gap-2 mt-1">
              {watchedValues.keywords?.length ? (
                watchedValues.keywords.map((kw) => (
                  <span
                    key={kw}
                    className="px-2 py-0.5 bg-gray-100 rounded text-sm"
                  >
                    {kw}
                  </span>
                ))
              ) : (
                <span className="text-apple-text-tertiary text-sm">None</span>
              )}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-apple-text-secondary">Hashtags</dt>
            <dd className="flex flex-wrap gap-2 mt-1">
              {watchedValues.hashtags?.length ? (
                watchedValues.hashtags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-apple-blue/10 text-apple-blue rounded text-sm"
                  >
                    {tag}
                  </span>
                ))
              ) : (
                <span className="text-apple-text-tertiary text-sm">None</span>
              )}
            </dd>
          </div>
        </dl>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-apple-text">Discovery Settings</h2>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<EditIcon />}
            onClick={() => setStep('config')}
          >
            Edit
          </Button>
        </div>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm text-apple-text-secondary">Discovery Limit</dt>
            <dd className="text-apple-text font-medium">{watchedValues.discoveryLimit} profiles</dd>
          </div>
          <div>
            <dt className="text-sm text-apple-text-secondary">Min Score</dt>
            <dd className="text-apple-text font-medium">{watchedValues.minScoreThreshold}%</dd>
          </div>
          <div>
            <dt className="text-sm text-apple-text-secondary">Follower Range</dt>
            <dd className="text-apple-text font-medium">
              {(watchedValues.minFollowers || 0).toLocaleString()} -{' '}
              {(watchedValues.maxFollowers || 0).toLocaleString()}
            </dd>
          </div>
          {watchedValues.targetCountry && (
            <div>
              <dt className="text-sm text-apple-text-secondary">Target Country</dt>
              <dd className="text-apple-text font-medium">{watchedValues.targetCountry}</dd>
            </div>
          )}
        </dl>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button
          type="button"
          variant="secondary"
          leftIcon={<ArrowBackIcon />}
          onClick={() => setStep('config')}
        >
          Back to Edit
        </Button>
        <Button
          type="button"
          leftIcon={<RocketLaunchIcon />}
          loading={createJob.isPending}
          onClick={handleSubmit(handleLaunch)}
        >
          Launch Discovery
        </Button>
      </div>
    </div>
  )
}
