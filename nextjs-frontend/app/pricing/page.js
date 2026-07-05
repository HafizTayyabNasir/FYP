'use client';

import Link from 'next/link';
import AnimatedSection, { StaggerContainer, StaggerItem } from '../components/landing/AnimatedSection';

const plans = [
  {
    name: 'Starter',
    price: '$0',
    description: 'For FYP demos and manual testing',
    features: ['Lead discovery', 'Website audit', 'Email finder', 'Local data storage'],
    isPopular: false,
  },
  {
    name: 'Pro',
    price: '$19',
    description: 'For freelancers and small agencies',
    features: ['Everything in Starter', 'Campaign management', 'Inbox workflow', 'AI outreach generation'],
    isPopular: true,
  },
  {
    name: 'Agency',
    price: '$49',
    description: 'For teams running repeat outreach',
    features: ['Everything in Pro', 'Higher usage limits', 'Team-ready workflow', 'Priority support'],
    isPopular: false,
  },
];

export default function PricingPage() {
  return (
    <main className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300 min-h-screen py-20 lg:py-28">
      {/* Grid overlay */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] dark:opacity-[0.015]" style={{
        backgroundImage: 'linear-gradient(rgba(109,93,246,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(109,93,246,0.15) 1px, transparent 1px)',
        backgroundSize: '60px 60px',
      }} />

      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Header */}
        <AnimatedSection variant="fadeUp" className="max-w-3xl mb-16 text-center mx-auto">
          <span className="text-xs font-semibold tracking-wider text-[#6D5DF6] dark:text-[#A78BFA] uppercase">
            Pricing
          </span>
          <h1 className="mt-4 text-[clamp(2.2rem,5vw,3.5rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Simple plans for turning{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              leads into conversations
            </span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3] max-w-2xl mx-auto">
            Get started for free to test lead finding and outreach. Upgrade as you scale your business.
          </p>
        </AnimatedSection>

        {/* Pricing Cards */}
        <StaggerContainer staggerDelay={0.12} className="grid gap-8 lg:grid-cols-3 max-w-[1080px] mx-auto">
          {plans.map((plan) => (
            <StaggerItem key={plan.name} variant="fadeUp">
              <div
                className={`group relative h-full rounded-3xl border p-8 shadow-sm dark:shadow-none transition-all duration-300 flex flex-col justify-between ${
                  plan.isPopular
                    ? 'border-[#6D5DF6] dark:border-[#A78BFA] bg-white dark:bg-[#0c0a1e] scale-[1.02] lg:scale-[1.03] z-10'
                    : 'border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.015] hover:border-[#6D5DF6]/20'
                }`}
              >
                {plan.isPopular && (
                  <span className="absolute -top-3 right-6 rounded-full bg-[#6D5DF6] px-3 py-1 text-2xs font-extrabold text-white uppercase tracking-wider">
                    Popular
                  </span>
                )}
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{plan.name}</h2>
                  <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-6 min-h-[40px]">{plan.description}</p>
                  
                  <div className="flex items-end gap-2 mb-8">
                    <span className="text-4xl font-extrabold text-slate-900 dark:text-white">{plan.price}</span>
                    <span className="pb-1 text-sm font-semibold text-slate-400 dark:text-[#6B6890]">/ month</span>
                  </div>

                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feat) => (
                      <li key={feat} className="flex items-start gap-3 text-sm text-slate-600 dark:text-[#C8C4E8]">
                        <span className="text-[#6D5DF6] dark:text-[#A78BFA] font-bold text-base leading-none">&bull;</span>
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Link
                  href="/login"
                  className={`mt-auto block w-full rounded-2xl py-4 text-center text-sm font-bold transition-all duration-300 ${
                    plan.isPopular
                      ? 'bg-[#6D5DF6] hover:bg-[#5b4ee4] text-white shadow-sm'
                      : 'border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] text-slate-700 dark:text-[#C8C4E8] hover:bg-slate-100 dark:hover:bg-white/[0.06]'
                  }`}
                >
                  Get Started
                </Link>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </main>
  );
}
