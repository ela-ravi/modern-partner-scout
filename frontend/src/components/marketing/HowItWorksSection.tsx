import SearchIcon from '@mui/icons-material/Search'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ScoreboardIcon from '@mui/icons-material/Scoreboard'
import EmailIcon from '@mui/icons-material/Email'

const steps = [
  {
    number: '01',
    title: 'Analyze',
    description: 'Paste any Instagram handle. The AI pulls apart what makes the brand tick: hashtags, keywords, visual style, audience vibe.',
    icon: <SearchIcon className="w-7 h-7" />,
    color: 'from-brand-primary to-purple-400',
  },
  {
    number: '02',
    title: 'Discover',
    description: 'AI agents go hunting on Instagram for profiles that match, filtering by engagement, follower count, and how well the content lines up.',
    icon: <AutoAwesomeIcon className="w-7 h-7" />,
    color: 'from-apple-purple to-purple-400',
  },
  {
    number: '03',
    title: 'Score',
    description: 'Every candidate gets a 0 to 100 score. You see exactly why: relevance, engagement, authenticity, reach. No black box.',
    icon: <ScoreboardIcon className="w-7 h-7" />,
    color: 'from-apple-green to-emerald-400',
  },
  {
    number: '04',
    title: 'Connect',
    description: 'Emails get pulled automatically. Write a personalized outreach message and start the conversation.',
    icon: <EmailIcon className="w-7 h-7" />,
    color: 'from-apple-orange to-amber-400',
  },
]

export function HowItWorksSection() {
  return (
    <section className="py-24 sm:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16 reveal-section">
          <p className="text-brand-primary font-semibold text-sm tracking-wide uppercase mb-3">
            How It Works
          </p>
          <h2 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight">
            From profile to partner in 4 steps
          </h2>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step) => (
            <div key={step.number} className="reveal-item group relative">
              {/* Connecting line (hidden on first item) */}
              <div className="hidden lg:block absolute top-10 left-[calc(50%+32px)] right-[calc(-50%+32px)] h-px bg-apple-border group-last:hidden" />

              <div className="text-center">
                {/* Icon circle */}
                <div className={`w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center text-white mb-6 shadow-lg group-hover:scale-105 transition-transform duration-300`}>
                  {step.icon}
                </div>

                {/* Step number */}
                <span className="text-xs font-bold text-apple-text-tertiary tracking-widest uppercase">
                  Step {step.number}
                </span>

                <h3 className="text-xl font-semibold text-apple-text mt-2 mb-3">
                  {step.title}
                </h3>

                <p className="text-sm text-apple-text-secondary leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
