import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import NewReleasesIcon from '@mui/icons-material/NewReleases'

const releases = [
  {
    version: 'v1.5',
    date: 'March 2026',
    tag: 'Latest',
    changes: [
      'Relevance pre-filter with 2-tier keyword matching to eliminate irrelevant profiles',
      'Industry relevance check requiring 2+ keyword hits in scorer',
      'Bulk paste support for keywords and hashtags with auto-prefix',
      'Rebalanced scoring weights: content alignment 25%, engagement 15%, business indicators 20%',
      'Solid sticky header and dynamic CTA buttons across marketing pages',
    ],
  },
  {
    version: 'v1.4',
    date: 'February 2026',
    changes: [
      'Smarter heuristic scoring with expanded profile type detection',
      'Consume partner keywords after Round 1 fallback usage for broader discovery',
      'Min-reference anchor for follower calibration instead of average',
      'Keep searching until N qualified profiles found',
      'Stop homepage auto-redirect to /sessions for authenticated users',
    ],
  },
  {
    version: 'v1.3',
    date: 'January 2026',
    changes: [
      '6-dimension scoring system: visual, content, engagement, follower quality, business indicators, activity',
      'Real-time processing dashboard with live profile updates',
      'Bookmark and filter discovered profiles',
      'Profile detail view with score breakdown and reasoning',
    ],
  },
  {
    version: 'v1.2',
    date: 'December 2025',
    changes: [
      'Multi-reference profile support: analyze up to 5 brand handles',
      'Custom keywords and hashtags input for fine-tuned discovery',
      'Contact email extraction from public profile data',
      'Session management with history and re-run capabilities',
    ],
  },
  {
    version: 'v1.1',
    date: 'November 2025',
    changes: [
      'Brand DNA analysis agent with hashtag and keyword extraction',
      'Discovery agent using Apify Instagram scraping',
      'Basic scoring with engagement rate and follower count',
      'User authentication via Supabase Auth',
    ],
  },
  {
    version: 'v1.0',
    date: 'October 2025',
    changes: [
      'Initial release of PartnerScout AI',
      'Single reference profile analysis',
      'Basic partner discovery pipeline',
      'React dashboard with session creation flow',
    ],
  },
]

export default function ChangelogPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Changelog - PartnerScout AI',
    description: 'Latest updates, new features, and improvements to the PartnerScout AI platform.',
    keywords: 'changelog, updates, new features, PartnerScout AI release notes',
    canonical: '/changelog',
  })

  return (
    <div ref={containerRef}>
      {/* Hero */}
      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center reveal-section">
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-apple-text mb-6">
              Changelog
            </h1>
            <p className="text-lg sm:text-xl text-apple-text-secondary leading-relaxed">
              Every update, new feature, and improvement to PartnerScout AI.
            </p>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="pb-16 sm:pb-24">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-[19px] top-2 bottom-2 w-px bg-apple-border" />

            <div className="space-y-12">
              {releases.map((release) => (
                <div key={release.version} className="reveal-section relative pl-12">
                  {/* Timeline dot */}
                  <div className="absolute left-0 top-1 w-10 h-10 rounded-full bg-white border-2 border-apple-border flex items-center justify-center">
                    <NewReleasesIcon className="w-5 h-5 text-brand-primary" />
                  </div>

                  <div>
                    <div className="flex items-center gap-3 mb-3">
                      <h2 className="text-xl font-bold text-apple-text">{release.version}</h2>
                      <span className="text-sm text-apple-text-tertiary">{release.date}</span>
                      {release.tag && (
                        <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-apple-green/10 text-apple-green">
                          {release.tag}
                        </span>
                      )}
                    </div>
                    <ul className="space-y-2">
                      {release.changes.map((change, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-apple-text-secondary leading-relaxed">
                          <span className="w-1.5 h-1.5 rounded-full bg-brand-primary/40 mt-1.5 flex-shrink-0" />
                          {change}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
