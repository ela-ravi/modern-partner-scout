import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'
import CheckIcon from '@mui/icons-material/Check'

const plans = [
  {
    name: 'Starter',
    monthlyPrice: 49,
    annualPrice: 39,
    description: 'For solo founders exploring partner discovery for the first time.',
    features: [
      '5 discovery sessions/month',
      '50 profiles per session',
      'AI scoring & reasoning',
      'Email extraction',
      'CSV export',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Pro',
    monthlyPrice: 149,
    annualPrice: 119,
    description: 'For brands running regular outreach campaigns at higher volume.',
    features: [
      'Unlimited sessions',
      '200 profiles per session',
      'Advanced AI scoring',
      'Email extraction & outreach',
      'Real-time dashboard',
      'Priority support',
      'API access',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    monthlyPrice: null,
    annualPrice: null,
    description: 'For agencies and teams that need custom integrations and dedicated support.',
    features: [
      'Everything in Pro',
      'Unlimited profiles',
      'Custom AI models',
      'SSO & RBAC',
      'Dedicated account manager',
      'SLA guarantee',
      'Webhook integrations',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
]

export function PricingSection() {
  const [annual, setAnnual] = useState(false)

  return (
    <section id="pricing" className="py-24 sm:py-32 bg-apple-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12 reveal-section">
          <p className="text-brand-primary font-semibold text-sm tracking-wide uppercase mb-3">
            Pricing
          </p>
          <h2 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight mb-4">
            Simple, transparent pricing
          </h2>
          <p className="text-lg text-apple-text-secondary max-w-xl mx-auto mb-8">
            Start free, scale when you're ready. No hidden fees.
          </p>

          {/* Billing toggle */}
          <div className="inline-flex items-center gap-3 bg-apple-gray rounded-full p-1">
            <button
              className={cn(
                'px-5 py-2 rounded-full text-sm font-medium transition-all duration-200',
                !annual ? 'bg-white text-apple-text shadow-sm' : 'text-apple-text-secondary'
              )}
              onClick={() => setAnnual(false)}
            >
              Monthly
            </button>
            <button
              className={cn(
                'px-5 py-2 rounded-full text-sm font-medium transition-all duration-200',
                annual ? 'bg-white text-apple-text shadow-sm' : 'text-apple-text-secondary'
              )}
              onClick={() => setAnnual(true)}
            >
              Annual
              <span className="ml-1.5 text-xs text-brand-accent font-bold">-20%</span>
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 items-start">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={cn(
                'reveal-item rounded-2xl p-6 sm:p-8 border transition-all duration-300',
                plan.popular
                  ? 'border-brand-primary bg-white shadow-large scale-[1.02] relative'
                  : 'border-apple-border bg-white hover:shadow-medium'
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 bg-brand-primary text-white text-xs font-bold rounded-full">
                  Most Popular
                </div>
              )}

              <h3 className="text-xl font-semibold text-apple-text mb-2">{plan.name}</h3>
              <p className="text-sm text-apple-text-secondary mb-6">{plan.description}</p>

              {/* Price */}
              <div className="mb-6">
                {plan.monthlyPrice ? (
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-apple-text">
                      ${annual ? plan.annualPrice : plan.monthlyPrice}
                    </span>
                    <span className="text-apple-text-secondary">/mo</span>
                  </div>
                ) : (
                  <div className="text-4xl font-bold text-apple-text">Custom</div>
                )}
              </div>

              <Button
                variant={plan.popular ? 'primary' : 'secondary'}
                size="lg"
                className="w-full mb-8"
                asChild
              >
                <Link to={plan.monthlyPrice ? '/login' : '/contact'}>
                  {plan.cta}
                </Link>
              </Button>

              {/* Features */}
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm text-apple-text-secondary">
                    <CheckIcon className="w-5 h-5 text-apple-green shrink-0 mt-0.5" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
