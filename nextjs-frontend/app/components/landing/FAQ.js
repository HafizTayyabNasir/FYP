'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AnimatedSection from './AnimatedSection';

const faqs = [
  {
    q: 'How does AI Client Hunt find businesses?',
    a: 'We use OpenStreetMap (OSM) data to discover real local businesses by type and location. This gives you verified, up-to-date business listings across 50+ countries — no scraping Google or buying lists required.',
  },
  {
    q: 'What contact information can it extract?',
    a: 'Our enrichment engine crawls business websites to find emails, phone numbers, social media profiles (LinkedIn, Facebook, Instagram, Twitter), and where available, decision-maker names and roles.',
  },
  {
    q: 'How accurate are the website audits?',
    a: 'Audits cover SEO, page speed, mobile responsiveness, and design quality. Scores are generated using real technical analysis — not estimates. This gives you concrete talking points for outreach.',
  },
  {
    q: 'Are the AI-generated emails actually personalized?',
    a: 'Yes. Each email is generated using real audit data and business context. The AI references specific website issues, the business type, and location to craft messages that feel individually researched.',
  },
  {
    q: 'Do I need technical skills to use this tool?',
    a: 'Not at all. The entire workflow runs from an intuitive dashboard. Enter a business type and city, click search, and the tool handles discovery, enrichment, auditing, and email generation automatically.',
  },
  {
    q: 'Is this tool suitable for agencies and teams?',
    a: 'Absolutely. AI Client Hunt is built for agencies, freelancers, and small sales teams. The campaign management system lets you organize leads and track outreach across multiple projects.',
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <section className="relative py-20 lg:py-28">
      <div className="relative z-10 mx-auto max-w-[800px] px-6 lg:px-8">
        {/* Section header */}
        <AnimatedSection variant="fadeUp" className="text-center mb-14">
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Frequently asked{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              questions
            </span>
          </h2>
        </AnimatedSection>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <AnimatedSection key={i} variant="fadeUp" delay={i * 0.06}>
              <div
                className={`rounded-2xl border transition-all duration-300 ${
                  openIndex === i
                    ? 'border-[#6D5DF6]/25 bg-[#6D5DF6]/[0.03] dark:bg-[#6D5DF6]/[0.03]'
                    : 'border-slate-200/80 dark:border-white/[0.05] bg-white dark:bg-white/[0.01] hover:bg-slate-50 dark:hover:bg-white/[0.02] shadow-sm dark:shadow-none'
                }`}
              >
                <button
                  onClick={() => setOpenIndex(openIndex === i ? null : i)}
                  className="flex items-center justify-between w-full px-6 py-5 text-left"
                >
                  <span className="text-sm font-semibold text-slate-900 dark:text-white pr-4">{faq.q}</span>
                  <div className="flex-shrink-0 text-lg font-bold text-[#6D5DF6]">
                    {openIndex === i ? '−' : '+'}
                  </div>
                </button>

                <AnimatePresence>
                  {openIndex === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-5">
                        <p className="text-sm text-slate-600 dark:text-[#8E8BA3] leading-relaxed">{faq.a}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>
  );
}
