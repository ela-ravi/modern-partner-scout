import { useState } from 'react'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import { cn } from '@/lib/utils'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'

const sidebarNav = [
  { id: 'getting-started', label: 'Getting Started' },
  { id: 'core-concepts', label: 'Core Concepts' },
  { id: 'features', label: 'Features' },
  { id: 'faq', label: 'FAQ' },
  { id: 'api-reference', label: 'API Reference' },
]

const faqItems = [
  {
    question: 'What Instagram data does PartnerScout access?',
    answer:
      'PartnerScout only accesses publicly available profile data: usernames, bios, follower/following counts, post counts, and publicly listed contact information. We never access private accounts, direct messages, or non-public data.',
  },
  {
    question: 'How accurate is the AI scoring?',
    answer:
      'Our AI scoring achieves 95% accuracy based on human review benchmarks. Every score includes detailed reasoning across multiple dimensions (relevance, engagement, authenticity, reach, brand alignment) so you can understand and validate the recommendation.',
  },
  {
    question: 'Can I export my discovered profiles?',
    answer:
      'Yes. All plans include CSV export of discovered profiles with scores, contact information, and metadata. Pro and Enterprise plans also include API access for programmatic data retrieval.',
  },
  {
    question: 'How long does a discovery session take?',
    answer:
      'A typical session analyzing 50 profiles completes in under 5 minutes. Profiles appear in your dashboard in real-time as they are discovered and scored, so you can start reviewing results immediately.',
  },
  {
    question: 'What AI models power PartnerScout?',
    answer:
      'PartnerScout uses a multi-provider AI architecture supporting OpenAI GPT-4, Google Gemini, and local Ollama models. The system uses specialized agents for brand analysis, profile discovery, scoring, and contact extraction.',
  },
  {
    question: 'Is my data secure?',
    answer:
      'Yes. We use encryption in transit (TLS 1.3) and at rest (AES-256), row-level security policies, and infrastructure hosted on SOC 2 compliant providers. See our Privacy Policy for full details.',
  },
]

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border-b border-apple-border">
      <button
        className="w-full flex items-center justify-between py-4 text-left group"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="text-sm font-medium text-apple-text group-hover:text-brand-primary transition-colors">
          {question}
        </span>
        <ExpandMoreIcon
          className={cn(
            'w-5 h-5 text-apple-text-tertiary transition-transform duration-200 shrink-0 ml-4',
            open && 'rotate-180'
          )}
        />
      </button>
      <div
        className={cn(
          'overflow-hidden transition-all duration-300',
          open ? 'max-h-96 pb-4' : 'max-h-0'
        )}
      >
        <p className="text-sm text-apple-text-secondary leading-relaxed">
          {answer}
        </p>
      </div>
    </div>
  )
}

export default function DocsPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Documentation - PartnerScout AI',
    description: 'Learn how to use PartnerScout AI. Covers getting started guides, core concepts, features, and API reference.',
    keywords: 'documentation, API reference, getting started, PartnerScout AI guide',
    canonical: '/docs',
  })

  return (
    <div ref={containerRef} className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16 reveal-section">
          <h1 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Documentation
          </h1>
          <p className="text-lg text-apple-text-secondary max-w-xl mx-auto">
            Everything you need to get started with PartnerScout AI.
          </p>
        </div>

        <div className="grid lg:grid-cols-4 gap-12">
          {/* Sidebar nav */}
          <nav className="hidden lg:block lg:col-span-1" aria-label="Documentation navigation">
            <div className="sticky top-24 space-y-1">
              <p className="text-xs font-bold text-apple-text-tertiary uppercase tracking-wider mb-3">
                Documentation
              </p>
              {sidebarNav.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className="block text-sm text-apple-text-secondary hover:text-brand-primary transition-colors py-1.5"
                >
                  {item.label}
                </a>
              ))}
            </div>
          </nav>

          {/* Content */}
          <div className="lg:col-span-3 space-y-16">
            {/* Getting Started */}
            <section id="getting-started" className="reveal-section">
              <h2 className="text-2xl font-semibold text-apple-text mb-6">Getting Started</h2>

              <div className="space-y-6">
                <div className="card">
                  <h3 className="text-lg font-semibold text-apple-text mb-3">1. Create an Account</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    Sign up at PartnerScout with your email address. No credit card required for the free trial.
                    You'll receive a confirmation email. Click the link to activate your account.
                  </p>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold text-apple-text mb-3">2. Start a Discovery Session</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    Click "New Session" and enter a reference Instagram profile URL (your brand or a brand you admire).
                    Configure your target audience: follower range, engagement rate, content niche, and geographic focus.
                  </p>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold text-apple-text mb-3">3. Review Results</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    Watch as AI agents discover, analyze, and score potential partners in real-time.
                    Each profile card shows the match score, detailed reasoning, follower stats, and contact information.
                    Bookmark your favorites and export the results.
                  </p>
                </div>
              </div>
            </section>

            {/* Core Concepts */}
            <section id="core-concepts" className="reveal-section">
              <h2 className="text-2xl font-semibold text-apple-text mb-6">Core Concepts</h2>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-apple-text mb-2">Brand DNA</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    When you provide a reference profile, our Brand Analyzer agent extracts the brand's "DNA": a
                    structured representation including hashtags, keywords, visual themes, audience demographics, and
                    a semantic embedding vector. This DNA becomes the basis for all discovery and scoring.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-apple-text mb-2">AI Agents</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    PartnerScout uses a multi-agent architecture powered by LangChain. Each agent has a specific role:
                    the Brand Analyzer extracts brand identity, the Discovery Agent finds matching profiles, and the
                    Scorer Agent evaluates each candidate with transparent reasoning.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-apple-text mb-2">Scoring System</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    Profiles are scored 0-100 across six dimensions: engagement quality, content relevance, audience
                    authenticity, reach potential, content quality, and brand alignment. Each dimension includes
                    specific reasoning so you can understand why a profile received its score.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-apple-text mb-2">Session Pipeline</h3>
                  <p className="text-sm text-apple-text-secondary leading-relaxed">
                    Each session moves through stages: <strong>Pending</strong> → <strong>Analyzing</strong> (brand DNA extraction) →{' '}
                    <strong>Discovering</strong> (finding profiles) → <strong>Scoring</strong> (AI evaluation) →{' '}
                    <strong>Completed</strong>. You can monitor progress in real-time on the processing page.
                  </p>
                </div>
              </div>
            </section>

            {/* Features */}
            <section id="features" className="reveal-section">
              <h2 className="text-2xl font-semibold text-apple-text mb-6">Features</h2>

              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  { title: 'Real-time Discovery', desc: 'Profiles appear in your dashboard as they are discovered, no waiting for batch processing.' },
                  { title: 'Smart Filtering', desc: 'Filter by follower range, engagement rate, score threshold, bookmark status, and contact availability.' },
                  { title: 'Email Extraction', desc: 'Automatically extract publicly listed email addresses and other contact information.' },
                  { title: 'AI Email Composer', desc: 'Generate personalized outreach emails with adjustable tone: professional, casual, or enthusiastic.' },
                  { title: 'Bookmark & Organize', desc: 'Bookmark top candidates, skip irrelevant ones, and build your shortlist.' },
                  { title: 'CSV Export', desc: 'Export all discovered profiles with scores, contacts, and metadata for your CRM.' },
                ].map((feature) => (
                  <div key={feature.title} className="p-4 rounded-xl border border-apple-border bg-white">
                    <h3 className="text-sm font-semibold text-apple-text mb-1">{feature.title}</h3>
                    <p className="text-sm text-apple-text-secondary">{feature.desc}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* FAQ */}
            <section id="faq" className="reveal-section">
              <h2 className="text-2xl font-semibold text-apple-text mb-6">
                Frequently Asked Questions
              </h2>

              <div className="border-t border-apple-border">
                {faqItems.map((item) => (
                  <FAQItem key={item.question} {...item} />
                ))}
              </div>
            </section>

            {/* API Reference */}
            <section id="api-reference" className="reveal-section">
              <h2 className="text-2xl font-semibold text-apple-text mb-6">API Reference</h2>

              <div className="space-y-4">
                <p className="text-sm text-apple-text-secondary leading-relaxed">
                  PartnerScout exposes a RESTful API for programmatic access. All endpoints require authentication
                  via Bearer token.
                </p>

                <div className="rounded-xl bg-[#0a0a0a] text-white/90 p-6 font-mono text-sm overflow-x-auto">
                  <p className="text-apple-text-tertiary mb-4"># Base URL</p>
                  <p className="mb-4">https://api.partnerscout.ai/v1</p>

                  <p className="text-apple-text-tertiary mb-2"># Endpoints</p>
                  <p className="text-brand-accent">POST /api/jobs</p>
                  <p className="text-white/50 mb-2 ml-4">Create a new discovery session</p>

                  <p className="text-brand-accent">GET  /api/jobs/:id</p>
                  <p className="text-white/50 mb-2 ml-4">Get session status and summary</p>

                  <p className="text-brand-accent">GET  /api/profiles?job_id=:id</p>
                  <p className="text-white/50 mb-2 ml-4">List discovered profiles with scores</p>

                  <p className="text-brand-accent">POST /api/agent/analyze-brand</p>
                  <p className="text-white/50 mb-2 ml-4">Extract brand DNA from reference profile</p>

                  <p className="text-brand-accent">POST /api/agent/discover</p>
                  <p className="text-white/50 mb-2 ml-4">Discover matching profiles</p>

                  <p className="text-brand-accent">POST /api/agent/score</p>
                  <p className="text-white/50 ml-4">Score a candidate profile</p>
                </div>

                <p className="text-sm text-apple-text-secondary">
                  Full API documentation with request/response examples is available to Pro and Enterprise customers.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
