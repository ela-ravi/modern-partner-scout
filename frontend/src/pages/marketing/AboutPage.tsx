import { Link } from 'react-router-dom'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import SearchIcon from '@mui/icons-material/Search'
import PsychologyIcon from '@mui/icons-material/Psychology'
import ScoreboardIcon from '@mui/icons-material/Scoreboard'
import ContactMailIcon from '@mui/icons-material/ContactMail'

const pipelineSteps = [
  {
    icon: <PsychologyIcon className="w-7 h-7" />,
    title: 'Brand DNA Analysis',
    description:
      'Our AI analyzes reference Instagram profiles to extract brand identity — hashtags, content themes, visual aesthetics, and audience signals.',
  },
  {
    icon: <SearchIcon className="w-7 h-7" />,
    title: 'Partner Discovery',
    description:
      'Using the extracted brand DNA, we search across Instagram to find profiles that share similar audiences, aesthetics, and content patterns.',
  },
  {
    icon: <ScoreboardIcon className="w-7 h-7" />,
    title: '6-Dimension Scoring',
    description:
      'Each candidate is scored across visual match, content alignment, engagement quality, follower health, business indicators, and posting activity.',
  },
  {
    icon: <ContactMailIcon className="w-7 h-7" />,
    title: 'Contact Extraction',
    description:
      'We pull publicly available emails and contact details so you can reach out to top-scoring partners immediately.',
  },
]

const values = [
  {
    title: 'Transparency',
    description: 'Every score comes with detailed reasoning. No black-box decisions — you see exactly why a partner scored the way they did.',
  },
  {
    title: 'Speed',
    description: 'What used to take weeks of manual research now happens in minutes. Discover, score, and contact partners in a single session.',
  },
  {
    title: 'Accuracy',
    description: 'Multi-stage relevance filtering and industry-aware scoring ensure you only see partners who truly align with your brand.',
  },
  {
    title: 'Privacy First',
    description: 'We only access publicly available Instagram data. No private account access, no DM scraping, no non-public information.',
  },
]

export default function AboutPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'About - PartnerScout AI',
    description:
      'Learn about PartnerScout AI\'s mission to help D2C brands find Instagram partners using AI-powered discovery and scoring.',
    keywords: 'about partnerscout, AI partner discovery, Instagram collaboration, D2C marketing',
    canonical: '/about',
  })

  return (
    <div ref={containerRef}>
      {/* Hero */}
      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center reveal-section">
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-apple-text mb-6">
              Partner discovery,{' '}
              <span className="text-gradient-brand">reimagined with AI</span>
            </h1>
            <p className="text-lg sm:text-xl text-apple-text-secondary leading-relaxed">
              PartnerScout AI helps D2C brands find their perfect Instagram collaborators.
              Drop in a brand handle, and our AI pipeline does the rest — analyzing, discovering,
              scoring, and connecting you with ideal partners in minutes.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Pipeline */}
      <section className="py-16 sm:py-24 bg-apple-gray/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 reveal-section">
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
              Our 4-step AI pipeline
            </h2>
            <p className="text-apple-text-secondary text-lg max-w-2xl mx-auto">
              From a single Instagram handle to a ranked list of qualified partners — fully automated.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {pipelineSteps.map((step, i) => (
              <div
                key={step.title}
                className="reveal-section relative bg-white rounded-2xl p-6 border border-apple-border shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 rounded-xl bg-brand-primary/10 text-brand-primary flex items-center justify-center mb-4">
                  {step.icon}
                </div>
                <span className="absolute top-4 right-4 text-sm font-bold text-apple-text-tertiary">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="text-lg font-semibold text-apple-text mb-2">{step.title}</h3>
                <p className="text-sm text-apple-text-secondary leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 reveal-section">
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
              What we stand for
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {values.map((value) => (
              <div key={value.title} className="reveal-section">
                <h3 className="text-lg font-semibold text-apple-text mb-2">{value.title}</h3>
                <p className="text-apple-text-secondary leading-relaxed">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-24 bg-apple-gray/30">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal-section">
          <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
            Want to learn more?
          </h2>
          <p className="text-apple-text-secondary text-lg mb-8">
            Have questions or want to see PartnerScout in action? We'd love to hear from you.
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
            Get in Touch
            <ArrowForwardIcon className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
          </Link>
        </div>
      </section>
    </div>
  )
}
