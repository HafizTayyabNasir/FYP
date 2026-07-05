'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function handleSubmit(event) {
    event.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API}/api/v1/auth/login/json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('access_token', data.token);
        if (data.user && data.user.full_name) {
          localStorage.setItem('user_name', data.user.full_name);
        }
        window.dispatchEvent(new Event('storage'));
        router.replace('/dashboard');
      } else {
        const err = await res.json();
        setError(err.detail || 'Login failed');
      }
    } catch (e) {
      setError('Network error. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto grid min-h-[calc(100vh-154px)] max-w-7xl items-center gap-10 px-5 py-12 lg:grid-cols-[0.95fr_1.05fr]">
      <div>
        <p className="mb-4 text-xs font-bold uppercase tracking-wider text-[#6D5DF6] dark:text-[#A78BFA]">Secure Access</p>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white md:text-5xl tracking-tight leading-tight">Login required before using the client hunting tool.</h1>
        <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3]">
          Public pages are available to everyone. The dashboard, business hunter, audits, outreach, campaigns, inbox, and settings are protected behind this login.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015] p-8 shadow-sm dark:shadow-none transition-all duration-300">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Login</h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-[#8E8BA3]">Enter your credentials to continue.</p>

        <label className="mt-8 block">
          <span className="mb-2 block text-sm font-bold text-slate-900 dark:text-white">Email</span>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-xl border border-slate-200 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.02] px-4 py-3.5 text-slate-900 dark:text-white outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] focus:ring-1 focus:ring-[#6D5DF6] dark:focus:ring-[#A78BFA] transition-all"
            type="email"
            required
          />
        </label>

        <label className="mt-5 block">
          <span className="mb-2 block text-sm font-bold text-slate-900 dark:text-white">Password</span>
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-xl border border-slate-200 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.02] px-4 py-3.5 text-slate-900 dark:text-white outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] focus:ring-1 focus:ring-[#6D5DF6] dark:focus:ring-[#A78BFA] transition-all"
            type="password"
            required
          />
        </label>

        {error && <p className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3.5 text-sm font-medium text-red-600 dark:text-red-400">{error}</p>}

        <button disabled={loading} className="mt-8 w-full rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] disabled:opacity-50 px-5 py-3.5 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5">
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <p className="mt-6 text-center text-sm text-slate-600 dark:text-[#8E8BA3]">
          Don't have an account?{' '}
          <Link href="/signup" className="font-bold text-[#6D5DF6] hover:underline">
            Sign up
          </Link>
        </p>
      </form>
    </main>
  );
}
