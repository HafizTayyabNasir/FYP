'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js';

Chart.register(DoughnutController, ArcElement, Tooltip, Legend);

export default function DashboardPage() {
  const [stats, setStats] = useState({});
  const [businesses, setBusinesses] = useState([]);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const router = useRouter();

  const loadStats = useCallback(async () => {
    try {
      const statsRes = await fetch('/api/v1/businesses/stats/summary');
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }

      const bizRes = await fetch('/api/v1/businesses?per_page=5');
      if (bizRes.ok) {
        const data = await bizRes.json();
        setBusinesses(data.businesses || []);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadStats();
  }, [loadStats]);

  const renderChart = useCallback(() => {
    const ctx = chartRef.current.getContext('2d');
    if (chartInstance.current) chartInstance.current.destroy();

    const dist = stats.score_distribution || { excellent: 0, good: 0, fair: 0, poor: 0 };

    chartInstance.current = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Excellent', 'Good', 'Fair', 'Poor'],
        datasets: [{
          data: [dist.excellent, dist.good, dist.fair, dist.poor],
          backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
          borderWidth: 0,
          hoverOffset: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#94A3B8',
              padding: 20,
              usePointStyle: true,
              pointStyle: 'circle',
              font: { size: 12, family: 'Inter' },
            },
          },
        },
      },
    });
  }, [stats]);

  useEffect(() => {
    if (chartRef.current && stats.score_distribution) {
      renderChart();
    }
    return () => {
      if (chartInstance.current) chartInstance.current.destroy();
    };
  }, [stats, renderChart]);

  const statCards = [
    { label: 'Total Businesses', value: stats.total_businesses || 0, icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', color: 'text-[#6D5DF6] dark:text-[#A78BFA]' },
    { label: 'With Email', value: stats.with_email || 0, icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z', color: 'text-[#8BA1C1]' },
    { label: 'Audited', value: stats.audited || 0, icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', color: 'text-amber-500' },
    { label: 'Avg Score', value: `${(stats.average_score || 0).toFixed(1)}/5`, icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', color: 'text-[#A78BFA]' },
  ];

  return (
    <div>
      {/* Welcome Banner */}
      <div className="mb-6 p-8 rounded-xl bg-white dark:bg-white/[0.015] border border-slate-200/80 dark:border-white/[0.06] relative overflow-hidden">
        <div className="relative z-10">
          <h1 className="text-2xl font-bold mb-2 text-slate-900 dark:text-white">Welcome to AI Client Hunt</h1>
          <p className="text-slate-500 dark:text-[#8E8BA3]">Your outreach automation platform</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, i) => (
          <div key={i} className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg bg-[#6D5DF6]/10 dark:bg-[#A78BFA]/10 ${card.color}`}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={card.icon} />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-500 dark:text-[#8E8BA3]">{card.label}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Score Distribution */}
        <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Score Distribution</h3>
          <div className="h-64">
            <canvas ref={chartRef} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Quick Actions</h3>
          <div className="space-y-3">
            <Link href="/businesses" className="flex items-center p-4 bg-slate-50 dark:bg-white/[0.03] rounded-lg border border-slate-200/80 dark:border-white/[0.06] hover:border-[#6D5DF6] dark:border-[#A78BFA]/50 transition-colors">
              <div className="p-2 bg-slate-100 dark:bg-[#08061a] rounded text-[#6D5DF6] dark:text-[#A78BFA] mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-white">Hunt New Businesses</p>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Search businesses from OSM database</p>
              </div>
            </Link>

            <Link href="/audits" className="flex items-center p-4 bg-slate-50 dark:bg-white/[0.03] rounded-lg border border-slate-200/80 dark:border-white/[0.06] hover:border-[#6D5DF6] dark:border-[#A78BFA]/50 transition-colors">
              <div className="p-2 bg-slate-100 dark:bg-[#08061a] rounded text-[#8BA1C1] mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-white">Run Website Audit</p>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Analyze website performance</p>
              </div>
            </Link>

            <Link href="/outreach" className="flex items-center p-4 bg-slate-50 dark:bg-white/[0.03] rounded-lg border border-slate-200/80 dark:border-white/[0.06] hover:border-[#6D5DF6] dark:border-[#A78BFA]/50 transition-colors">
              <div className="p-2 bg-slate-100 dark:bg-[#08061a] rounded text-[#A78BFA] mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-white">Generate Outreach Email</p>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">AI-powered personalized emails</p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Businesses */}
      <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Recent Businesses</h3>
          <Link href="/businesses" className="text-sm text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] font-medium">
            View All
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-100 dark:bg-white/[0.04] border-b border-slate-200/80 dark:border-white/[0.06]">
              <tr>
                <th className="px-4 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide">Business</th>
                <th className="px-4 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide">Website</th>
                <th className="px-4 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide">Email</th>
                <th className="px-4 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide">Score</th>
                <th className="px-4 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody>
              {businesses.map((biz, i) => (
                <tr key={biz.id} className={`border-b border-slate-200/80 dark:border-white/[0.06] hover:bg-slate-50 dark:bg-white/[0.03] transition-colors duration-150 ${i % 2 === 0 ? 'bg-slate-50 dark:bg-white/[0.02]' : 'bg-white dark:bg-white/[0.01]'}`}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900 dark:text-white">{biz.business_name || 'Unknown'}</p>
                  </td>
                  <td className="px-4 py-3">
                    <a href={biz.website} target="_blank" rel="noopener noreferrer" className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] text-sm truncate max-w-[200px] block">
                      {biz.website || '-'}
                    </a>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-slate-500 dark:text-[#8E8BA3]">{biz.email || '-'}</span>
                  </td>
                  <td className="px-4 py-3">
                    {biz.audit_completed ? (
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${
                        biz.overall_score >= 4 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        biz.overall_score >= 3 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        {(biz.overall_score || 0).toFixed(1)}/5
                      </span>
                    ) : (
                      <span className="text-sm text-slate-500 dark:text-[#8E8BA3]">Pending</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => router.push(`/businesses?id=${biz.id}`)} className="text-sm font-medium text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white">
                      View
                    </button>
                  </td>
                </tr>
              ))}
              {businesses.length === 0 && (
                <tr>
                  <td colSpan="5" className="py-12 text-center text-slate-500 dark:text-[#8E8BA3]">
                    <p>No businesses found.</p>
                    <Link href="/businesses" className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] mt-2 inline-block">Start Hunting</Link>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
