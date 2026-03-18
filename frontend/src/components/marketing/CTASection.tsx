import { Link } from 'react-router-dom'
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
            <Link
              to="/login"
              className="group relative inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold text-lg
                text-brand-primary bg-white
                shadow-[0_8px_30px_rgba(255,255,255,0.3)]
                hover:shadow-[0_12px_40px_rgba(255,255,255,0.5)]
                hover:scale-[1.03] active:scale-[0.98]
                transition-all duration-200 ease-out"
            >
              Get Started Free
              <ArrowForwardIcon className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
            </Link>
            <Link
              to="/contact"
              className="group relative inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold text-lg
                text-white
                border-2 border-white/30
                shadow-[0_4px_20px_rgba(255,255,255,0.08)]
                hover:border-white/60 hover:shadow-[0_8px_30px_rgba(255,255,255,0.2)]
                hover:scale-[1.03] active:scale-[0.98]
                transition-all duration-200 ease-out"
            >
              Talk to Sales
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
