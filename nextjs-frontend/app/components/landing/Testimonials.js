'use client';

import Image from 'next/image';
import AnimatedSection, { StaggerContainer, StaggerItem } from './AnimatedSection';

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Founder, GrowthLabs Agency',
    avatar: '/images/team-collaboration.png',
    content: 'AI Client Hunt cut our lead research time from 6 hours to 20 minutes per batch. The website audits give us incredible pitch angles that our competitors simply don\'t have.',
    rating: 5,
  },
  {
    name: 'Marcus Rodriguez',
    role: 'Freelance Web Developer',
    avatar: '/images/freelancer-working.png',
    content: 'I used to spend entire weekends finding potential clients. Now I generate a full pipeline of qualified leads before my morning coffee is done. Game changer for solo freelancers.',
    rating: 5,
  },
  {
    name: 'Priya Sharma',
    role: 'Head of Sales, TechForge',
    avatar: '/images/business-meeting.png',
    content: 'The personalized emails this tool generates are genuinely impressive. Our response rates jumped from 3% to 18% because every email references real website issues we can fix.',
    rating: 5,
  },
];

export default function Testimonials() {
  return (
    <section className="relative py-20 lg:py-28 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-16">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Loved by{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              real teams
            </span>
          </h2>
          <p className="mt-5 text-slate-600 dark:text-[#7A7893] text-lg max-w-[480px] mx-auto leading-relaxed">
            See how agencies, freelancers, and sales teams transformed their outreach.
          </p>
        </AnimatedSection>

        <StaggerContainer staggerDelay={0.15} className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((item) => (
            <StaggerItem key={item.name} variant="fadeUp">
              <div className="group h-full rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015] shadow-sm dark:shadow-none p-7 transition-all duration-400">
                {/* Quote */}
                <p className="text-slate-600 dark:text-[#B5B3CC] text-sm leading-relaxed mb-7">&ldquo;{item.content}&rdquo;</p>

                {/* Author */}
                <div className="flex items-center gap-3">
                  <div className="relative w-10 h-10 rounded-full overflow-hidden border border-slate-200 dark:border-white/[0.08]">
                    <Image
                      src={item.avatar}
                      alt={item.name}
                      width={40}
                      height={40}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900 dark:text-white">{item.name}</div>
                    <div className="text-xs text-slate-400 dark:text-[#6B6890]">{item.role}</div>
                  </div>
                </div>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  );
}
