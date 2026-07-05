'use client';

import HeroSection from './components/landing/HeroSection';
import BentoGrid from './components/landing/BentoGrid';
import WorkflowTimeline from './components/landing/WorkflowTimeline';
import SocialProof from './components/landing/SocialProof';
import FeatureShowcase from './components/landing/FeatureShowcase';
import WhyChooseUs from './components/landing/WhyChooseUs';
import Testimonials from './components/landing/Testimonials';
import Statistics from './components/landing/Statistics';
import ProductScreenshots from './components/landing/ProductScreenshots';
import FAQ from './components/landing/FAQ';
import FinalCTA from './components/landing/FinalCTA';

export default function HomePage() {
  return (
    <main className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300">
      {/* Background layers */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {/* Subtle grid */}
        <div
          className="absolute inset-0 opacity-[0.04] dark:opacity-[0.025]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(139,124,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(139,124,246,0.3) 1px, transparent 1px)',
            backgroundSize: '80px 80px',
          }}
        />
        {/* Noise texture overlay */}
        <div className="absolute inset-0 opacity-[0.015]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.5'/%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Content */}
      <div className="relative z-10">
        <HeroSection />
        <SocialProof />
        <BentoGrid />
        <WorkflowTimeline />
        <FeatureShowcase />
        <WhyChooseUs />
        <Statistics />
        <Testimonials />
        <ProductScreenshots />
        <FAQ />
        <FinalCTA />
      </div>
    </main>
  );
}
