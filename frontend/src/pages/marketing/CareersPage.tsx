import { Link } from 'react-router-dom'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import WorkIcon from '@mui/icons-material/Work'
import GroupsIcon from '@mui/icons-material/Groups'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import BalanceIcon from '@mui/icons-material/Balance'

const cultureValues = [
  {
    icon: <RocketLaunchIcon className="w-6 h-6" />,
    title: 'Ship fast, iterate faster',
    description: 'We move quickly, test ideas in production, and refine based on real user feedback.',
  },
  {
    icon: <GroupsIcon className="w-6 h-6" />,
    title: 'Small team, big impact',
    description: 'Every team member has ownership over meaningful parts of the product. No bureaucracy.',
  },
  {
    icon: <BalanceIcon className="w-6 h-6" />,
    title: 'Work-life balance',
    description: 'Remote-first with flexible hours. We care about output, not hours at a desk.',
  },
  {
    icon: <WorkIcon className="w-6 h-6" />,
    title: 'Learn constantly',
    description: 'AI, scraping, scoring, UX. You\'ll work across the full stack and pick up something new every week.',
  },
]

const openings = [
  {
    title: 'Full-Stack Engineer',
    type: 'Full-time, Remote',
    description: 'Build and improve our React + FastAPI platform. Work on AI agent pipelines, real-time processing, and the user-facing dashboard.',
  },
  {
    title: 'AI/ML Engineer',
    type: 'Full-time, Remote',
    description: 'Design and fine-tune our multi-agent scoring system. Work with LangChain, embeddings, and multi-provider LLM integrations.',
  },
  {
    title: 'Growth Marketing Lead',
    type: 'Full-time, Remote',
    description: 'Drive user acquisition for D2C brands. Own content strategy, partnerships, and product-led growth initiatives.',
  },
]

export default function CareersPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Careers - PartnerScout AI',
    description: 'Join the PartnerScout AI team. Explore open positions and our company culture.',
    keywords: 'careers, jobs, PartnerScout AI, remote work, AI engineer, full-stack developer',
    canonical: '/careers',
  })

  return (
    <div ref={containerRef}>
      {/* Hero */}
      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center reveal-section">
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-apple-text mb-6">
              Join our{' '}
              <span className="text-gradient-brand">team</span>
            </h1>
            <p className="text-lg sm:text-xl text-apple-text-secondary leading-relaxed">
              We're building the future of partner discovery. Help us make it easier for
              brands to find the right collaborators with AI.
            </p>
          </div>
        </div>
      </section>

      {/* Culture */}
      <section className="py-16 sm:py-24 bg-apple-gray/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 reveal-section">
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
              How we work
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {cultureValues.map((value) => (
              <div
                key={value.title}
                className="reveal-section bg-white rounded-2xl p-6 border border-apple-border"
              >
                <div className="w-12 h-12 rounded-xl bg-brand-primary/10 text-brand-primary flex items-center justify-center mb-4">
                  {value.icon}
                </div>
                <h3 className="text-lg font-semibold text-apple-text mb-2">{value.title}</h3>
                <p className="text-sm text-apple-text-secondary leading-relaxed">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Openings */}
      <section className="py-16 sm:py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 reveal-section">
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
              Open positions
            </h2>
            <p className="text-apple-text-secondary text-lg">
              Don't see a perfect match? Reach out anyway. We're always looking for talented people.
            </p>
          </div>

          <div className="space-y-4">
            {openings.map((job) => (
              <Link
                key={job.title}
                to="/contact"
                className="reveal-section group block bg-white rounded-2xl p-6 border border-apple-border hover:border-brand-primary/30 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-semibold text-apple-text group-hover:text-brand-primary transition-colors">
                      {job.title}
                    </h3>
                    <p className="text-sm text-apple-text-tertiary mt-1">{job.type}</p>
                    <p className="text-sm text-apple-text-secondary mt-3 leading-relaxed">{job.description}</p>
                  </div>
                  <ArrowForwardIcon className="w-5 h-5 text-apple-text-tertiary group-hover:text-brand-primary transition-all duration-200 group-hover:translate-x-1 flex-shrink-0 mt-1" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-24 bg-apple-gray/30">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal-section">
          <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
            Interested?
          </h2>
          <p className="text-apple-text-secondary text-lg mb-8">
            Send us a message with your resume and what excites you about PartnerScout.
          </p>
          <Link
            to="/contact"
            className="group inline-flex items-center gap-2 px-8 py-4 rounded-2xl text-white font-semibold text-lg
              bg-gradient-to-r from-brand-primary to-brand-accent
              shadow-[0_8px_30px_rgba(0,122,255,0.35)]
              hover:shadow-[0_12px_40px_rgba(0,122,255,0.5)]
              hover:scale-[1.03] active:scale-[0.98]
              transition-all duration-200 ease-out"
          >
            Apply Now
            <ArrowForwardIcon className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
          </Link>
        </div>
      </section>
    </div>
  )
}
