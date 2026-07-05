'use client';

import Image from 'next/image';
import AnimatedSection from './AnimatedSection';

const screenshots = [
  { src: '/images/product-dashboard.png', label: 'Business Discovery Dashboard', caption: 'Search and discover businesses by type and location' },
  { src: '/images/website-audit.png', label: 'Website Audit Report', caption: 'Comprehensive audit scoring with actionable insights' },
  { src: '/images/email-outreach.png', label: 'AI Email Generation', caption: 'Personalized outreach powered by real audit data' },
];

export default function ProductScreenshots() {
  return (
    <section className="relative py-20 lg:py-28 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-16">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Designed for{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              real workflows
            </span>
          </h2>
          <p className="mt-5 text-slate-600 dark:text-[#7A7893] text-lg max-w-[500px] mx-auto leading-relaxed">
            Clean, intuitive interfaces that make lead generation feel effortless.
          </p>
        </AnimatedSection>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {screenshots.map((item, i) => (
            <AnimatedSection key={item.label} variant="fadeUp" delay={i * 0.15}>
              <div className="group">
                <div className="relative rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-[0_20px_60px_rgba(0,0,0,0.35)] bg-white dark:bg-[#08061a] mb-5 transition-all duration-500">
                  <Image
                    src={item.src}
                    alt={item.label}
                    width={500}
                    height={320}
                    className="w-full h-auto transition-transform duration-700 group-hover:scale-[1.03]"
                  />
                </div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">{item.label}</h3>
                <p className="text-sm text-slate-500 dark:text-[#7A7893]">{item.caption}</p>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>
  );
}
