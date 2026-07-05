'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import AnimatedSection, { FloatingElement } from './AnimatedSection';

const stats = [
  { value: '10x', label: 'Faster Prospecting' },
  { value: '3K+', label: 'Leads Per Search' },
  { value: '92%', label: 'Email Delivery Rate' },
  { value: '50+', label: 'Countries Covered' },
];

export default function HeroSection() {
  return (
    <section className="relative min-h-[calc(100vh-80px)] flex items-center overflow-hidden">
      {/* Background glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-[#6D5DF6]/[0.02] dark:bg-[#6D5DF6]/[0.04] blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-15%] right-[-8%] w-[500px] h-[500px] rounded-full bg-[#A855F7]/[0.015] dark:bg-[#A855F7]/[0.03] blur-[100px] pointer-events-none" />

      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8 py-20 lg:py-0 w-full">
        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-16 lg:gap-20 items-center">
          {/* Left: Content */}
          <div>
            <AnimatedSection variant="fadeUp" delay={0.1}>
              <h1 className="text-[clamp(2.4rem,5.5vw,4.2rem)] font-extrabold leading-[1.08] tracking-tight text-slate-900 dark:text-white">
                Find clients. Audit their sites. Close with outreach.
              </h1>
            </AnimatedSection>

            <AnimatedSection variant="fadeUp" delay={0.2}>
              <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3] max-w-[500px]">
                A platform for agencies and freelancers to discover local businesses,
                extract contact details, and run website audits.
              </p>
            </AnimatedSection>

            <AnimatedSection variant="fadeUp" delay={0.3}>
              <div className="flex flex-wrap items-center gap-4 mt-10">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center rounded-2xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-7 py-3.5 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5"
                >
                  Start Hunting Clients
                </Link>
                <Link
                  href="/about"
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white/60 dark:bg-white/[0.03] px-7 py-3.5 text-sm font-semibold text-slate-700 dark:text-[#C8C4E8] backdrop-blur-sm transition-all duration-300 hover:bg-slate-50 dark:hover:bg-white/[0.06] hover:border-slate-300 dark:hover:border-white/[0.15]"
                >
                  See How It Works
                </Link>
              </div>
            </AnimatedSection>

            <AnimatedSection variant="fadeUp" delay={0.45}>
              <div className="flex flex-wrap gap-8 mt-14 pt-8 border-t border-slate-200/80 dark:border-white/[0.06]">
                {stats.map((item, i) => (
                  <div key={item.label}>
                    <div className="text-2xl font-extrabold text-[#6D5DF6] dark:text-[#A78BFA]">
                      {item.value}
                    </div>
                    <div className="text-[11px] font-medium tracking-wider text-slate-400 dark:text-[#5C5A7A] uppercase mt-1">
                      {item.label}
                    </div>
                  </div>
                ))}
              </div>
            </AnimatedSection>
          </div>

          {/* Right: Product Mockup */}
          <AnimatedSection variant="scale" delay={0.3} className="relative">
            <div className="relative">
              {/* Main dashboard preview */}
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-white/[0.08] shadow-[0_20px_50px_rgba(0,0,0,0.06)] dark:shadow-[0_40px_100px_rgba(0,0,0,0.5)] bg-white dark:bg-[#08061a]">
                <Image
                  src="/images/product-dashboard.png"
                  alt="AI Client Hunt Dashboard"
                  width={680}
                  height={460}
                  className="w-full h-auto"
                  priority
                />
              </div>
            </div>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}
