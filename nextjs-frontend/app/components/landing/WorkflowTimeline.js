'use client';

import Image from 'next/image';
import AnimatedSection from './AnimatedSection';

const steps = [
  {
    num: '01',
    title: 'Search Businesses',
    description: 'Enter business type and city to find local leads.',
    image: '/images/product-dashboard.png',
    color: '#6D5DF6',
  },
  {
    num: '02',
    title: 'Extract Contacts',
    description: 'Extract email addresses, phone numbers, and social profiles.',
    image: '/images/freelancer-working.png',
    color: '#8B5CF6',
  },
  {
    num: '03',
    title: 'Website Audit',
    description: 'Analyze site speed, SEO, design, and mobile friendliness.',
    image: '/images/website-audit.png',
    color: '#A855F7',
  },
  {
    num: '04',
    title: 'Personalized Outreach',
    description: 'Generate email drafts based on audit results.',
    image: '/images/email-outreach.png',
    color: '#7C3AED',
  },
];

export default function WorkflowTimeline() {
  return (
    <section className="relative py-20 lg:py-28 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-20">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            From search to outreach in{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              minutes
            </span>
          </h2>
          <p className="mt-5 text-slate-600 dark:text-[#7A7893] text-lg max-w-[500px] mx-auto leading-relaxed">
            A pipeline that turns cold data into warm conversations.
          </p>
        </AnimatedSection>

        {/* Timeline */}
        <div className="relative">
          {/* Connecting line - desktop */}
          <div className="hidden lg:block absolute top-[60px] left-0 right-0 h-[2px]">
            <div className="w-full h-full bg-slate-200 dark:bg-white/[0.08] rounded-full" />
          </div>

          {/* Connecting line - mobile */}
          <div className="lg:hidden absolute top-0 bottom-0 left-[28px] w-[2px]">
            <div className="w-full h-full bg-slate-200 dark:bg-white/[0.08] rounded-full" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 lg:gap-5">
            {steps.map((step, i) => (
              <AnimatedSection key={step.num} variant="fadeUp" delay={i * 0.15}>
                <div className="relative pl-16 lg:pl-0">
                  {/* Step number circle */}
                  <div className="absolute left-0 top-0 lg:relative lg:left-auto lg:top-auto flex items-center justify-center w-14 h-14 lg:mx-auto lg:mb-8 rounded-2xl border-2 border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0c0a1e] z-10 transition-colors duration-300"
                    style={{ borderColor: `${step.color}30` }}
                  >
                    <span className="text-sm font-extrabold" style={{ color: step.color }}>{step.num}</span>
                  </div>

                  {/* Content */}
                  <div className="lg:text-center">
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">{step.title}</h3>
                    <p className="text-slate-600 dark:text-[#7A7893] text-sm leading-relaxed mb-5">{step.description}</p>
                  </div>

                  {/* Step image */}
                  <div className="relative rounded-xl overflow-hidden border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-[0_10px_40px_rgba(0,0,0,0.3)] bg-white dark:bg-[#08061a] group">
                    <Image
                       src={step.image}
                       alt={step.title}
                       width={400}
                       height={240}
                       className="w-full h-auto transition-transform duration-700 group-hover:scale-[1.03]"
                    />
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
