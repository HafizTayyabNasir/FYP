'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect, useSyncExternalStore } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

function subscribeAuth(callback) {
  if (typeof window !== 'undefined') {
    window.addEventListener('storage', callback);
    return () => window.removeEventListener('storage', callback);
  }
  return () => {};
}

function getAuthSnapshot() {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}

function getUserNameSnapshot() {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('user_name') || '';
}

function getUserRoleSnapshot() {
  if (typeof window === 'undefined') return '';
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    return user ? user.role : '';
  } catch (e) {
    return '';
  }
}

const navLinks = [
  { href: '/about', label: 'About' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/login', label: 'Tool' },
  { href: '/contact', label: 'Contact' },
  { href: '/blog', label: 'Blog' },
];

const footerLinks = {
  Product: [
    { href: '/login', label: 'Dashboard' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
  ],
  Features: [
    { href: '/login', label: 'Business Discovery' },
    { href: '/login', label: 'Contact Enrichment' },
    { href: '/login', label: 'Website Audits' },
    { href: '/login', label: 'AI Outreach' },
  ],
  Company: [
    { href: '/about', label: 'About Us' },
    { href: '/contact', label: 'Contact' },
    { href: '/blog', label: 'Blog' },
  ],
};

export default function PublicShell({ children }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const deleteAccount = async () => {
    if (!window.confirm("Are you sure you want to delete your account and all associated data? This action cannot be undone.")) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setDropdownOpen(false);
        setMobileMenuOpen(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_name');
        sessionStorage.removeItem('huntBusinessesState');
        window.dispatchEvent(new Event('storage'));
        router.replace('/login');
      } else {
        alert("Failed to delete account. Please try again.");
      }
    } catch (error) {
      console.error(error);
      alert("An error occurred while deleting your account.");
    }
  };

  const isAuthenticated = useSyncExternalStore(subscribeAuth, getAuthSnapshot, () => false);
  const userName = useSyncExternalStore(subscribeAuth, getUserNameSnapshot, () => '');
  const userRole = useSyncExternalStore(subscribeAuth, getUserRoleSnapshot, () => '');
  const firstLetter = userName ? userName.charAt(0).toUpperCase() : 'U';

  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    if (savedTheme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('theme', nextTheme);
    if (nextTheme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.add('dark');
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#08061a] text-slate-600 dark:text-[#c8c4e8] transition-colors duration-300">
      {/* Navigation */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#F8FAFC]/80 dark:bg-[#08061a]/80 border-b border-slate-200/80 dark:border-white/[0.04] transition-colors duration-300">
        <div className="mx-auto max-w-[1280px] px-6 lg:px-8">
          <div className="flex items-center justify-between h-[72px]">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <span className="text-base font-bold text-slate-900 dark:text-white tracking-tight transition-colors duration-250">
                AI Client Hunt
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`relative px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                    pathname === link.href
                      ? 'text-slate-900 dark:text-white bg-slate-200/50 dark:bg-white/[0.06]'
                      : 'text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/30 dark:hover:bg-white/[0.03]'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Desktop CTAs */}
            <div className="hidden lg:flex items-center gap-3">
              {/* Premium Theme Switcher */}
              <button
                onClick={toggleTheme}
                className="relative inline-flex items-center justify-center w-10 h-10 rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-white/60 dark:bg-white/[0.04] text-slate-500 dark:text-[#C8C4E8] hover:text-slate-900 dark:hover:text-white shadow-sm hover:shadow-md transition-all duration-300 hover:scale-105 active:scale-95"
                aria-label="Toggle Theme"
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: theme === 'dark' ? 0 : 185 }}
                  transition={{ type: "spring", stiffness: 200, damping: 15 }}
                  className="flex items-center justify-center"
                >
                  {theme === 'dark' ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646" />
                    </svg>
                  )}
                </motion.div>
              </button>

              {isAuthenticated ? (
                <div className="relative ml-2">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#6D5DF6] to-[#5b4ee4] text-sm font-bold text-white shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105"
                  >
                    {firstLetter}
                  </button>

                  <AnimatePresence>
                    {dropdownOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute right-0 mt-3 w-48 overflow-hidden rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#131127] p-1 shadow-xl backdrop-blur-xl"
                      >
                        <div className="px-3 py-2 border-b border-slate-100 dark:border-white/[0.04] mb-1">
                          <p className="text-xs font-medium text-slate-500 dark:text-[#8E8BA3]">Signed in as</p>
                          <p className="text-sm font-bold text-slate-900 dark:text-white truncate">{userName || 'User'}</p>
                        </div>
                        <Link
                          href="/dashboard"
                          className="flex items-center rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 dark:text-[#C8C4E8] hover:bg-slate-100 dark:hover:bg-white/[0.06] hover:text-slate-900 dark:hover:text-white transition-colors"
                          onClick={() => setDropdownOpen(false)}
                        >
                          Dashboard
                        </Link>
                        <button
                          onClick={() => {
                            setDropdownOpen(false);
                            localStorage.removeItem('access_token');
                            localStorage.removeItem('user_name');
                            sessionStorage.removeItem('huntBusinessesState');
                            window.dispatchEvent(new Event('storage'));
                            router.replace('/');
                          }}
                          className="flex w-full items-center rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 dark:text-[#C8C4E8] hover:bg-slate-100 dark:hover:bg-white/[0.06] hover:text-slate-900 dark:hover:text-white transition-colors mt-1"
                        >
                          Logout
                        </button>
                        <button
                          onClick={deleteAccount}
                          className="flex w-full items-center rounded-xl px-3 py-2 text-sm font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors mt-1"
                        >
                          Delete Account
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-sm font-semibold text-slate-500 dark:text-[#C8C4E8] px-4 py-2 transition-colors duration-200 hover:text-slate-900 dark:hover:text-white"
                  >
                    Log In
                  </Link>
                  <Link
                    href="/signup"
                    className="inline-flex items-center gap-2 rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-5 py-2.5 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Actions (Theme Toggle & Menu) */}
            <div className="lg:hidden flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="relative inline-flex items-center justify-center w-10 h-10 rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-white/60 dark:bg-white/[0.04] text-slate-500 dark:text-[#C8C4E8] hover:text-slate-900 dark:hover:text-white shadow-sm transition-all duration-300 hover:scale-105 active:scale-95"
                aria-label="Toggle Theme"
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: theme === 'dark' ? 0 : 185 }}
                  transition={{ type: "spring", stiffness: 200, damping: 15 }}
                  className="flex items-center justify-center"
                >
                  {theme === 'dark' ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646" />
                    </svg>
                  )}
                </motion.div>
              </button>

              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="flex items-center justify-center w-10 h-10 rounded-lg text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/50 dark:hover:bg-white/[0.04] transition-all"
              >
                Menu
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="lg:hidden border-t border-slate-200/80 dark:border-white/[0.04] bg-[#F8FAFC]/95 dark:bg-[#08061a]/95 backdrop-blur-xl overflow-hidden"
            >
              <div className="px-6 py-4 space-y-1">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-3 text-sm font-medium rounded-lg transition-all ${
                      pathname === link.href
                        ? 'text-slate-900 dark:text-white bg-slate-200/50 dark:bg-white/[0.06]'
                        : 'text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/30 dark:hover:bg-white/[0.03]'
                    }`}
                  >
                    {link.label}
                  </Link>
                ))}
                <div className="pt-3 border-t border-slate-200/80 dark:border-white/[0.04] flex flex-col gap-2">
                  {isAuthenticated ? (
                    <>
                      <Link
                        href="/dashboard"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block w-full text-center rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-[#6D5DF6] px-5 py-3 text-sm font-bold text-white shadow-sm"
                      >
                        Dashboard
                      </Link>
                      <button
                        onClick={() => {
                          setMobileMenuOpen(false);
                          localStorage.removeItem('access_token');
                          localStorage.removeItem('user_name');
                          sessionStorage.removeItem('huntBusinessesState');
                          window.dispatchEvent(new Event('storage'));
                          router.replace('/');
                        }}
                        className="block w-full text-center rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-100 dark:bg-white/[0.04] px-5 py-3 text-sm font-bold text-slate-700 dark:text-[#C8C4E8] hover:bg-slate-200 dark:hover:bg-white/[0.08] transition-colors"
                      >
                        Logout
                      </button>
                      <button
                        onClick={deleteAccount}
                        className="block w-full text-center rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-red-50 dark:bg-red-500/10 px-5 py-3 text-sm font-bold text-red-600 dark:text-red-400 hover:bg-red-100 transition-colors"
                      >
                        Delete Account
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/login"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block w-full text-center rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-white/60 dark:bg-white/[0.04] px-5 py-3 text-sm font-bold text-slate-700 dark:text-[#C8C4E8] hover:text-slate-900 dark:hover:text-white"
                      >
                        Log In
                      </Link>
                      <Link
                        href="/signup"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block w-full text-center rounded-xl bg-[#6D5DF6] px-5 py-3 text-sm font-bold text-white shadow-sm"
                      >
                        Get Started
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {children}

      {/* Footer */}
      <footer className="relative border-t border-slate-200/80 dark:border-white/[0.04] bg-slate-100 dark:bg-[#060518] transition-colors duration-300">
        <div className="mx-auto max-w-[1280px] px-6 lg:px-8 py-16 lg:py-20">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10 lg:gap-16">
            {/* Brand column */}
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center gap-3 mb-5">
                <span className="text-sm font-bold text-slate-900 dark:text-white">AI Client Hunt</span>
              </Link>
              <p className="text-sm text-slate-500 dark:text-[#5C5A7A] leading-relaxed max-w-[260px]">
                Lead generation, website audits, and outreach platform.
              </p>
            </div>

            {/* Link columns */}
            {Object.entries(footerLinks).map(([title, links]) => (
              <div key={title}>
                <h4 className="text-xs font-bold tracking-wider text-slate-400 dark:text-[#6B6890] uppercase mb-4">{title}</h4>
                <ul className="space-y-3">
                  {links.map((link) => (
                    <li key={link.label}>
                      <Link
                        href={link.href}
                        className="text-sm text-slate-500 dark:text-[#5C5A7A] hover:text-[#6D5DF6] dark:hover:text-[#A78BFA] transition-colors duration-200"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div className="mt-14 pt-8 border-t border-slate-200/80 dark:border-white/[0.04] flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-400 dark:text-[#4A4868]">
              © {new Date().getFullYear()} AI Client Hunt & Outreach. All rights reserved.
            </p>

          </div>
        </div>
      </footer>
    </div>
  );
}
