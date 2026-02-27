import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

export function CTASection() {
  return (
    <section className="py-24 sm:py-32 relative overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand-primary via-purple-700 to-brand-dark" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,rgba(255,255,255,0.15),transparent)]" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <div className="reveal-section">
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl text-white tracking-tight mb-6">
            Ready to find your
            <br />
            next partners?
          </h2>

          <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto mb-10">
            PartnerScout uses AI to discover, score, and connect you with Instagram
            collaborators. Start a session and see results in minutes.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Button
              variant="secondary"
              size="lg"
              rightIcon={<ArrowForwardIcon className="w-5 h-5" />}
              className="bg-white text-brand-primary hover:bg-white/90"
              asChild
            >
              <Link to="/login">Get Started Free</Link>
            </Button>
            <Button
              variant="ghost"
              size="lg"
              className="text-white border border-white/30 hover:bg-white/10"
              asChild
            >
              <Link to="/contact">Talk to Sales</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
