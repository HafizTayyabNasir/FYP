'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('Verifying your email address...');

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Invalid or missing verification token.');
      return;
    }

    async function verifyToken() {
      try {
        const res = await fetch(`${API}/api/v1/auth/verify-email?token=${token}`);
        if (res.ok) {
          setStatus('success');
          setMessage('Your email has been successfully verified! You can now login to your account.');
        } else {
          const err = await res.json();
          setStatus('error');
          setMessage(err.detail || 'Email verification failed. The token may be expired or invalid.');
        }
      } catch (e) {
        setStatus('error');
        setMessage('A network error occurred while verifying your email. Please try again later.');
      }
    }

    verifyToken();
  }, [token, API]);

  return (
    <main className="mx-auto flex min-h-[calc(100vh-154px)] max-w-2xl items-center justify-center px-5 py-12">
      <div className="w-full text-center rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015] p-10 shadow-sm dark:shadow-none transition-all duration-300">
        
        {status === 'verifying' && (
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#6D5DF6] border-t-transparent mb-6" />
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Verifying Email</h2>
            <p className="text-slate-600 dark:text-[#8E8BA3]">{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center">
            <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-emerald-100 dark:bg-emerald-500/20 mb-6">
              <span className="text-4xl">✅</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Email Verified!</h2>
            <p className="text-slate-600 dark:text-[#8E8BA3] mb-8">{message}</p>
            <Link href="/login" className="w-full rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-5 py-3.5 text-sm font-bold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5">
              Proceed to Login
            </Link>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center">
            <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-red-100 dark:bg-red-500/20 mb-6">
              <span className="text-4xl">❌</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Verification Failed</h2>
            <p className="text-slate-600 dark:text-[#8E8BA3] mb-8">{message}</p>
            <div className="flex gap-4 w-full">
              <Link href="/signup" className="flex-1 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 px-5 py-3.5 text-sm font-bold text-slate-700 dark:text-white transition-all">
                Sign Up Again
              </Link>
              <Link href="/login" className="flex-1 rounded-xl bg-[#6D5DF6] hover:bg-[#5b4ee4] px-5 py-3.5 text-sm font-bold text-white transition-all">
                Go to Login
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
