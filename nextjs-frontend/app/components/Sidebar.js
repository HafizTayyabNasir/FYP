'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  {
    label: 'Main Menu',
    items: [
      { href: '/dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { href: '/businesses', label: 'Leads / Hunt', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
      { href: '/audits', label: 'Website Audits', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
      { href: '/outreach', label: 'Email Generator', icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
      { href: '/inbox', label: 'Inbox', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
    ],
  },
  {
    label: 'System',
    items: [
      { href: '/settings', label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', icon2: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    ],
  },
];

export default function Sidebar({ open }) {
  const pathname = usePathname();

  const isActive = (href) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    if (href === '/settings') return pathname === '/settings';
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={`sticky top-[72px] h-[calc(100vh-72px)] bg-white/80 dark:bg-[#08061a]/80 backdrop-blur-xl border-r border-slate-200/80 dark:border-white/[0.04] w-64 flex-shrink-0 transition-all duration-300 flex flex-col z-20 overflow-hidden ${
        !open ? '-ml-64' : ''
      }`}
    >
      {/* Logo */}
      <div className="p-5 border-b border-slate-200/80 dark:border-white/[0.04] flex items-center h-[72px]">
        <h1 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">AI Client Hunt</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 mt-6 overflow-y-auto">
        {navItems.map((section, si) => (
          <div key={si}>
            <div className={`px-4 mb-2 text-xs font-bold text-slate-400 dark:text-[#6B6890] uppercase tracking-wider ${si > 0 ? 'mt-8' : ''}`}>
              {section.label}
            </div>
            {section.items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center px-4 py-2.5 text-sm rounded-xl mx-3 my-1 transition-all duration-200 font-medium ${
                  isActive(item.href)
                    ? 'bg-slate-200/50 dark:bg-white/[0.06] text-slate-900 dark:text-white'
                    : 'text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/30 dark:hover:bg-white/[0.03]'
                }`}
              >
                <svg className="w-5 h-5 mr-3 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={item.icon} />
                  {item.icon2 && (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={item.icon2} />
                  )}
                </svg>
                {item.label}
              </Link>
            ))}
          </div>
        ))}
      </nav>

      {/* Sidebar footer */}
      <div className="p-4 border-t border-slate-200/80 dark:border-white/[0.04]">
        <div className="flex items-center">
          <div className="w-9 h-9 rounded-xl bg-slate-200/50 dark:bg-white/[0.04] flex items-center justify-center text-xs font-bold text-slate-600 dark:text-[#C8C4E8] border border-slate-200/80 dark:border-white/[0.06]">
            ACH
          </div>
          <div className="ml-3">
            <p className="text-sm font-bold text-slate-900 dark:text-white">AI Client Hunt</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
