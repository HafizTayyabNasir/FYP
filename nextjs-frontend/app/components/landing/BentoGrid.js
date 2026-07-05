'use client';

import Image from 'next/image';
import AnimatedSection, { StaggerContainer, StaggerItem } from './AnimatedSection';

const bentoItems = [
  {
    title: 'Business Discovery',
    description: 'Search by business type and location to find local leads.',
    image: '/images/product-dashboard.png',
    span: 'col-span-1 lg:col-span-2',
  },
  {
    title: 'Contact Enrichment',
    description: 'Extract emails, phone numbers, and social profiles from business websites.',
    image: null,
    span: 'col-span-1',
  },
  {
    title: 'Website Audits',
    description: 'Audit websites for speed, SEO, and responsiveness.',
    image: '/images/website-audit.png',
    span: 'col-span-1',
  },
  {
    title: 'AI Outreach Engine',
    description: 'Draft personalized emails using audit results and business data.',
    image: '/images/email-outreach.png',
    span: 'col-span-1 lg:col-span-2',
  },
];

export default function BentoGrid() {
  return (
    <section className="relative py-20 lg:py-28">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-16">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            One tool. Full-stack{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              lead generation
            </span>
          </h2>
          <p className="mt-5 text-slate-600 dark:text-[#7A7893] text-lg max-w-[560px] mx-auto leading-relaxed">
            From discovery to personalized email inside a single workflow.
          </p>
        </AnimatedSection>

        {/* Bento grid */}
        <StaggerContainer staggerDelay={0.12} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {bentoItems.map((item, i) => (
            <StaggerItem key={item.title} className={item.span}>
              <div className="group relative h-full rounded-2xl border border-slate-200/60 dark:border-white/[0.06] bg-white dark:bg-[#0c0a1e]/60 shadow-sm dark:shadow-none backdrop-blur-sm overflow-hidden transition-all duration-500 hover:border-[#6D5DF6]/25 dark:hover:border-[#6D5DF6]/25">
                {/* Content */}
                <div className="p-7">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2.5">{item.title}</h3>
                  <p className="text-slate-600 dark:text-[#7A7893] text-sm leading-relaxed">{item.description}</p>
                </div>

                {/* Screenshot preview */}
                {item.image && (
                  <div className="px-5 pb-5">
                    <div className="relative rounded-xl overflow-hidden border border-slate-100 dark:border-white/[0.04] shadow-lg">
                      <Image
                        src={item.image}
                        alt={`${item.title} preview`}
                        width={600}
                        height={340}
                        className="w-full h-auto transition-transform duration-700 group-hover:scale-[1.02]"
                      />
                    </div>
                  </div>
                )}
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  );
}
