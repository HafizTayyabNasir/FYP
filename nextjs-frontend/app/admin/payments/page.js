'use client';

import { useState, useEffect } from 'react';
import Spinner from '../../components/Spinner';

const API = process.env.NEXT_PUBLIC_API_URL || '';
function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''; }

export default function AdminPaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayments();
  }, []);

  async function fetchPayments() {
    try {
      const res = await fetch(`${API}/api/v1/admin/payments`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      if (res.ok) {
        setPayments(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="flex justify-center p-12"><Spinner className="h-8 w-8 text-[#6D5DF6]" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Payment History</h2>
      </div>

      <div className="bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-white/5 text-slate-500 dark:text-[#8E8BA3] font-semibold border-b border-slate-200 dark:border-white/10">
              <tr>
                <th className="px-6 py-4">Transaction ID</th>
                <th className="px-6 py-4">User ID</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Plan</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-white/10">
              {payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-slate-500 dark:text-slate-400">{payment.transaction_id || 'N/A'}</td>
                  <td className="px-6 py-4 font-mono text-xs text-slate-500 dark:text-slate-400" title={payment.user_id}>{payment.user_id.substring(0,8)}...</td>
                  <td className="px-6 py-4 font-bold text-slate-900 dark:text-white">${payment.amount.toFixed(2)} {payment.currency}</td>
                  <td className="px-6 py-4 uppercase text-xs font-bold text-slate-500">{payment.plan_name}</td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{new Date(payment.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                      payment.status === 'completed' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' :
                      payment.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300' :
                      'bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-slate-300'
                    }`}>
                      {payment.status}
                    </span>
                  </td>
                </tr>
              ))}
              {payments.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">No payment history found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
