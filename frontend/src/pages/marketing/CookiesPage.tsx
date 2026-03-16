import { Link } from 'react-router-dom'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'

const cookieTypes = [
  {
    name: 'Essential Cookies',
    description:
      'These cookies are required for the website to function properly. They enable core features like user authentication, session management, and security. You cannot disable these cookies.',
    examples: ['Authentication session tokens', 'CSRF protection tokens', 'Cookie consent preferences'],
  },
  {
    name: 'Functional Cookies',
    description:
      'These cookies enable personalized features and remember your preferences, such as your selected theme, language, or previously used search settings.',
    examples: ['Dashboard layout preferences', 'Recently viewed sessions', 'Form auto-fill data'],
  },
  {
    name: 'Analytics Cookies',
    description:
      'These cookies help us understand how visitors interact with our website. All data is aggregated and anonymized. We use this information to improve our platform.',
    examples: ['Page view tracking', 'Feature usage metrics', 'Error reporting'],
  },
]

export default function CookiesPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Cookie Policy - PartnerScout AI',
    description: 'How PartnerScout AI uses cookies and similar tracking technologies on our website.',
    keywords: 'cookie policy, cookies, tracking, PartnerScout AI privacy',
    canonical: '/cookies',
  })

  return (
    <div ref={containerRef}>
      {/* Hero */}
      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center reveal-section">
            <h1 className="font-display text-4xl sm:text-5xl tracking-tight text-apple-text mb-6">
              Cookie Policy
            </h1>
            <p className="text-lg text-apple-text-secondary leading-relaxed">
              Last updated: March 2026
            </p>
          </div>
        </div>
      </section>

      {/* Content */}
      <section className="pb-16 sm:pb-24">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Intro */}
          <div className="reveal-section prose-section mb-12">
            <h2 className="text-2xl font-semibold text-apple-text mb-4">What are cookies?</h2>
            <p className="text-apple-text-secondary leading-relaxed mb-4">
              Cookies are small text files stored on your device when you visit a website. They help
              the website remember your preferences, keep you logged in, and understand how you use
              the site. PartnerScout AI uses cookies to provide a secure, functional experience.
            </p>
          </div>

          {/* Cookie Types */}
          <div className="space-y-10">
            {cookieTypes.map((type) => (
              <div key={type.name} className="reveal-section">
                <h2 className="text-xl font-semibold text-apple-text mb-3">{type.name}</h2>
                <p className="text-apple-text-secondary leading-relaxed mb-4">{type.description}</p>
                <div className="bg-apple-gray/50 rounded-xl p-4 border border-apple-border">
                  <p className="text-sm font-medium text-apple-text mb-2">Examples:</p>
                  <ul className="space-y-1.5">
                    {type.examples.map((example, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-apple-text-secondary">
                        <span className="w-1.5 h-1.5 rounded-full bg-brand-primary/40 mt-1.5 flex-shrink-0" />
                        {example}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          {/* Managing Cookies */}
          <div className="reveal-section mt-12">
            <h2 className="text-2xl font-semibold text-apple-text mb-4">Managing your cookies</h2>
            <p className="text-apple-text-secondary leading-relaxed mb-4">
              Most web browsers allow you to control cookies through their settings. You can typically
              find these in the "Options" or "Preferences" menu of your browser. You can set your
              browser to block or delete cookies, though this may impact site functionality.
            </p>
            <p className="text-apple-text-secondary leading-relaxed mb-4">
              For more information about cookies and how to manage them, visit{' '}
              <a
                href="https://www.allaboutcookies.org"
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand-primary hover:underline"
              >
                allaboutcookies.org
              </a>
              .
            </p>
          </div>

          {/* Third-party */}
          <div className="reveal-section mt-12">
            <h2 className="text-2xl font-semibold text-apple-text mb-4">Third-party services</h2>
            <p className="text-apple-text-secondary leading-relaxed mb-4">
              PartnerScout AI uses Supabase for authentication and data storage. Supabase may set its
              own cookies to maintain your login session. We do not use third-party advertising cookies.
            </p>
          </div>

          {/* Link to Privacy */}
          <div className="reveal-section mt-12 p-6 bg-apple-gray/30 rounded-2xl border border-apple-border">
            <p className="text-apple-text-secondary leading-relaxed">
              For more details on how we handle your data, please review our{' '}
              <Link to="/privacy" className="text-brand-primary font-medium hover:underline">
                Privacy Policy
              </Link>
              . If you have questions about our cookie practices, please{' '}
              <Link to="/contact" className="text-brand-primary font-medium hover:underline">
                contact us
              </Link>
              .
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
