'use client';

import AnimatedSection, { StaggerContainer, StaggerItem } from '../components/landing/AnimatedSection';

const posts = [
  {
    title: 'How to Audit Client Websites for Service Gaps',
    description: 'Learn how to analyze a prospect website speed, design flaws, and SEO checklist, then turn those findings into a winning pitch.',
    date: 'Jun 24, 2026',
    readTime: '5 min read',
    category: 'Website Audits',
  },
  {
    title: 'Cold Email Deliverability Checklist for Freelancers',
    description: 'Ensure your emails hit the inbox instead of spam. A checklist for setting up DNS, SPF, DKIM, and warming up outbound accounts.',
    date: 'Jun 18, 2026',
    readTime: '7 min read',
    category: 'Outreach',
  },
  {
    title: 'Why Self-Hosted Lead Databases Protect Your Sales Pipeline',
    description: 'Avoid paying recurring fees for static databases. Discover how running local crawler discovery maintains lead ownership and data privacy.',
    date: 'Jun 12, 2026',
    readTime: '6 min read',
    category: 'Lead Gen',
  },
];

export default function BlogPage() {
  return (
    <main className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300 min-h-screen py-20 lg:py-28">
      {/* Grid overlay */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] dark:opacity-[0.015]" style={{
        backgroundImage: 'linear-gradient(rgba(109,93,246,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(109,93,246,0.15) 1px, transparent 1px)',
        backgroundSize: '60px 60px',
      }} />

      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        {/* Header */}
        <AnimatedSection variant="fadeUp" className="max-w-3xl mb-16">
          <span className="text-xs font-semibold tracking-wider text-[#6D5DF6] dark:text-[#A78BFA] uppercase">
            Resources & Blog
          </span>
          <h1 className="mt-4 text-[clamp(2.2rem,5vw,3.5rem)] font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Outreach insights and{' '}
            <span className="text-[#6D5DF6] dark:text-[#A78BFA]">
              product updates
            </span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3] max-w-2xl">
            A resource hub for strategies on lead finding, technical auditing, and generating high-response cold emails.
          </p>
        </AnimatedSection>

        {/* Blog Post Cards */}
        <StaggerContainer staggerDelay={0.1} className="grid gap-8 md:grid-cols-3">
          {posts.map((post) => (
            <StaggerItem key={post.title} variant="fadeUp">
              <div className="group h-full rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015] p-6 shadow-sm dark:shadow-none hover:border-[#6D5DF6]/15 transition-all duration-300 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-2xs font-bold uppercase tracking-wider text-[#6D5DF6] dark:text-[#A78BFA] bg-[#6D5DF6]/10 dark:bg-[#6D5DF6]/15 px-2.5 py-1 rounded-md">
                      {post.category}
                    </span>
                    <span className="text-2xs text-slate-400 dark:text-[#6B6890]">{post.date}</span>
                  </div>

                  <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-3 group-hover:text-[#6D5DF6] dark:group-hover:text-[#A78BFA] transition-colors duration-250 leading-snug">
                    {post.title}
                  </h2>
                  
                  <p className="text-sm text-slate-500 dark:text-[#8E8BA3] leading-relaxed mb-6">
                    {post.description}
                  </p>
                </div>

                <div className="flex items-center justify-between mt-auto border-t border-slate-200/80 dark:border-white/[0.06] pt-4">
                  <span className="text-xs font-semibold text-slate-400 dark:text-[#6B6890]">{post.readTime}</span>
                  <span className="text-xs font-bold text-[#6D5DF6] dark:text-[#A78BFA] hover:underline cursor-pointer">
                    Read Article
                  </span>
                </div>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </main>
  );
}
