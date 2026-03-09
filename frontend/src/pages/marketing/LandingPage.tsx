import { useScrollReveal } from '@/hooks/useScrollReveal'
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
