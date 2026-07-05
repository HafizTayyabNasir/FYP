'use client';

import Link from 'next/link';
import AnimatedSection from './AnimatedSection';

export default function FinalCTA() {
  return (
    <section className="relative py-20 lg:py-28 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-[800px] px-6 lg:px-8 text-center">
        <AnimatedSection variant="scale" delay={0}>
          <div className="relative rounded-3xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-[#0c0a1e]/60 shadow-sm dark:shadow-none overflow-hidden transition-colors duration-300">
            <div className="relative z-10 px-8 py-16 lg:px-16 lg:py-24">
              <h2 className="text-[clamp(1.8rem,4.5vw,3rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight mb-5">
                Ready to start hunting{' '}
                <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
                  better clients
                </span>?
              </h2>

              <p className="text-slate-600 dark:text-[#8E8BA3] text-lg max-w-[480px] mx-auto leading-relaxed mb-10">
                Discover local businesses, find contact details, and start outreach.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-4">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center rounded-2xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-8 py-4 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5"
                >
                  Get Started Free
                </Link>
                <Link
                  href="/contact"
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.03] px-8 py-4 text-sm font-semibold text-slate-700 dark:text-[#C8C4E8] backdrop-blur-sm transition-all duration-300 hover:bg-slate-100 dark:hover:bg-white/[0.06] hover:border-slate-300 dark:hover:border-white/[0.15]"
                >
                  Talk to Us
                </Link>
              </div>

              <p className="mt-8 text-xs text-slate-400 dark:text-[#5C5A7A]">No credit card required</p>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
