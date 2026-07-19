'use client';

import { useState, useEffect } from 'react';
import Spinner from '../components/Spinner';

const API = process.env.NEXT_PUBLIC_API_URL || '';
function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''; }

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch(`${API}/api/v1/admin/stats`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) return <div className="flex justify-center p-12"><Spinner className="h-8 w-8 text-[#6D5DF6]" /></div>;
  if (!stats) return <div className="text-red-500">Failed to load statistics.</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Platform Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard title="Total Users" value={stats.total_users} icon="👥" color="bg-blue-500" />
        <StatCard title="Verified Users" value={stats.verified_users} icon="✅" color="bg-emerald-500" />
        <StatCard title="Total Emails Sent" value={stats.total_emails_sent} icon="📤" color="bg-purple-500" />
        <StatCard title="Paying Teams" value={stats.plans?.team || 0} icon="💼" color="bg-amber-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Plan Distribution</h3>
          <div className="space-y-4">
            <PlanBar name="Free / None" count={stats.plans?.none || 0} total={stats.total_users} color="bg-slate-400" />
            <PlanBar name="Individual" count={stats.plans?.individual || 0} total={stats.total_users} color="bg-blue-500" />
            <PlanBar name="Team" count={stats.plans?.team || 0} total={stats.total_users} color="bg-amber-500" />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  return (
    <div className="bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-xl p-6 flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
      <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl text-white shadow-lg ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] uppercase tracking-wider">{title}</p>
        <p className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{value}</p>
      </div>
    </div>
  );
}

function PlanBar({ name, count, total, color }) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-slate-700 dark:text-slate-300">{name}</span>
        <span className="text-slate-500">{count} ({percentage}%)</span>
      </div>
      <div className="w-full bg-slate-100 dark:bg-white/5 rounded-full h-2.5">
        <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}
