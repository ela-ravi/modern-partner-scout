import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import SpeedIcon from '@mui/icons-material/Speed'
import InsightsIcon from '@mui/icons-material/Insights'
import SecurityIcon from '@mui/icons-material/Security'
import TuneIcon from '@mui/icons-material/Tune'
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions'

const features = [
  {
    title: 'AI-Powered Discovery',
    description:
      'Three specialized AI agents work together: one reads the brand, one finds matching profiles, one scores them. You get the reasoning behind every recommendation.',
    icon: <AutoAwesomeIcon className="w-6 h-6" />,
    span: 'sm:col-span-2',
    gradient: 'from-brand-primary/10 to-purple-50',
  },
  {
    title: 'Lightning Fast',
    description:
      'Process 50+ profiles in under 10 minutes. Real-time dashboard updates as profiles are discovered and scored.',
    icon: <SpeedIcon className="w-6 h-6" />,
    span: '',
    gradient: 'from-apple-green/10 to-emerald-50',
  },
  {
    title: 'Explainable Scores',
    description:
      'Every score comes with detailed reasoning across engagement, relevance, authenticity, reach, and brand alignment.',
    icon: <InsightsIcon className="w-6 h-6" />,
    span: '',
    gradient: 'from-apple-orange/10 to-amber-50',
  },
  {
    title: 'Smart Filters',
    description:
      'Filter by follower range, engagement rate, content niche, country, and minimum score threshold.',
    icon: <TuneIcon className="w-6 h-6" />,
    span: '',
    gradient: 'from-brand-primary/10 to-fuchsia-50',
  },
  {
    title: 'Enterprise Ready',
    description:
      'SOC 2 compliant infrastructure, role-based access, and SSO integration for teams of any size.',
    icon: <SecurityIcon className="w-6 h-6" />,
    span: '',
    gradient: 'from-apple-red/10 to-rose-50',
  },
  {
    title: 'API & Webhooks',
    description:
      'RESTful API, real-time webhooks, and n8n workflow integration for custom automation pipelines.',
    icon: <IntegrationInstructionsIcon className="w-6 h-6" />,
    span: 'sm:col-span-2',
    gradient: 'from-purple-50 to-brand-primary/5',
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 sm:py-32 bg-apple-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16 reveal-section">
          <p className="text-brand-primary font-semibold text-sm tracking-wide uppercase mb-3">
            Features
          </p>
          <h2 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Everything you need to scale partnerships
          </h2>
          <p className="text-lg text-apple-text-secondary max-w-2xl mx-auto">
            From AI-powered discovery to automated outreach, PartnerScout handles the entire
            partner pipeline.
          </p>
        </div>

        {/* Bento grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className={`reveal-item ${feature.span} group relative rounded-2xl border border-apple-border bg-gradient-to-br ${feature.gradient} p-6 sm:p-8 transition-all duration-300 hover:shadow-medium hover:-translate-y-1`}
            >
              <div className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-brand-primary mb-5 group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>

              <h3 className="text-lg font-semibold text-apple-text mb-2">
                {feature.title}
              </h3>

              <p className="text-sm text-apple-text-secondary leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
