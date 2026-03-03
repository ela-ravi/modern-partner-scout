import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
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
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const containerRef = useScrollReveal()

  // Redirect authenticated users to the app — but never block rendering
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate('/sessions', { replace: true })
    }
  }, [isAuthenticated, isLoading, navigate])

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
