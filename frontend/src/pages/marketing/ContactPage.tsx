import { useState, type FormEvent } from 'react'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/Toast'
import EmailIcon from '@mui/icons-material/Email'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import PhoneIcon from '@mui/icons-material/Phone'
import SendIcon from '@mui/icons-material/Send'

const contactInfo = [
  {
    icon: <EmailIcon className="w-5 h-5" />,
    label: 'Email',
    value: 'hello@partnerscout.ai',
    href: 'mailto:hello@partnerscout.ai',
  },
  {
    icon: <PhoneIcon className="w-5 h-5" />,
    label: 'Phone',
    value: '+1 (555) 000-1234',
    href: 'tel:+15550001234',
  },
  {
    icon: <LocationOnIcon className="w-5 h-5" />,
    label: 'Office',
    value: 'San Francisco, CA',
    href: undefined,
  },
]

export default function ContactPage() {
  const containerRef = useScrollReveal()
  const { success } = useToast()
  const [submitting, setSubmitting] = useState(false)

  usePageMeta({
    title: 'Contact Us - PartnerScout AI',
    description: 'Get in touch with the PartnerScout AI team for questions, demos, or partnership inquiries.',
    keywords: 'contact PartnerScout, support, demo request, partnership inquiry',
    canonical: '/contact',
  })

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSubmitting(true)

    // Demo-first: simulate submission
    setTimeout(() => {
      setSubmitting(false)
      success('Message sent! We\'ll get back to you within 24 hours.')
      ;(e.target as HTMLFormElement).reset()
    }, 1000)
  }

  return (
    <div ref={containerRef} className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16 reveal-section">
          <p className="text-brand-primary font-semibold text-sm tracking-wide uppercase mb-3">
            Contact Us
          </p>
          <h1 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Get in touch
          </h1>
          <p className="text-lg text-apple-text-secondary max-w-xl mx-auto">
            Have a question or want to learn more? We'd love to hear from you.
          </p>
        </div>

        <div className="grid lg:grid-cols-5 gap-12 lg:gap-16">
          {/* Form */}
          <div className="lg:col-span-3 reveal-section">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid sm:grid-cols-2 gap-6">
                <Input
                  label="Name"
                  name="name"
                  placeholder="Your name"
                  required
                />
                <Input
                  label="Email"
                  name="email"
                  type="email"
                  placeholder="you@company.com"
                  required
                />
              </div>

              <Input
                label="Company"
                name="company"
                placeholder="Your company name"
              />

              <Input
                label="Subject"
                name="subject"
                placeholder="How can we help?"
                required
              />

              <Textarea
                label="Message"
                name="message"
                placeholder="Tell us more about your needs..."
                required
                rows={6}
              />

              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={submitting}
                rightIcon={<SendIcon className="w-5 h-5" />}
              >
                Send Message
              </Button>
            </form>
          </div>

          {/* Contact info sidebar */}
          <div className="lg:col-span-2 reveal-section">
            <div className="sticky top-24 space-y-8">
              <div>
                <h2 className="text-lg font-semibold text-apple-text mb-6">
                  Other ways to reach us
                </h2>

                <div className="space-y-4">
                  {contactInfo.map((info) => (
                    <div key={info.label} className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-xl bg-brand-primary/10 flex items-center justify-center text-brand-primary shrink-0">
                        {info.icon}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-apple-text">{info.label}</div>
                        {info.href ? (
                          <a
                            href={info.href}
                            className="text-sm text-brand-primary hover:underline"
                          >
                            {info.value}
                          </a>
                        ) : (
                          <div className="text-sm text-apple-text-secondary">{info.value}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* FAQ teaser */}
              <div className="p-6 rounded-2xl bg-apple-gray border border-apple-border">
                <h3 className="text-sm font-semibold text-apple-text mb-2">
                  Looking for answers?
                </h3>
                <p className="text-sm text-apple-text-secondary mb-3">
                  Check out our documentation for guides, FAQs, and API references.
                </p>
                <Button variant="ghost" size="sm" asChild>
                  <a href="/docs">Visit Docs</a>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
