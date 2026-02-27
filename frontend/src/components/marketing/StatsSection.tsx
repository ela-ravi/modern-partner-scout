import { useAnimatedCounter } from '@/hooks/useAnimatedCounter'

const stats = [
  { end: 200, suffix: '+', label: 'Profiles per Session', sublabel: 'Analyzed and scored' },
  { end: 6, suffix: '', label: 'Scoring Dimensions', sublabel: 'Transparent AI reasoning' },
  { end: 5, suffix: ' min', label: 'Average Session', sublabel: 'Start to results' },
  { end: 3, suffix: '', label: 'AI Agents', sublabel: 'Analyze, discover, score' },
]

function StatItem({ end, suffix, label, sublabel }: typeof stats[number]) {
  const { ref, display } = useAnimatedCounter(end, 2000, '', suffix)

  return (
    <div className="reveal-item text-center">
      <span
        ref={ref}
        className="block text-5xl sm:text-6xl font-bold text-white mb-2 tracking-tight"
      >
        {display}
      </span>
      <span className="block text-white font-medium mb-1">{label}</span>
      <span className="block text-sm text-white/50">{sublabel}</span>
    </div>
  )
}

export function StatsSection() {
  return (
    <section className="py-24 sm:py-32 bg-[#1A0533] relative overflow-hidden noise-overlay">
      {/* Subtle gradient accents */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-brand-accent/10 rounded-full blur-3xl" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16 reveal-section">
          <p className="text-brand-accent font-semibold text-sm tracking-wide uppercase mb-3">
            Platform Capabilities
          </p>
          <h2 className="font-display text-4xl sm:text-5xl text-white tracking-tight">
            Built for Scale
          </h2>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 sm:gap-12">
          {stats.map((stat) => (
            <StatItem key={stat.label} {...stat} />
          ))}
        </div>
      </div>
    </section>
  )
}
