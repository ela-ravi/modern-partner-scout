import SpaIcon from '@mui/icons-material/Spa'
import CheckroomIcon from '@mui/icons-material/Checkroom'
import RestaurantIcon from '@mui/icons-material/Restaurant'

const useCases = [
  {
    title: 'Beauty Brand Partnerships',
    description:
      'Find skincare, cosmetics, and wellness creators whose audiences match your brand. Surface micro-influencers with high engagement that manual searches miss.',
    tagline: 'Skincare, cosmetics, wellness',
    icon: <SpaIcon className="w-7 h-7" />,
    gradient: 'from-brand-primary to-purple-400',
  },
  {
    title: 'Fashion Collab Discovery',
    description:
      'Discover apparel, streetwear, and luxury fashion profiles aligned with your aesthetic. Score them on content quality, audience overlap, and brand fit.',
    tagline: 'Apparel, streetwear, luxury',
    icon: <CheckroomIcon className="w-7 h-7" />,
    gradient: 'from-brand-accent to-amber-400',
  },
  {
    title: 'Food & Beverage Outreach',
    description:
      'Identify food, drink, and nutrition creators who resonate with your products. Pull their contact info and start building partnerships the same day.',
    tagline: 'Food, drink, nutrition',
    icon: <RestaurantIcon className="w-7 h-7" />,
    gradient: 'from-purple-500 to-brand-primary',
  },
]

export function TestimonialsSection() {
  return (
    <section className="py-24 sm:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16 reveal-section">
          <p className="text-brand-primary font-semibold text-sm tracking-wide uppercase mb-3">
            Use Cases
          </p>
          <h2 className="font-display text-4xl sm:text-5xl text-apple-text tracking-tight">
            How brands will use PartnerScout
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {useCases.map((uc) => (
            <div
              key={uc.title}
              className="reveal-item group relative rounded-2xl border border-apple-border bg-white p-6 sm:p-8 transition-all duration-300 hover:shadow-medium hover:-translate-y-1"
            >
              {/* Icon */}
              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${uc.gradient} flex items-center justify-center text-white mb-6 shadow-lg group-hover:scale-105 transition-transform duration-300`}>
                {uc.icon}
              </div>

              <h3 className="text-lg font-semibold text-apple-text mb-3">
                {uc.title}
              </h3>

              <p className="text-sm text-apple-text-secondary leading-relaxed mb-6">
                {uc.description}
              </p>

              {/* Tagline badge */}
              <span className="inline-block px-3 py-1 rounded-full bg-brand-primary/10 text-brand-primary text-xs font-medium">
                {uc.tagline}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
