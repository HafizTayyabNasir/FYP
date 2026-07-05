'use client';

import AnimatedSection from '../components/landing/AnimatedSection';

export default function ContactPage() {
  return (
    <main className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300 min-h-screen py-20 lg:py-28">
      {/* Grid overlay */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] dark:opacity-[0.015]" style={{
        backgroundImage: 'linear-gradient(rgba(109,93,246,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(109,93,246,0.15) 1px, transparent 1px)',
        backgroundSize: '60px 60px',
      }} />

      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-[0.9fr_1.1fr] gap-12 lg:gap-20 items-start">
          
          {/* Left Column: Info */}
          <AnimatedSection variant="fadeLeft">
            <span className="text-xs font-semibold tracking-wider text-[#6D5DF6] dark:text-[#A78BFA] uppercase">
              Get in touch
            </span>
            <h1 className="mt-4 text-[clamp(2.2rem,5vw,3.5rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
              Have questions?{' '}
              <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
                We are here to help
              </span>
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3] max-w-md">
              Whether you are an evaluator checking the demo or interested in details about our scraping and lead generation pipelines, we would love to hear from you.
            </p>

            <div className="mt-10 rounded-3xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.015] p-8 max-w-md shadow-sm dark:shadow-none">
              <span className="text-xs font-semibold tracking-wider text-slate-400 dark:text-[#6B6890] uppercase block mb-2">
                Project Owner
              </span>
              <p className="font-extrabold text-lg text-slate-900 dark:text-white">Elvion Solutions</p>
              
              <div className="mt-6 border-t border-slate-200/80 dark:border-white/[0.06] pt-4">
                <span className="text-xs font-semibold tracking-wider text-slate-400 dark:text-[#6B6890] uppercase block mb-1">
                  Support Email
                </span>
                <p className="font-medium text-slate-700 dark:text-[#C8C4E8]">support@elvionsolutions.com</p>
              </div>
            </div>
          </AnimatedSection>

          {/* Right Column: Form */}
          <AnimatedSection variant="fadeRight">
            <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-[#0c0a1e]/40 p-8 lg:p-10 shadow-sm dark:shadow-none">
              <form className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <label className="block">
                    <span className="mb-2 block text-sm font-semibold text-slate-700 dark:text-white">Name</span>
                    <input
                      type="text"
                      className="w-full rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0c0a1e] px-4 py-3.5 text-sm text-slate-900 dark:text-white outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors duration-250"
                      placeholder="Your name"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm font-semibold text-slate-700 dark:text-white">Email</span>
                    <input
                      type="email"
                      className="w-full rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0c0a1e] px-4 py-3.5 text-sm text-slate-900 dark:text-white outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors duration-250"
                      placeholder="you@example.com"
                    />
                  </label>
                </div>
                
                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-slate-700 dark:text-white">Message</span>
                  <textarea
                    rows="5"
                    className="w-full rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0c0a1e] px-4 py-3.5 text-sm text-slate-900 dark:text-white outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors duration-250 resize-none"
                    placeholder="Write your message here..."
                  />
                </label>

                <button
                  type="button"
                  className="w-full rounded-2xl bg-[#6D5DF6] hover:bg-[#5b4ee4] py-4 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5"
                >
                  Send Message
                </button>
              </form>
            </div>
          </AnimatedSection>

        </div>
      </div>
    </main>
  );
}
