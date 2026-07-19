'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function SignupPage() {
  const [showModal, setShowModal] = useState(true);

  function handleSubmit(event) {
    if (event) event.preventDefault();
    setShowModal(true);
  }

  return (
    <main className="mx-auto grid min-h-[calc(100vh-154px)] max-w-7xl items-center gap-10 px-5 py-12 lg:grid-cols-[0.95fr_1.05fr]">
      <div>
        <p className="mb-4 text-xs font-bold uppercase tracking-wider text-[#6D5DF6] dark:text-[#A78BFA]">Internal Tool</p>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white md:text-5xl tracking-tight leading-tight">AI Client Hunting & Outreach Platform</h1>
        <p className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-[#8E8BA3]">
          Automated business discovery, instant website auditing, and AI-powered outreach campaign generation.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015] p-8 shadow-sm transition-all duration-300">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Sign Up</h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-[#8E8BA3]">Public registrations are currently disabled.</p>

        <form onSubmit={handleSubmit}>
          <label className="mt-8 block opacity-60">
            <span className="mb-2 block text-sm font-bold text-slate-900 dark:text-white">Full Name</span>
            <input
              disabled
              className="w-full cursor-not-allowed rounded-xl border border-slate-200 dark:border-white/[0.06] bg-slate-100 dark:bg-white/[0.02] px-4 py-3.5 text-slate-500 dark:text-[#8E8BA3]"
              type="text"
              placeholder="Public sign up disabled"
            />
          </label>

          <label className="mt-5 block opacity-60">
            <span className="mb-2 block text-sm font-bold text-slate-900 dark:text-white">Email</span>
            <input
              disabled
              className="w-full cursor-not-allowed rounded-xl border border-slate-200 dark:border-white/[0.06] bg-slate-100 dark:bg-white/[0.02] px-4 py-3.5 text-slate-500 dark:text-[#8E8BA3]"
              type="email"
              placeholder="you@example.com"
            />
          </label>

          <button
            type="button"
            onClick={() => setShowModal(true)}
            className="mt-8 w-full rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-5 py-3.5 text-sm font-bold text-white shadow-sm transition-all duration-300"
          >
            Create Account
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600 dark:text-[#8E8BA3]">
          Already have admin access?{' '}
          <Link href="/login" className="font-bold text-[#6D5DF6] hover:underline">
            Login
          </Link>
        </p>
      </div>

      {/* Restriction Popup Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-[#0B0914] rounded-2xl p-6 sm:p-8 max-w-md w-full border border-slate-200 dark:border-white/10 shadow-2xl text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-amber-100 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 text-3xl mb-4">
              ⚠️
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Notice</h3>
            <p className="text-base font-semibold text-amber-600 dark:text-amber-400 mb-6 bg-amber-50 dark:bg-amber-500/10 p-4 rounded-xl border border-amber-200 dark:border-amber-500/20">
              Tool is currently no launched for the public use
            </p>
            <div className="flex gap-3">
              <Link
                href="/login"
                className="w-full rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] py-3 px-5 text-sm font-bold text-white transition-all shadow-md"
              >
                Go to Admin Login
              </Link>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
