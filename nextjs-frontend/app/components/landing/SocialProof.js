'use client';

import AnimatedSection, { StaggerContainer, StaggerItem } from './AnimatedSection';

const audiences = [
  { label: 'Agencies' },
  { label: 'Freelancers' },
  { label: 'Growth Teams' },
  { label: 'Digital Marketers' },
  { label: 'Sales Teams' },
  { label: 'Consultants' },
];

const logos = [
  'TechAgency', 'GrowthLabs', 'PixelCraft', 'SalesForge',
  'LeadGen Pro', 'OutreachHQ', 'ClientFlow', 'ProspectAI',
];

export default function SocialProof() {
  return (
    <section className="relative py-20 lg:py-28 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        <AnimatedSection variant="fadeUp" className="text-center">
          <h2 className="text-[clamp(1.6rem,3.5vw,2.4rem)] font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
            Trusted by teams who close deals
          </h2>
          <p className="text-slate-600 dark:text-[#7A7893] text-base max-w-[440px] mx-auto leading-relaxed mb-12">
            Join hundreds of professionals already using AI Client Hunt to build qualified pipelines.
          </p>
        </AnimatedSection>

        {/* Audience pills */}
        <StaggerContainer staggerDelay={0.08} className="flex flex-wrap items-center justify-center gap-3 mb-16">
          {audiences.map((aud) => (
            <StaggerItem key={aud.label} variant="scale">
              <div className="flex items-center gap-2.5 rounded-full border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.02] px-5 py-2.5 shadow-sm dark:shadow-none backdrop-blur-sm transition-all duration-300">
                <span className="text-sm font-semibold text-slate-700 dark:text-[#C8C4E8]">{aud.label}</span>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>

        {/* Logo strip */}
        <AnimatedSection variant="fadeUp" delay={0.3}>
          <div className="relative">
            <div className="flex items-center justify-center gap-8 lg:gap-14 overflow-hidden py-6">
              {logos.map((name) => (
                <div
                  key={name}
                  className="flex-shrink-0 text-sm font-bold tracking-wider text-slate-400 dark:text-[#3A3856] uppercase select-none transition-colors duration-300 hover:text-[#6D5DF6]/50"
                >
                  {name}
                </div>
              ))}
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
