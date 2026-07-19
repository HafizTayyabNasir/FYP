'use client';

import { useState, useSyncExternalStore } from 'react';
import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useRouter } from 'next/navigation';
import Sidebar from './Sidebar';
import PublicShell from './PublicShell';

const titleMap = {
  '/dashboard': 'Dashboard',
  '/businesses': 'Hunt Businesses',
  '/audits': 'Website Audits',
  '/outreach': 'Email Outreach',
  '/campaigns': 'Campaigns',
  '/inbox': 'Inbox',
  '/settings': 'Settings',
};

const publicRoutes = ['/', '/about', '/contact', '/pricing', '/login', '/signup', '/verify-email', '/blog'];

function subscribeAuth(callback) {
  window.addEventListener('storage', callback);
  return () => window.removeEventListener('storage', callback);
}

function getAuthSnapshot() {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}

export default function AppShell({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pathname = usePathname();
  const router = useRouter();
  const title = titleMap[pathname] || 'AI Client Hunt';
  const isPublicRoute = publicRoutes.includes(pathname);
  const isAuthenticated = useSyncExternalStore(subscribeAuth, getAuthSnapshot, () => false);

  useEffect(() => {
    // Basic redirect logic if not authenticated
    if (!isPublicRoute && !getAuthSnapshot()) {
      router.replace('/login');
    }
  }, [isPublicRoute, router, pathname]);

  if (pathname.startsWith('/admin')) {
    return <>{children}</>;
  }

  if (isPublicRoute) {
    return <PublicShell>{children}</PublicShell>;
  }

  if (!isAuthenticated) {
    return (
      <PublicShell>
        <div className="flex min-h-[calc(100vh-72px)] items-center justify-center bg-transparent transition-colors duration-300">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#6D5DF6] border-t-transparent" />
        </div>
      </PublicShell>
    );
  }

  function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_name');
    sessionStorage.removeItem('huntBusinessesState');
    window.dispatchEvent(new Event('storage'));
    router.replace('/login');
  }

  return (
    <PublicShell>
      {/* Background layers specifically for dashboard to maintain the grid effect */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div
          className="absolute inset-0 opacity-[0.04] dark:opacity-[0.025]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(139,124,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(139,124,246,0.3) 1px, transparent 1px)',
            backgroundSize: '80px 80px',
          }}
        />
        <div className="absolute inset-0 opacity-[0.015]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.5'/%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="flex min-h-[calc(100vh-72px)] bg-transparent relative z-10 w-full max-w-[1600px] mx-auto border-x border-slate-200/80 dark:border-white/[0.04]">
        <Sidebar open={sidebarOpen} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top Header */}
          <header className="sticky top-[72px] z-30 backdrop-blur-xl bg-[#F8FAFC]/80 dark:bg-[#08061a]/80 border-b border-slate-200/80 dark:border-white/[0.04] transition-colors duration-300 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:hover:text-white mr-4 transition-colors duration-200"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white truncate">{title}</h2>
              </div>

              <div className="flex items-center space-x-3 shrink-0">
                <button onClick={logout} className="rounded-xl border border-slate-200/80 dark:border-white/[0.06] bg-white/60 dark:bg-white/[0.04] px-4 py-2 md:px-5 md:py-2.5 text-xs md:text-sm font-bold text-slate-700 dark:text-[#C8C4E8] hover:text-slate-900 dark:hover:text-white transition-all duration-300">
                  Logout
                </button>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 p-6">
            <div className="max-w-7xl mx-auto space-y-6">{children}</div>
          </main>
        </div>
      </div>
    </PublicShell>
  );
}
