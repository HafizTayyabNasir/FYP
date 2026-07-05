'use client';

import Image from 'next/image';
import AnimatedSection from './AnimatedSection';

const showcaseItems = [
  {
    title: 'Discover Local Businesses',
    description: 'Find local leads by business type and location with addresses and website URLs.',
    image: '/images/product-dashboard.png',
    features: ['OSM-powered discovery', 'Real-time results', 'Multi-country support'],
    imagePosition: 'right',
  },
  {
    title: 'Audit Websites',
    description: 'Score websites on SEO, speed, and mobile responsiveness to identify areas of improvement.',
    image: '/images/website-audit.png',
    features: ['SEO & performance scoring', 'Improvement insights', 'Pitch suggestions'],
    imagePosition: 'left',
  },
  {
    title: 'Generate Outreach Emails',
    description: 'Draft cold emails automatically using audit results and lead details.',
    image: '/images/email-outreach.png',
    features: ['Context-aware personalization', 'Multi-template support', 'One-click generation'],
    imagePosition: 'right',
  },
];

export default function FeatureShowcase() {
  return (
    <section className="relative py-20 lg:py-28">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-20">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Features Showcase
          </h2>
        </AnimatedSection>

        {/* Alternating sections */}
        <div className="space-y-24 lg:space-y-32">
          {showcaseItems.map((item, i) => (
            <div
              key={item.title}
              className={`grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center ${
                item.imagePosition === 'left' ? 'lg:direction-rtl' : ''
              }`}
            >
              {/* Text content */}
              <AnimatedSection
                variant={item.imagePosition === 'left' ? 'fadeRight' : 'fadeLeft'}
                delay={0.1}
                className={item.imagePosition === 'left' ? 'lg:order-2 lg:direction-ltr' : 'lg:direction-ltr'}
              >
                <div className="max-w-[500px]">
                  <h3 className="text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-snug mb-5">
                    {item.title}
                  </h3>
                  <p className="text-slate-600 dark:text-[#8E8BA3] text-base leading-relaxed mb-8">
                    {item.description}
                  </p>
                  <div className="space-y-3">
                    {item.features.map((feat) => (
                      <div key={feat} className="flex items-center gap-3">
                        <span className="text-[#6D5DF6] dark:text-[#A78BFA] font-bold text-lg">&bull;</span>
                        <span className="text-sm font-medium text-slate-700 dark:text-[#C8C4E8]">{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </AnimatedSection>

              {/* Image */}
              <AnimatedSection
                variant={item.imagePosition === 'left' ? 'fadeLeft' : 'fadeRight'}
                delay={0.2}
                className={item.imagePosition === 'left' ? 'lg:order-1 lg:direction-ltr' : 'lg:direction-ltr'}
              >
                <div className="relative group">
                  <div className="relative rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-[0_30px_80px_rgba(0,0,0,0.4)] bg-white dark:bg-[#08061a]">
                    <Image
                      src={item.image}
                      alt={item.title}
                      width={640}
                      height={400}
                      className="w-full h-auto transition-transform duration-700 group-hover:scale-[1.02]"
                    />
                  </div>
                </div>
              </AnimatedSection>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
