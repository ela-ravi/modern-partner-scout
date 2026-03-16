import { useScrollReveal } from '@/hooks/useScrollReveal'
import { usePageMeta } from '@/hooks/usePageMeta'
import {
  HeroSection,
  HowItWorksSection,
  FeaturesSection,
  StatsSection,
  TestimonialsSection,
  PricingSection,
  CTASection,
} from '@/components/marketing'

export default function LandingPage() {
  const containerRef = useScrollReveal()

  usePageMeta({
    title: 'PartnerScout AI - AI-Powered Instagram Partner Discovery',
    description: 'AI-powered Instagram partner discovery for D2C brands. Discover, score, and connect with ideal collaborators in minutes.',
    keywords: 'Instagram partner discovery, AI marketing, D2C brand partnerships, influencer scoring, partner matching',
    canonical: '/',
  })

  return (
    <div ref={containerRef}>
      <HeroSection />
      <HowItWorksSection />
      <FeaturesSection />
      <StatsSection />
      <TestimonialsSection />
      <PricingSection />
      <CTASection />
    </div>
  )
}
