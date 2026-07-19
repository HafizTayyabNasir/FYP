'use client';

import { useState, useEffect, useRef } from 'react';
import { Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Chart, PieController, RadarController, ArcElement, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import { useToast } from '../components/ToastProvider';
import Spinner from '../components/Spinner';

Chart.register(PieController, RadarController, ArcElement, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

function AuditsContent() {
  const showToast = useToast();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [websiteUrl, setWebsiteUrl] = useState('');
  const [auditing, setAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [recentAudits, setRecentAudits] = useState([]);
  const [extractingData, setExtractingData] = useState(false);
  const [businessData, setBusinessData] = useState(null);
  const [showEmailEditor, setShowEmailEditor] = useState(false);
  const [generatingEmail, setGeneratingEmail] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [crawlingEmail, setCrawlingEmail] = useState(false);
  const [emailForm, setEmailForm] = useState({ to: '', from: '', subject: '', body: '' });

  const pieRef = useRef(null);
  const radarRef = useRef(null);
  const pieChart = useRef(null);
  const radarChart = useRef(null);
  const emailEditorRef = useRef(null);

  useEffect(() => {
    loadRecentAudits();
    const wp = searchParams.get('website');
    
    // Check session storage first
    let restoredAudit = null;
    let restoredBusinessData = null;
    
    try {
      const savedAudit = sessionStorage.getItem('currentAudit');
      if (savedAudit) restoredAudit = JSON.parse(savedAudit);
      
      const savedBiz = sessionStorage.getItem('currentBusinessData');
      if (savedBiz) restoredBusinessData = JSON.parse(savedBiz);
    } catch (e) {}
    
    if (wp) {
      setWebsiteUrl(wp);
      if (restoredAudit && restoredAudit.url === wp) {
        setAuditResult(restoredAudit);
        if (restoredBusinessData && restoredBusinessData.website_url === wp) {
          setBusinessData(restoredBusinessData);
        }
      } else {
        runAuditFor(wp);
      }
    } else {
      if (restoredAudit) {
        setWebsiteUrl(restoredAudit.url);
        setAuditResult(restoredAudit);
      }
      if (restoredBusinessData) setBusinessData(restoredBusinessData);
    }

    const saved = sessionStorage.getItem('auditBusiness');
    if (saved) {
      try {
        const biz = JSON.parse(saved);
        setEmailForm(prev => ({ ...prev, to: biz.email || '' }));
        sessionStorage.removeItem('auditBusiness');
      } catch {}
    }
  }, [searchParams]);

  useEffect(() => {
    if (auditResult) {
      sessionStorage.setItem('currentAudit', JSON.stringify(auditResult));
    } else {
      sessionStorage.removeItem('currentAudit');
    }
  }, [auditResult]);

  useEffect(() => {
    if (businessData) {
      sessionStorage.setItem('currentBusinessData', JSON.stringify(businessData));
    } else {
      sessionStorage.removeItem('currentBusinessData');
    }
  }, [businessData]);

  function authHeaders() {
    const token = typeof window !== 'undefined' ? (localStorage.getItem('access_token') || localStorage.getItem('token')) : '';
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }

  function loadRecentAudits() {
    setRecentAudits(JSON.parse(localStorage.getItem('recentAudits') || '[]'));
  }

  async function runAuditFor(url) {
    setAuditing(true);
    setAuditResult(null);
    try {
      const res = await fetch(`/api/v1/audits/quick/${encodeURIComponent(url)}`, {
        headers: authHeaders()
      });
      if (res.ok) {
        const data = await res.json();
        setAuditResult(data);
        showToast('Audit completed!', 'success');
        saveAuditLocally(data);
      } else {
        const err = await res.json();
        showToast(err.detail || 'Audit failed', 'error');
      }
    } catch (e) {
      showToast('Audit failed: ' + e.message, 'error');
    } finally {
      setAuditing(false);
    }
  }

  async function runQuickAudit() {
    if (!websiteUrl.trim()) { showToast('Enter a URL', 'warning'); return; }
    await runAuditFor(websiteUrl);
  }

  function saveAuditLocally(audit) {
    let audits = JSON.parse(localStorage.getItem('recentAudits') || '[]');
    audits.unshift(audit);
    audits = audits.slice(0, 20);
    localStorage.setItem('recentAudits', JSON.stringify(audits));
    setRecentAudits(audits);
  }

  function viewAudit(audit) {
    setAuditResult(audit);
    setWebsiteUrl(audit.url);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  useEffect(() => {
    if (auditResult) {
      renderPieChart();
      renderRadarChart();
    }
    return () => {
      if (pieChart.current) pieChart.current.destroy();
      if (radarChart.current) radarChart.current.destroy();
    };
  }, [auditResult]);

  function renderPieChart() {
    if (!pieRef.current || !auditResult) return;
    if (pieChart.current) pieChart.current.destroy();
    const r = auditResult;
    pieChart.current = new Chart(pieRef.current.getContext('2d'), {
      type: 'pie',
      data: {
        labels: ['SEO', 'SSL', 'Speed', 'Responsive', 'Social', 'Images'],
        datasets: [{ data: [r.seo?.score||r.seo_metadata?.score||0, r.ssl?.score||r.ssl_certificate?.score||0, r.load_speed?.score||0, r.responsiveness?.score||0, r.social_links?.score||0, r.image_alt?.score||r.image_alt_tags?.score||0], backgroundColor: ['#3B82F6','#10B981','#F59E0B','#8B5CF6','#EC4899','#6366F1'], borderWidth: 2, borderColor: '#fff' }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8' } }, tooltip: { callbacks: { label: ctx => ctx.label + ': ' + ctx.raw.toFixed(1) + '/5' } } } }
    });
  }

  function renderRadarChart() {
    if (!radarRef.current || !auditResult) return;
    if (radarChart.current) radarChart.current.destroy();
    const r = auditResult;
    radarChart.current = new Chart(radarRef.current.getContext('2d'), {
      type: 'radar',
      data: {
        labels: ['SEO', 'SSL', 'Speed', 'Responsive', 'Social', 'Images'],
        datasets: [{ label: 'Score', data: [r.seo?.score||r.seo_metadata?.score||0, r.ssl?.score||r.ssl_certificate?.score||0, r.load_speed?.score||0, r.responsiveness?.score||0, r.social_links?.score||0, r.image_alt?.score||r.image_alt_tags?.score||0], backgroundColor: 'rgba(59,130,246,0.2)', borderColor: 'rgb(59,130,246)', borderWidth: 2, pointBackgroundColor: 'rgb(59,130,246)', pointBorderColor: '#fff' }]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 5, ticks: { stepSize: 1, color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.1)' }, angleLines: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: '#94A3B8' } } }, plugins: { legend: { display: false } } }
    });
  }

  function getScoreColor(score) {
    if (!score) return 'text-slate-500 dark:text-[#8E8BA3]';
    if (score >= 4) return 'text-emerald-400';
    if (score >= 3) return 'text-yellow-500';
    if (score >= 2) return 'text-orange-500';
    return 'text-red-500';
  }

  async function extractBusinessData() {
    if (!auditResult?.url) { showToast('Run an audit first', 'warning'); return; }
    setExtractingData(true);
    setBusinessData(null);
    try {
      const res = await fetch('/api/v1/businesses/extract', { method: 'POST', headers: authHeaders(), body: JSON.stringify({ url: auditResult.url }) });
      if (res.ok) {
        const data = await res.json();
        data.website_url = auditResult.url;
        setBusinessData(data);
        if (data?.contact_info?.email) setEmailForm(prev => ({ ...prev, to: data.contact_info.email }));
        showToast('Business data extracted!', 'success');
      } else {
        let errStr = 'Extraction failed';
        try { const err = await res.json(); errStr = err.detail || errStr; }
        catch(e) { errStr = await res.text(); }
        showToast(errStr, 'error');
      }
    } catch (e) { showToast('Extraction failed: ' + e.message, 'error'); }
    finally { setExtractingData(false); }
  }

  async function crawlForEmail() {
    const url = auditResult?.url || websiteUrl;
    if (!url) { showToast('No URL available', 'warning'); return; }
    setCrawlingEmail(true);
    try {
      const res = await fetch('/api/v1/businesses/crawl-url', { method: 'POST', headers: authHeaders(), body: JSON.stringify({ url }) });
      if (res.ok) {
        const data = await res.json();
        const foundEmail = data.email || (data.all_emails?.length > 0 ? data.all_emails[0] : null);
        if (foundEmail) { setEmailForm(prev => ({ ...prev, to: foundEmail })); showToast(`Found: ${foundEmail}`, 'success'); }
        else showToast('No email found', 'warning');
      } else showToast('Crawl failed', 'error');
    } catch (e) { showToast('Crawl failed', 'error'); }
    finally { setCrawlingEmail(false); }
  }

  async function generateEmailWithAI() {
    setGeneratingEmail(true);
    try {
      const payload = {
        business_name: businessData?.business_name || 'Business',
        website_url: auditResult?.url || websiteUrl,
        industry: businessData?.industry || null,
        location: businessData?.location || null,
        target_audience: businessData?.target_customers || null,
        business_goal: businessData?.business_goal || null,
        seo_score: auditResult?.seo?.score || auditResult?.seo_metadata?.score || 0,
        ssl_score: auditResult?.ssl?.score || auditResult?.ssl_certificate?.score || 0,
        load_speed_score: auditResult?.load_speed?.score || 0,
        responsiveness_score: auditResult?.responsiveness?.score || 0,
        social_links_score: auditResult?.social_links?.score || 0,
        image_alt_score: auditResult?.image_alt?.score || auditResult?.image_alt_tags?.score || 0,
        specific_issues: [], additional_notes: null
      };
      const res = await fetch('/api/v1/outreach/generate-email', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) });
      if (res.ok) {
        const data = await res.json();
        const subject = data.subject_lines?.[0] || 'Website Improvement Opportunity';
        let body = data.email_body || data.body || '';
        body = body.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>').replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
        setEmailForm(prev => ({ ...prev, subject, body: '<p>' + body + '</p>' }));
        if (emailEditorRef.current) emailEditorRef.current.innerHTML = '<p>' + body + '</p>';
        showToast('Email generated!', 'success');
      } else { const err = await res.json(); showToast(typeof err.detail === 'string' ? err.detail : 'Generation failed', 'error'); }
    } catch (e) { showToast('Generation failed', 'error'); }
    finally { setGeneratingEmail(false); }
  }

  async function sendEmail() {
    if (!emailForm.to || !emailForm.subject) { showToast('Fill recipient and subject', 'warning'); return; }
    setSendingEmail(true);
    try {
      const body = emailForm.body;
      const res = await fetch('/api/v1/mail/send', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ to_email: emailForm.to, subject: emailForm.subject, body: body.replace(/<[^>]*>?/gm, ''), html_body: body })
      });
      if (res.ok) {
        showToast('Email sent!', 'success');
        setShowEmailEditor(false);
        setEmailForm({ to: '', from: '', subject: '', body: '' });
      } else { const err = await res.json(); showToast(err.detail || 'Send failed', 'error'); }
    } catch (e) { showToast('Send failed', 'error'); }
    finally { setSendingEmail(false); }
  }

  function downloadReport() {
    const blob = new Blob([JSON.stringify(auditResult, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `audit-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  }

  function generateEmailFromAudit() {
    sessionStorage.setItem('auditData', JSON.stringify(auditResult));
    window.location.href = '/outreach';
  }

  return (
    <div>
      {/* Audit Input */}
      <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Quick Website Audit</h3>
        <div className="flex gap-4">
          <input value={websiteUrl} onChange={e => setWebsiteUrl(e.target.value)} onKeyDown={e => e.key === 'Enter' && runQuickAudit()} type="text" placeholder="https://example.com"
            className="flex-1 px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" />
          <button onClick={runQuickAudit} disabled={auditing}
            className="bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-semibold py-2.5 px-6 rounded-lg transition-colors disabled:opacity-50 flex items-center">
            {auditing ? <><Spinner className="mr-2 h-4 w-4" /> Auditing...</> : '🔍 Run Audit'}
          </button>
        </div>
      </div>

      {/* Audit Results */}
      {auditResult && (
        <div className="space-y-6 mb-6">
          {/* Overall Score */}
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Audit Results</h3>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">{auditResult.url}</p>
              </div>
              <div className="flex space-x-2">
                <button onClick={downloadReport} className="px-3 py-1.5 text-sm border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white">📥 Download</button>
                <button onClick={() => setShowEmailEditor(!showEmailEditor)} className="px-3 py-1.5 text-sm bg-accent-violet hover:bg-purple-600 text-white rounded-lg">✉️ Email</button>
                <button onClick={generateEmailFromAudit} className="px-3 py-1.5 text-sm bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white rounded-lg">📧 Outreach</button>
              </div>
            </div>

            {/* Score Overview */}
            <div className="text-center mb-6">
              <div className={`text-5xl font-bold ${getScoreColor(auditResult.overall_score)}`}>{(auditResult.overall_score || 0).toFixed(1)}<span className="text-2xl text-slate-500 dark:text-[#8E8BA3]">/5</span></div>
              <p className="text-slate-500 dark:text-[#8E8BA3] mt-1">Overall Score</p>
            </div>

            {/* Score Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { label: 'SEO', score: auditResult.seo?.score || auditResult.seo_metadata?.score },
                { label: 'SSL', score: auditResult.ssl?.score || auditResult.ssl_certificate?.score },
                { label: 'Speed', score: auditResult.load_speed?.score },
                { label: 'Responsive', score: auditResult.responsiveness?.score },
                { label: 'Social', score: auditResult.social_links?.score },
                { label: 'Images', score: auditResult.image_alt?.score || auditResult.image_alt_tags?.score },
              ].map((item, i) => (
                <div key={i} className="bg-slate-100 dark:bg-[#08061a] rounded-lg p-4 text-center border border-slate-200/80 dark:border-white/[0.06]">
                  <p className="text-xs text-slate-500 dark:text-[#8E8BA3] mb-1">{item.label}</p>
                  <p className={`text-2xl font-bold ${getScoreColor(item.score)}`}>{(item.score || 0).toFixed(1)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h4 className="font-semibold text-slate-900 dark:text-white mb-4">Score Distribution</h4>
              <div className="h-64"><canvas ref={pieRef} /></div>
            </div>
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h4 className="font-semibold text-slate-900 dark:text-white mb-4">Metrics Radar</h4>
              <div className="h-64"><canvas ref={radarRef} /></div>
            </div>
          </div>

          {/* Detailed Breakdown */}
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <h4 className="font-semibold text-slate-900 dark:text-white mb-4">Detailed Breakdown</h4>
            <div className="space-y-4">
              {[
                { label: 'SEO', data: auditResult.seo || auditResult.seo_metadata },
                { label: 'SSL', data: auditResult.ssl || auditResult.ssl_certificate },
                { label: 'Speed', data: auditResult.load_speed },
                { label: 'Responsive', data: auditResult.responsiveness },
                { label: 'Social', data: auditResult.social_links },
                { label: 'Images', data: auditResult.image_alt || auditResult.image_alt_tags },
              ].map((item, i) => (
                <div key={i} className="bg-slate-100 dark:bg-[#08061a] rounded-lg p-4 border border-slate-200/80 dark:border-white/[0.06]">
                  <div className="flex justify-between items-center mb-2">
                    <h5 className="font-medium text-slate-900 dark:text-white">{item.label} Score: {(item.data?.score || 0).toFixed(1)}/5</h5>
                  </div>
                  {item.data?.flaws && item.data.flaws.length > 0 ? (
                    <ul className="list-disc list-inside text-sm text-red-400 space-y-1">
                      {item.data.flaws.map((flaw, j) => <li key={j}>{flaw}</li>)}
                    </ul>
                  ) : (
                    <p className="text-sm text-emerald-400">✓ No critical issues found.</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Business Data Extraction */}
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-slate-900 dark:text-white">Business Intelligence</h4>
              <div className="flex space-x-2">
                <button onClick={extractBusinessData} disabled={extractingData} className="px-3 py-1.5 text-sm bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white rounded-lg disabled:opacity-50">
                  {extractingData ? 'Extracting...' : '🔍 Extract Data'}
                </button>
                <button onClick={() => {
                  const data = {
                    url: auditResult?.url || websiteUrl,
                    audit: auditResult,
                    business: businessData,
                  };
                  sessionStorage.setItem('auditToOutreach', JSON.stringify(data));
                  router.push('/outreach');
                }} className="px-3 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg flex items-center gap-1.5 transition-colors">
                  ✉️ Write Email
                </button>
              </div>
            </div>
            {businessData && (
              <div className="grid grid-cols-2 gap-4">
                {Object.entries({ 'Business': businessData.business_name, 'Industry': businessData.industry, 'Location': businessData.location, 'Core Offer': businessData.core_offer, 'Target': businessData.target_customers, 'Goal': businessData.business_goal }).map(([k, v]) => (
                  <div key={k} className="bg-slate-100 dark:bg-[#08061a] p-3 rounded-lg border border-slate-200/80 dark:border-white/[0.06]">
                    <p className="text-xs text-slate-500 dark:text-[#8E8BA3]">{k}</p>
                    <p className="text-sm text-slate-900 dark:text-white">{v || '-'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Email Editor Modal */}
      {showEmailEditor && (
        <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] mb-6">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4">Compose Email</h4>
          <div className="space-y-4">
            <input value={emailForm.to} onChange={e => setEmailForm(p => ({ ...p, to: e.target.value }))} placeholder="To email" className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" />
            <input value={emailForm.subject} onChange={e => setEmailForm(p => ({ ...p, subject: e.target.value }))} placeholder="Subject" className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" />
            <div ref={emailEditorRef} contentEditable suppressContentEditableWarning className="w-full min-h-[200px] px-4 py-3 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]"
              onInput={e => setEmailForm(p => ({ ...p, body: e.currentTarget.innerHTML }))}><p>Start typing...</p></div>
            <div className="flex space-x-2">
              <button onClick={generateEmailWithAI} disabled={generatingEmail} className="px-4 py-2 text-sm bg-accent-violet hover:bg-purple-600 text-white rounded-lg disabled:opacity-50">
                {generatingEmail ? 'Generating...' : '🤖 AI Generate'}
              </button>
              <button onClick={sendEmail} disabled={sendingEmail} className="px-4 py-2 text-sm bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white rounded-lg disabled:opacity-50">
                {sendingEmail ? 'Sending...' : '📤 Send'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Recent Audits */}
      <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Recent Audits</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-100 dark:bg-white/[0.04]">
              <tr>
                <th className="px-4 py-3 text-xs font-medium text-slate-500 dark:text-[#8E8BA3] uppercase">URL</th>
                <th className="px-4 py-3 text-xs font-medium text-slate-500 dark:text-[#8E8BA3] uppercase">Score</th>
                <th className="px-4 py-3 text-xs font-medium text-slate-500 dark:text-[#8E8BA3] uppercase">Date</th>
                <th className="px-4 py-3 text-xs font-medium text-slate-500 dark:text-[#8E8BA3] uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentAudits.map((audit, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:bg-white/[0.03] border-b border-slate-200/80 dark:border-white/[0.06]">
                  <td className="px-4 py-3"><a href={audit.url} target="_blank" className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA]">{audit.url}</a></td>
                  <td className="px-4 py-3"><span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${audit.overall_score >= 4 ? 'bg-emerald-500/20 text-emerald-400' : audit.overall_score >= 3 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>{(audit.overall_score||0).toFixed(1)}/5</span></td>
                  <td className="px-4 py-3 text-slate-500 dark:text-[#8E8BA3]">{new Date(audit.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-3"><button onClick={() => viewAudit(audit)} className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] text-sm">View Details</button></td>
                </tr>
              ))}
              {recentAudits.length === 0 && (<tr><td colSpan="4" className="px-4 py-8 text-center text-slate-500 dark:text-[#8E8BA3]">No audits yet. Run your first audit above.</td></tr>)}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default function AuditsPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-12"><Spinner className="w-8 h-8 text-[#6D5DF6] dark:text-[#A78BFA]" /></div>}>
      <AuditsContent />
    </Suspense>
  );
}
