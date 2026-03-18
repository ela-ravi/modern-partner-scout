import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'

const sections = [
  {
    id: 'acceptance',
    title: '1. Acceptance of Terms',
    content: `By accessing or using PartnerScout AI ("Service"), you agree to be bound by these Terms of Service ("Terms"). If you are using the Service on behalf of an organization, you represent that you have authority to bind that organization to these Terms.

If you do not agree to these Terms, do not use the Service.`,
  },
  {
    id: 'description',
    title: '2. Description of Service',
    content: `PartnerScout AI is an AI-powered platform that:

- Analyzes brand identity from Instagram profiles.
- Discovers potential partner profiles using AI agents.
- Scores and ranks candidate profiles based on relevance, engagement, and brand alignment.
- Extracts publicly available contact information.
- Generates personalized outreach communications.

The Service operates on publicly available Instagram data and does not access private accounts, direct messages, or non-public information.`,
  },
  {
    id: 'accounts',
    title: '3. User Accounts',
    content: `To use the Service, you must:

- Create an account with a valid email address.
- Provide accurate and complete registration information.
- Maintain the security of your account credentials.
- Notify us immediately of any unauthorized access.

You are responsible for all activity that occurs under your account. We reserve the right to suspend or terminate accounts that violate these Terms.`,
  },
  {
    id: 'acceptable-use',
    title: '4. Acceptable Use',
    content: `You agree not to:

- Use the Service to harass, spam, or send unsolicited bulk communications.
- Attempt to scrape, reverse-engineer, or circumvent rate limits.
- Use the Service to collect personal data for purposes unrelated to legitimate business partnerships.
- Impersonate other users, brands, or entities.
- Use automated tools to access the Service outside of our API.
- Violate any applicable laws, regulations, or third-party rights.
- Use the Service in any way that could damage, disable, or impair our infrastructure.`,
  },
  {
    id: 'ai-usage',
    title: '5. AI-Generated Content',
    content: `Our Service uses artificial intelligence to generate scores, recommendations, and communications. You acknowledge that:

- AI outputs are recommendations and should be reviewed before acting upon them.
- Scores and rankings are based on publicly available data and AI analysis; they are not guarantees of partnership success.
- Generated emails and communications should be reviewed and customized before sending.
- We continuously improve our AI models, which may affect scoring over time.
- AI-generated content does not constitute professional advice.`,
  },
  {
    id: 'payment',
    title: '6. Payment & Billing',
    content: `Paid plans are billed in advance on a monthly or annual basis. You agree that:

- Prices are subject to change with 30 days' notice.
- Refunds are available within 14 days of initial purchase if no discovery sessions have been completed.
- Failure to pay may result in service suspension.
- Annual plans are billed for the full year and are non-refundable after the 14-day window.
- Free trial periods do not require payment information and automatically expire.`,
  },
  {
    id: 'intellectual-property',
    title: '7. Intellectual Property',
    content: `- **Our IP**: The Service, including its AI models, algorithms, interface, and documentation, is owned by PartnerScout AI and protected by intellectual property laws.
- **Your content**: You retain ownership of data you input (brand descriptions, reference profiles). You grant us a limited license to process this data to provide the Service.
- **Discovered data**: Publicly available Instagram data processed by the Service does not confer ownership rights to either party.
- **Feedback**: If you provide feedback or suggestions, we may use them without obligation to you.`,
  },
  {
    id: 'limitation',
    title: '8. Limitation of Liability',
    content: `To the maximum extent permitted by law:

- The Service is provided "AS IS" without warranties of any kind.
- We do not guarantee the accuracy, completeness, or reliability of AI-generated scores or recommendations.
- Our total liability shall not exceed the amount you paid us in the 12 months preceding the claim.
- We are not liable for indirect, incidental, special, consequential, or punitive damages.
- We are not liable for any losses resulting from your reliance on AI-generated content.`,
  },
  {
    id: 'termination',
    title: '9. Termination',
    content: `Either party may terminate the agreement:

- You may cancel your account at any time through your account settings.
- We may suspend or terminate your access if you violate these Terms.
- Upon termination, your right to use the Service ceases immediately.
- We will retain your data for 30 days after termination, after which it will be permanently deleted.
- Provisions that by their nature should survive termination will remain in effect.`,
  },
  {
    id: 'changes',
    title: '10. Changes to Terms',
    content: `We may modify these Terms at any time. We will provide notice of material changes through:

- Email notification to your registered address.
- Prominent notice on our website.
- In-app notification.

Continued use of the Service after changes take effect constitutes acceptance of the modified Terms. If you disagree with changes, you should discontinue use and cancel your account.

**Last updated**: January 2026
**Effective date**: January 2026`,
  },
]

export default function TermsPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'Terms of Service - PartnerScout AI',
    description: 'Terms and conditions for using the PartnerScout AI platform.',
    keywords: 'terms of service, terms and conditions, PartnerScout AI legal',
    canonical: '/terms',
  })

  return (
    <div ref={containerRef} className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16 reveal-section">
          <h1 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Terms of Service
          </h1>
          <p className="text-lg text-apple-text-secondary max-w-xl mx-auto">
            Please read these terms carefully before using PartnerScout AI.
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
