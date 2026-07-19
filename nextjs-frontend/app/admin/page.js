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

  if (loading) return <div className="flex justify-center p-12"><Spinner className="h-8 w-8 text-indigo-500" /></div>;
  if (!stats) return (
    <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center gap-3">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      Failed to load statistics from the server.
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Platform Overview</h2>
        <p className="text-slate-400 text-sm mt-1">Real-time metrics and system status.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard 
          title="Total Users" 
          value={stats.total_users} 
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>} 
          colorClass="from-blue-500/20 to-blue-600/20 text-blue-400 border-blue-500/20" 
          iconBg="bg-blue-500/10"
        />
        <StatCard 
          title="Verified Users" 
          value={stats.verified_users} 
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>} 
          colorClass="from-emerald-500/20 to-emerald-600/20 text-emerald-400 border-emerald-500/20" 
          iconBg="bg-emerald-500/10"
        />
        <StatCard 
          title="Emails Sent" 
          value={stats.total_emails_sent} 
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>} 
          colorClass="from-purple-500/20 to-purple-600/20 text-purple-400 border-purple-500/20" 
          iconBg="bg-purple-500/10"
        />
        <StatCard 
          title="Paying Teams" 
          value={stats.plans?.team || 0} 
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>} 
          colorClass="from-amber-500/20 to-amber-600/20 text-amber-400 border-amber-500/20" 
          iconBg="bg-amber-500/10"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-[#111116] border border-white/5 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path></svg>
            Plan Distribution
          </h3>
          <div className="space-y-5 relative z-10">
            <PlanBar name="Free / None" count={stats.plans?.none || 0} total={stats.total_users} color="bg-slate-500" />
            <PlanBar name="Individual" count={stats.plans?.individual || 0} total={stats.total_users} color="bg-indigo-500" glow="shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
            <PlanBar name="Team" count={stats.plans?.team || 0} total={stats.total_users} color="bg-amber-500" glow="shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, colorClass, iconBg }) {
  return (
    <div className={`bg-gradient-to-br ${colorClass} bg-[#111116] border rounded-2xl p-6 flex flex-col gap-4 shadow-lg backdrop-blur-sm relative overflow-hidden group hover:scale-[1.02] transition-transform duration-300`}>
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity transform group-hover:scale-110 duration-500">
        <div className="w-16 h-16">{icon}</div>
      </div>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg} backdrop-blur-md border border-white/5 shadow-sm`}>
        {icon}
      </div>
      <div>
        <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
        <p className="text-sm font-medium opacity-80 mt-1 uppercase tracking-wider">{title}</p>
      </div>
    </div>
  );
}

function PlanBar({ name, count, total, color, glow = '' }) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="font-medium text-slate-300">{name}</span>
        <span className="text-slate-400 font-mono">{count} <span className="opacity-50">({percentage}%)</span></span>
      </div>
      <div className="w-full bg-[#1A1A24] rounded-full h-2.5 overflow-hidden border border-white/5">
        <div 
          className={`h-full rounded-full ${color} ${glow} transition-all duration-1000 ease-out`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
