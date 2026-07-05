'use client';

import AnimatedSection, { StaggerContainer, StaggerItem } from './AnimatedSection';
import { useInView } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';

const statItems = [
  { value: 3000, suffix: '+', label: 'Leads Per Search', prefix: '' },
  { value: 92, suffix: '%', label: 'Email Delivery Rate', prefix: '' },
  { value: 50, suffix: '+', label: 'Countries Covered', prefix: '' },
  { value: 10, suffix: 'x', label: 'Faster Than Manual', prefix: '' },
];

function AnimatedCounter({ value, suffix = '', prefix = '', duration = 2000 }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const step = Math.ceil(value / (duration / 30));
    const timer = setInterval(() => {
      start += step;
      if (start >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, 30);
    return () => clearInterval(timer);
  }, [isInView, value, duration]);

  return (
    <span ref={ref}>
      {prefix}{count.toLocaleString()}{suffix}
    </span>
  );
}

export default function Statistics() {
  return (
    <section className="relative py-20 lg:py-24">
      <div className="relative z-10 mx-auto max-w-[1280px] px-6 lg:px-8">
        <div className="relative rounded-3xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-[#0c0a1e]/60 shadow-sm dark:shadow-none overflow-hidden transition-colors duration-300">
          <div className="relative z-10 px-8 py-16 lg:py-20">
            <StaggerContainer staggerDelay={0.12} className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
              {statItems.map((item) => (
                <StaggerItem key={item.label} variant="scale">
                  <div className="text-center">
                    <div className="text-4xl lg:text-5xl font-extrabold text-[#6D5DF6] dark:text-[#A78BFA] mb-3">
                      <AnimatedCounter value={item.value} suffix={item.suffix} prefix={item.prefix} />
                    </div>
                    <div className="text-xs font-semibold tracking-wider text-slate-500 dark:text-[#6B6890] uppercase">
                      {item.label}
                    </div>
                  </div>
                </StaggerItem>
              ))}
            </StaggerContainer>
          </div>
        </div>
      </div>
    </section>
  );
}
