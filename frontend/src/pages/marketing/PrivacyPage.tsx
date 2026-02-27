import { useScrollReveal } from '@/hooks/useScrollReveal'

const sections = [
  {
    id: 'information-we-collect',
    title: '1. Information We Collect',
    content: `We collect information you provide directly, such as when you create an account, use our services, or contact us. This includes:

- **Account information**: Name, email address, company name, and password when you register.
- **Usage data**: Discovery sessions you create, profiles you analyze, and preferences you set.
- **Payment information**: Billing details processed securely through our payment provider (we do not store card numbers).
- **Communications**: Messages you send through our contact forms or support channels.`,
  },
  {
    id: 'how-we-use',
    title: '2. How We Use Your Information',
    content: `We use your information to:

- Provide, maintain, and improve our services.
- Process discovery sessions and deliver AI-powered partner recommendations.
- Send you service-related communications and updates.
- Respond to your support requests and inquiries.
- Analyze usage patterns to improve our AI models and user experience.
- Detect and prevent fraud, abuse, and security incidents.`,
  },
  {
    id: 'data-sharing',
    title: '3. Data Sharing & Disclosure',
    content: `We do not sell your personal information. We may share information with:

- **Service providers**: Third-party services that help us operate (hosting, analytics, payment processing).
- **AI processing partners**: Data processed by our AI providers (OpenAI, Google) is subject to their data processing agreements and is not used to train their models.
- **Legal requirements**: When required by law, regulation, or legal process.
- **Business transfers**: In connection with a merger, acquisition, or sale of assets.`,
  },
  {
    id: 'instagram-data',
    title: '4. Instagram Data Processing',
    content: `Our service analyzes publicly available Instagram profile data. We:

- Only access publicly available information (bios, post counts, follower counts).
- Do not access private accounts or direct messages.
- Process data through authorized API partners (Apify) in compliance with platform terms.
- Store discovered profile data only for the duration of your active sessions.
- Allow you to delete all discovered data at any time through your dashboard.`,
  },
  {
    id: 'data-security',
    title: '5. Data Security',
    content: `We implement industry-standard security measures including:

- Encryption in transit (TLS 1.3) and at rest (AES-256).
- Row-level security (RLS) policies in our database.
- Regular security audits and vulnerability assessments.
- Access controls and authentication via Supabase Auth.
- Infrastructure hosted on SOC 2 compliant providers.`,
  },
  {
    id: 'data-retention',
    title: '6. Data Retention',
    content: `We retain your data as follows:

- **Account data**: Retained while your account is active and for 30 days after deletion request.
- **Discovery sessions**: Active sessions retained until you delete them. Completed sessions archived for 90 days.
- **Usage analytics**: Aggregated, anonymized analytics retained indefinitely.
- **Support communications**: Retained for 2 years after last interaction.`,
  },
  {
    id: 'your-rights',
    title: '7. Your Rights',
    content: `Depending on your jurisdiction, you may have the right to:

- **Access**: Request a copy of the personal data we hold about you.
- **Correction**: Request correction of inaccurate personal data.
- **Deletion**: Request deletion of your personal data.
- **Portability**: Request your data in a structured, machine-readable format.
- **Objection**: Object to processing of your data for certain purposes.
- **Restriction**: Request restriction of processing in certain circumstances.

To exercise these rights, contact us at privacy@partnerscout.ai.`,
  },
  {
    id: 'cookies',
    title: '8. Cookies & Tracking',
    content: `We use essential cookies to:

- Maintain your authenticated session.
- Remember your preferences and settings.
- Ensure security and prevent fraud.

We do not use third-party advertising cookies. Analytics cookies are only used with your consent and can be disabled in your browser settings.`,
  },
  {
    id: 'international',
    title: '9. International Data Transfers',
    content: `Your data may be processed in the United States and other countries where our service providers operate. We ensure appropriate safeguards are in place, including:

- Standard Contractual Clauses (SCCs) for EU/EEA data transfers.
- Data processing agreements with all sub-processors.
- Compliance with applicable data protection frameworks.`,
  },
  {
    id: 'changes',
    title: '10. Changes to This Policy',
    content: `We may update this Privacy Policy from time to time. We will notify you of material changes by:

- Posting a notice on our website.
- Sending an email to your registered address.
- Displaying an in-app notification.

Your continued use of PartnerScout after changes are posted constitutes acceptance of the updated policy.

**Last updated**: January 2026
**Effective date**: January 2026`,
  },
]

export default function PrivacyPage() {
  const containerRef = useScrollReveal()

  return (
    <div ref={containerRef} className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16 reveal-section">
          <h1 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Privacy Policy
          </h1>
          <p className="text-lg text-apple-text-secondary max-w-xl mx-auto">
            Your privacy matters. Here's how PartnerScout collects, uses, and protects your data.
          </p>
        </div>

        <div className="grid lg:grid-cols-4 gap-12">
          {/* Sticky TOC sidebar */}
          <nav className="hidden lg:block lg:col-span-1" aria-label="Table of contents">
            <div className="sticky top-24 space-y-1">
              <p className="text-xs font-bold text-apple-text-tertiary uppercase tracking-wider mb-3">
                On this page
              </p>
              {sections.map((section) => (
                <a
                  key={section.id}
                  href={`#${section.id}`}
                  className="block text-sm text-apple-text-secondary hover:text-brand-primary transition-colors py-1.5 truncate"
                >
                  {section.title}
                </a>
              ))}
            </div>
          </nav>

          {/* Content */}
          <div className="lg:col-span-3 space-y-12">
            {sections.map((section) => (
              <section key={section.id} id={section.id} className="reveal-section">
                <h2 className="text-xl font-semibold text-apple-text mb-4">
                  {section.title}
                </h2>
                <div className="prose prose-sm max-w-none text-apple-text-secondary leading-relaxed whitespace-pre-line">
                  {section.content.split('\n').map((line, i) => {
                    if (line.startsWith('- **')) {
                      const match = line.match(/^- \*\*(.+?)\*\*: (.+)$/)
                      if (match) {
                        return (
                          <p key={i} className="ml-4 mb-1">
                            &bull; <strong className="text-apple-text">{match[1]}</strong>: {match[2]}
                          </p>
                        )
                      }
                    }
                    if (line.startsWith('- ')) {
                      return (
                        <p key={i} className="ml-4 mb-1">
                          &bull; {line.slice(2)}
                        </p>
                      )
                    }
                    if (line.startsWith('**')) {
                      const match = line.match(/^\*\*(.+?)\*\*: (.+)$/)
                      if (match) {
                        return (
                          <p key={i} className="mt-2">
                            <strong className="text-apple-text">{match[1]}</strong>: {match[2]}
                          </p>
                        )
                      }
                    }
                    if (line.trim() === '') return <br key={i} />
                    return <p key={i} className="mb-2">{line}</p>
                  })}
                </div>
              </section>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
