'use client';

import Image from 'next/image';
import AnimatedSection, { StaggerContainer, StaggerItem } from './AnimatedSection';

const reasons = [
  {
    title: 'Fast',
    description: 'Search and discover local leads quickly.',
  },
  {
    title: 'Privacy First',
    description: 'We do not share your lead data.',
  },
  {
    title: 'Global',
    description: 'Discover businesses across the world.',
  },
  {
    title: 'Smart Outreach',
    description: 'Generate tailored cold outreach.',
  },
  {
    title: 'Unified',
    description: 'All prospect data in one location.',
  },
  {
    title: 'Effective',
    description: 'Deliver your messages directly to prospects.',
  },
];

export default function WhyChooseUs() {
  return (
    <section className="relative py-20 lg:py-28">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-20 items-start">
          {/* Left: Text + Image */}
          <AnimatedSection variant="fadeLeft" delay={0.1}>
            <h2 className="text-[clamp(1.8rem,4vw,2.6rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight mb-5">
              Stop wasting hours on{' '}
              <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
                manual prospecting
              </span>
            </h2>
            <p className="text-slate-600 dark:text-[#8E8BA3] text-base leading-relaxed mb-10 max-w-[460px]">
              Traditional lead generation means hours of Google searching, spreadsheet copying, and generic cold emails. We automate the entire pipeline.
            </p>

            <div className="relative rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-[0_20px_60px_rgba(0,0,0,0.4)] bg-white dark:bg-[#08061a] group">
              <Image
                src="/images/team-collaboration.png"
                alt="Marketing team collaborating"
                width={600}
                height={380}
                className="w-full h-auto transition-transform duration-700 group-hover:scale-[1.02]"
              />
            </div>
          </AnimatedSection>

          {/* Right: Feature cards */}
          <StaggerContainer staggerDelay={0.1} className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:pt-10">
            {reasons.map((reason) => (
              <StaggerItem key={reason.title} variant="fadeUp">
                <div className="group h-full rounded-2xl border border-slate-200/60 dark:border-white/[0.05] bg-white dark:bg-white/[0.015] shadow-sm dark:shadow-none p-5 transition-all duration-400">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2">{reason.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-[#7A7893] leading-relaxed">{reason.description}</p>
                </div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </div>
    </section>
  );
}
