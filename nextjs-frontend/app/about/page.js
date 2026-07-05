'use client';

import AnimatedSection, { StaggerContainer, StaggerItem } from '../components/landing/AnimatedSection';

export default function AboutPage() {
  return (
    <main className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300 min-h-screen py-20 lg:py-28">
      {/* Subtle Grid overlay */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] dark:opacity-[0.015]" style={{
        backgroundImage: 'linear-gradient(rgba(109,93,246,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(109,93,246,0.15) 1px, transparent 1px)',
        backgroundSize: '60px 60px',
      }} />

      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Hero header */}
        <AnimatedSection variant="fadeUp" className="max-w-3xl mb-16">
          <span className="text-xs font-semibold tracking-wider text-[#6D5DF6] dark:text-[#A78BFA] uppercase">
            About The Project
          </span>
          <h1 className="mt-4 text-[clamp(2.2rem,5vw,3.5rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Built to make lead hunting{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              faster & smarter
            </span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3] max-w-2xl">
            AI Client Hunt & Outreach is a sales platform designed to simplify business discovery, contact extraction, and audit-driven personalization.
          </p>
        </AnimatedSection>

        {/* Pillars Grid */}
        <StaggerContainer staggerDelay={0.12} className="grid gap-6 md:grid-cols-3 mb-24">
          {[
            ['The Problem', 'Manual prospecting requires switching between search tools, site crawlers, SEO checkers, and email editors, wasting hours daily.'],
            ['The Solution', 'A single pipeline that searches local businesses, enriches contact details, audits sites for flaws, and generates warm emails.'],
            ['The Outcome', 'Approach prospects with specific, helpful details about their business performance, raising reply rates and saving time.'],
          ].map(([title, text]) => (
            <StaggerItem key={title} variant="fadeUp">
              <div className="group h-full rounded-2xl border border-slate-200/60 dark:border-white/[0.05] bg-white dark:bg-white/[0.015] p-8 shadow-sm dark:shadow-none hover:border-[#6D5DF6]/15 transition-all duration-300">
                <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">{title}</h2>
                <p className="text-sm leading-relaxed text-slate-600 dark:text-[#8E8BA3]">{text}</p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>

        {/* Workflow overview */}
        <AnimatedSection variant="fadeUp" className="border-t border-slate-200/80 dark:border-white/[0.06] pt-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white mb-6">
                Our core objectives
              </h2>
              <p className="text-slate-600 dark:text-[#8E8BA3] text-sm leading-relaxed mb-6">
                We believe that outbound outreach does not need to feel spammy. By automating technical analysis and incorporating it into drafts, you create meaningful connections with potential clients.
              </p>
              <div className="space-y-4">
                {[
                  'Accurate local search using open OSM mapping.',
                  'In-depth audits covering SEO speed, design, and mobile scaling.',
                  'Dynamic email blueprints tailored to real weaknesses.',
                ].map((item) => (
                  <div key={item} className="flex items-center gap-3">
                    <span className="text-[#6D5DF6] dark:text-[#A78BFA] font-bold text-lg">&bull;</span>
                    <span className="text-sm font-medium text-slate-700 dark:text-[#C8C4E8]">{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="p-8 rounded-2xl border border-slate-200/60 dark:border-white/[0.05] bg-white dark:bg-[#0c0a1e]/40 shadow-sm dark:shadow-none">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Project Overview</h3>
              <div className="space-y-4 text-sm text-slate-600 dark:text-[#8E8BA3] leading-relaxed">
                <div>
                  <span className="font-semibold text-slate-900 dark:text-white">Developer:</span> AI Client Hunt
                </div>
                <div>
                  <span className="font-semibold text-slate-900 dark:text-white">Focus:</span> Lead discovery, audits, and outreach
                </div>
                <div>
                  <span className="font-semibold text-slate-900 dark:text-white">Type:</span> SaaS Platform
                </div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </main>
  );
}
