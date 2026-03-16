import { Link } from 'react-router-dom'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center gradient-mesh noise-overlay overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left copy */}
          <div className="max-w-xl">
            <div
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-primary/10 text-brand-primary text-sm font-medium mb-8"
              style={{ animation: 'fade-in 0.6s ease-out forwards' }}
            >
              <span className="w-2 h-2 rounded-full bg-apple-green animate-pulse" />
              AI-Powered Partner Discovery
            </div>

            <h1
              className="font-display text-5xl sm:text-6xl lg:text-7xl leading-[1.05] tracking-tight text-apple-text mb-6"
              style={{ animation: 'slide-up 0.8s cubic-bezier(0.16,1,0.3,1) forwards', animationDelay: '0.1s', opacity: 0 }}
            >
              Find your
              <br />
              <span className="text-gradient-brand">perfect partners</span>
            </h1>

            <p
              className="text-lg sm:text-xl text-apple-text-secondary leading-relaxed mb-10 max-w-md"
              style={{ animation: 'slide-up 0.8s cubic-bezier(0.16,1,0.3,1) forwards', animationDelay: '0.25s', opacity: 0 }}
            >
              Drop in a brand's Instagram handle. Our AI figures out who they are,
              finds similar profiles, scores each one, and pulls contact info. Done in minutes.
            </p>

            <div
              className="flex flex-wrap gap-4"
              style={{ animation: 'slide-up 0.8s cubic-bezier(0.16,1,0.3,1) forwards', animationDelay: '0.4s', opacity: 0 }}
            >
              <Link
                to="/login"
                className="group relative inline-flex items-center gap-2 px-8 py-4 rounded-2xl text-white font-semibold text-lg
                  bg-gradient-to-r from-brand-primary to-brand-accent
                  shadow-[0_8px_30px_rgba(0,122,255,0.35)]
                  hover:shadow-[0_12px_40px_rgba(0,122,255,0.5)]
                  hover:scale-[1.03] active:scale-[0.98]
                  transition-all duration-200 ease-out"
              >
                Get Started Free
                <ArrowForwardIcon className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
              </Link>
              <Link
                to="/docs"
                className="group relative inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold text-lg
                  text-apple-text bg-white
                  border-2 border-apple-border
                  shadow-[0_4px_20px_rgba(0,0,0,0.08)]
                  hover:border-brand-primary/40 hover:shadow-[0_8px_30px_rgba(0,122,255,0.15)]
                  hover:scale-[1.03] active:scale-[0.98]
                  transition-all duration-200 ease-out"
              >
                <PlayArrowIcon className="w-6 h-6 text-brand-primary transition-transform duration-200 group-hover:scale-110" />
                Watch Demo
              </Link>
            </div>
          </div>

          {/* Right product mockup */}
          <div
            className="relative hidden lg:block"
            style={{ animation: 'fade-in 1s ease-out forwards', animationDelay: '0.5s', opacity: 0, perspective: '1200px' }}
          >
            <div
              className="relative rounded-2xl overflow-hidden shadow-large border border-apple-border bg-white"
              style={{ animation: 'float 8s ease-in-out infinite' }}
            >
              {/* Mock dashboard card */}
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 rounded-full bg-apple-red" />
                  <div className="w-3 h-3 rounded-full bg-apple-orange" />
                  <div className="w-3 h-3 rounded-full bg-apple-green" />
                  <span className="ml-4 text-sm text-apple-text-tertiary">PartnerScout Dashboard</span>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: 'Discovered', value: '48', color: 'bg-brand-primary/10 text-brand-primary' },
                    { label: 'Scored', value: '32', color: 'bg-apple-green/10 text-apple-green' },
                    { label: 'Avg Score', value: '87', color: 'bg-brand-accent/10 text-brand-accent' },
                  ].map((stat) => (
                    <div key={stat.label} className={`${stat.color} rounded-xl p-3 text-center`}>
                      <div className="text-2xl font-bold">{stat.value}</div>
                      <div className="text-xs opacity-70">{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Profile rows */}
                {[
                  { name: 'StyleHouse Co.', score: 94, followers: '125K' },
                  { name: 'Urban Bloom', score: 91, followers: '89K' },
                  { name: 'The Daily Edit', score: 87, followers: '210K' },
                ].map((profile) => (
                  <div
                    key={profile.name}
                    className="flex items-center justify-between p-3 rounded-xl bg-apple-gray/50 border border-apple-border"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent" />
                      <div>
                        <div className="text-sm font-medium text-apple-text">{profile.name}</div>
                        <div className="text-xs text-apple-text-tertiary">{profile.followers} followers</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-apple-green">{profile.score}</span>
                      <div className="w-8 h-8 rounded-full border-2 border-apple-green flex items-center justify-center">
                        <svg className="w-4 h-4 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Decorative glow */}
            <div className="absolute -inset-4 bg-brand-primary/5 rounded-3xl -z-10 blur-xl" />
          </div>
        </div>
      </div>
    </section>
  )
}
