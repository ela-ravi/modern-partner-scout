import { Link } from 'react-router-dom'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

const articles = [
  {
    title: 'How AI Is Transforming Partner Discovery for D2C Brands',
    excerpt:
      'Manual outreach is slow and inconsistent. Learn how AI-powered tools analyze brand identity and surface ideal collaborators in minutes instead of weeks.',
    category: 'AI & Marketing',
    date: 'Mar 8, 2026',
    readTime: '5 min read',
    link: '/docs',
  },
  {
    title: 'Inside PartnerScout\'s 6-Dimension Scoring System',
    excerpt:
      'Not all partners are equal. We break down how visual aesthetics, content alignment, engagement quality, follower health, business indicators, and activity recency combine into a single score.',
    category: 'Product',
    date: 'Feb 22, 2026',
    readTime: '7 min read',
    link: '/docs',
  },
  {
    title: 'Why Engagement Rate Alone Isn\'t Enough to Evaluate Partners',
    excerpt:
      'High engagement doesn\'t always mean high quality. Retail accounts naturally have lower engagement than influencers — here\'s why multi-dimensional scoring matters.',
    category: 'Insights',
    date: 'Feb 10, 2026',
    readTime: '4 min read',
    link: '/docs',
  },
  {
    title: 'Bulk Discovery: Analyzing Multiple Reference Profiles at Once',
    excerpt:
      'Drop in up to 5 reference profiles to build a richer brand DNA. Bulk paste keywords and hashtags to fine-tune discovery for your exact niche.',
    category: 'Features',
    date: 'Jan 28, 2026',
    readTime: '3 min read',
    link: '/docs',
  },
]

const categoryColors: Record<string, string> = {
  'AI & Marketing': 'bg-brand-primary/10 text-brand-primary',
  Product: 'bg-apple-green/10 text-apple-green',
  Insights: 'bg-brand-accent/10 text-brand-accent',
  Features: 'bg-apple-orange/10 text-apple-orange',
}

export default function BlogPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Blog - PartnerScout AI',
    description:
      'Insights on AI-powered partner discovery, Instagram marketing strategies, and D2C brand growth tips.',
    keywords: 'partner discovery blog, Instagram marketing, D2C brand growth, AI scoring',
    canonical: '/blog',
  })

  return (
    <div ref={containerRef}>
      {/* Hero */}
      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center reveal-section">
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-apple-text mb-6">
              Blog
            </h1>
            <p className="text-lg sm:text-xl text-apple-text-secondary leading-relaxed">
              Insights on AI-powered partner discovery, scoring strategies,
              and growing your D2C brand through smarter collaborations.
            </p>
          </div>
        </div>
      </section>

      {/* Articles Grid */}
      <section className="pb-16 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 gap-8">
            {articles.map((article) => (
              <Link
                key={article.title}
                to={article.link}
                className="reveal-section group bg-white rounded-2xl border border-apple-border p-6 hover:shadow-lg hover:border-brand-primary/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <span
                    className={`text-xs font-medium px-3 py-1 rounded-full ${categoryColors[article.category] || 'bg-apple-gray text-apple-text-secondary'}`}
                  >
                    {article.category}
                  </span>
                  <span className="text-xs text-apple-text-tertiary">{article.date}</span>
                  <span className="text-xs text-apple-text-tertiary">{article.readTime}</span>
                </div>
                <h2 className="text-xl font-semibold text-apple-text mb-3 group-hover:text-brand-primary transition-colors">
                  {article.title}
                </h2>
                <p className="text-sm text-apple-text-secondary leading-relaxed mb-4">
                  {article.excerpt}
                </p>
                <span className="inline-flex items-center gap-1 text-sm font-medium text-brand-primary">
                  Read more
                  <ArrowForwardIcon className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-24 bg-apple-gray/30">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center reveal-section">
          <h2 className="font-display text-3xl sm:text-4xl tracking-tight text-apple-text mb-4">
            Ready to try it yourself?
          </h2>
          <p className="text-apple-text-secondary text-lg mb-8">
            See how PartnerScout discovers and scores partners for your brand.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/login"
              className="group inline-flex items-center gap-2 px-8 py-4 rounded-2xl text-white font-semibold text-lg
                bg-gradient-to-r from-brand-primary to-brand-accent
                shadow-[0_8px_30px_rgba(0,122,255,0.35)]
                hover:shadow-[0_12px_40px_rgba(0,122,255,0.5)]
                hover:scale-[1.03] active:scale-[0.98]
                transition-all duration-200 ease-out"
            >
              Get Started Free
              <ArrowForwardIcon className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
            </Link>
            <Link
              to="/docs"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold text-lg
                text-apple-text bg-white border-2 border-apple-border
                shadow-[0_4px_20px_rgba(0,0,0,0.08)]
                hover:border-brand-primary/40 hover:shadow-[0_8px_30px_rgba(0,122,255,0.15)]
                hover:scale-[1.03] active:scale-[0.98]
                transition-all duration-200 ease-out"
            >
              Read the Docs
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
