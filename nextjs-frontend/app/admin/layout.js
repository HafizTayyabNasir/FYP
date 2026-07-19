'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

export default function AdminLayout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      router.push('/login');
      return;
    }
    try {
      const user = JSON.parse(userStr);
      if (user.role !== 'admin') {
        router.push('/dashboard');
        return;
      }
      setIsAdmin(true);
    } catch (e) {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }, [router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#0B0914] text-slate-900 dark:text-white">Loading Admin Portal...</div>;
  if (!isAdmin) return null;

  const navItems = [
    { name: 'Dashboard', path: '/admin', icon: '📊' },
    { name: 'Users', path: '/admin/users', icon: '👥' },
    { name: 'Payments', path: '/admin/payments', icon: '💳' },
    { name: 'Back to App', path: '/dashboard', icon: '⬅️' },
  ];

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-[#0B0914] text-slate-900 dark:text-white font-sans">
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-200 dark:border-white/10 bg-white dark:bg-[#120F22] flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-white/10">
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#6D5DF6] to-[#A78BFA]">
            Admin Portal
          </span>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-3">
            {navItems.map((item) => {
              const isActive = pathname === item.path || (item.path !== '/admin' && pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-[#6D5DF6]/10 text-[#6D5DF6] dark:text-[#A78BFA]' 
                      : 'text-slate-600 dark:text-[#8E8BA3] hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="h-16 flex items-center justify-between px-8 border-b border-slate-200 dark:border-white/10 bg-white dark:bg-[#0B0914] sticky top-0 z-10">
          <h1 className="text-xl font-bold">Administration</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium bg-[#6D5DF6]/20 text-[#6D5DF6] px-3 py-1 rounded-full">Admin Privileges Active</span>
          </div>
        </div>
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
