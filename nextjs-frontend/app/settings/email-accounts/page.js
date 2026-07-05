'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || '';

const SMTP_PRESETS = {
  hostinger: { label: 'Hostinger', smtp_host: 'smtp.hostinger.com', smtp_port: 587, imap_host: 'imap.hostinger.com', imap_port: 993 },
  godaddy: { label: 'GoDaddy', smtp_host: 'smtpout.secureserver.net', smtp_port: 587, imap_host: 'imap.secureserver.net', imap_port: 993 },
  zoho: { label: 'Zoho Mail', smtp_host: 'smtp.zoho.com', smtp_port: 587, imap_host: 'imap.zoho.com', imap_port: 993 },
  namecheap: { label: 'Namecheap', smtp_host: 'mail.privateemail.com', smtp_port: 587, imap_host: 'mail.privateemail.com', imap_port: 993 },
  cpanel: { label: 'cPanel / Custom', smtp_host: '', smtp_port: 587, imap_host: '', imap_port: 993 },
  gmail_smtp: { label: 'Gmail (SMTP)', smtp_host: 'smtp.gmail.com', smtp_port: 587, imap_host: 'imap.gmail.com', imap_port: 993 },
};

function getToken() {
  if (typeof window !== 'undefined') return localStorage.getItem('access_token') || '';
  return '';
}

function authHeaders() {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` };
}

export default function EmailAccountsPage() {
  const searchParams = useSearchParams();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // list | add | smtp
  const [toast, setToast] = useState(null);
  const [testing, setTesting] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState('hostinger');
  const [smtpForm, setSmtpForm] = useState({ smtp_host: 'smtp.hostinger.com', smtp_port: 587, email_address: '', smtp_password: '', display_name: '', imap_host: 'imap.hostinger.com', imap_port: 993 });

  const showToast = (msg, type = 'success') => { setToast({ msg, type }); setTimeout(() => setToast(null), 4000); };

  useEffect(() => {
    const connected = searchParams.get('connected');
    const email = searchParams.get('email');
    if (connected) showToast(`Account connected: ${email || ''}`, 'success');
    const error = searchParams.get('error');
    if (error) showToast(`Connection failed: ${error}`, 'error');
    fetchAccounts();
  }, []);

  async function fetchAccounts() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/email-accounts/`, { headers: authHeaders() });
      if (res.ok) { const data = await res.json(); setAccounts(data.accounts || []); }
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  async function connectGoogle() {
    try {
      const res = await fetch(`${API}/api/v1/email-accounts/google/auth-url`, { headers: authHeaders() });
      if (!res.ok) { const d = await res.json(); showToast(d.detail || 'Failed', 'error'); return; }
      const data = await res.json();
      window.location.href = data.auth_url;
    } catch (e) { showToast('Google OAuth error', 'error'); }
  }

  async function testSmtp() {
    setTesting(true);
    try {
      const res = await fetch(`${API}/api/v1/email-accounts/test-smtp`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(smtpForm) });
      const data = await res.json();
      showToast(data.message, data.success ? 'success' : 'error');
    } catch (e) { showToast('Test failed', 'error'); }
    setTesting(false);
  }

  async function connectSmtp() {
    setConnecting(true);
    try {
      const res = await fetch(`${API}/api/v1/email-accounts/connect-smtp`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(smtpForm) });
      const data = await res.json();
      if (res.ok) { showToast('Account connected!', 'success'); setView('list'); fetchAccounts(); }
      else showToast(data.detail || 'Failed', 'error');
    } catch (e) { showToast('Connection failed', 'error'); }
    setConnecting(false);
  }

  async function deleteAccount(id) {
    if (!confirm('Disconnect this account?')) return;
    try {
      await fetch(`${API}/api/v1/email-accounts/${id}`, { method: 'DELETE', headers: authHeaders() });
      showToast('Account disconnected', 'success');
      fetchAccounts();
    } catch (e) { showToast('Failed to disconnect', 'error'); }
  }

  async function setDefault(id) {
    try {
      await fetch(`${API}/api/v1/email-accounts/${id}/default`, { method: 'PATCH', headers: authHeaders() });
      showToast('Default account updated', 'success');
      fetchAccounts();
    } catch (e) { showToast('Failed', 'error'); }
  }

  function applyPreset(key) {
    setSelectedPreset(key);
    const p = SMTP_PRESETS[key];
    setSmtpForm(f => ({ ...f, smtp_host: p.smtp_host, smtp_port: p.smtp_port, imap_host: p.imap_host, imap_port: p.imap_port }));
  }

  const providerIcon = (p) => p === 'google' ? '🔵' : '⚙️';
  const providerLabel = (p) => p === 'google' ? 'Google' : 'SMTP';
  const statusColor = (s) => s === 'connected' ? 'text-emerald-500' : s === 'failed' ? 'text-red-500' : 'text-amber-500';

  const cardClass = "bg-white dark:bg-white/[0.015] rounded-xl border border-slate-200/80 dark:border-white/[0.06]";
  const inputClass = "w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-[#6D5DF6]/40";
  const btnPrimary = "px-5 py-2.5 bg-[#6D5DF6] hover:bg-[#5B4DE0] text-white rounded-lg text-sm font-medium transition-colors";
  const btnOutline = "px-5 py-2.5 border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors";

  return (
    <div className="max-w-3xl mx-auto">
      {toast && (
        <div className={`fixed top-6 right-6 z-50 px-5 py-3 rounded-xl text-sm font-medium shadow-lg transition-all ${toast.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'}`}>
          {toast.msg}
        </div>
      )}

      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-12 h-12 rounded-xl bg-[#6D5DF6]/10 flex items-center justify-center mr-4">
            <svg className="w-6 h-6 text-[#6D5DF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Email Accounts</h2>
            <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Connect your email accounts for outreach</p>
          </div>
        </div>
        {view === 'list' && (
          <button onClick={() => setView('add')} className={btnPrimary}>+ Add Account</button>
        )}
        {view !== 'list' && (
          <button onClick={() => setView('list')} className={btnOutline}>← Back</button>
        )}
      </div>

      {/* ── LIST VIEW ── */}
      {view === 'list' && (
        <div className="space-y-4">
          {loading ? (
            <div className={`${cardClass} p-12 text-center`}>
              <div className="animate-spin w-8 h-8 border-2 border-[#6D5DF6] border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-slate-500 dark:text-[#8E8BA3]">Loading accounts...</p>
            </div>
          ) : accounts.length === 0 ? (
            <div className={`${cardClass} p-12 text-center`}>
              <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-white/[0.03] flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">No email accounts connected</h3>
              <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-6">Connect your Gmail, Outlook, or business email to start outreach</p>
              <button onClick={() => setView('add')} className={btnPrimary}>Connect Email Account</button>
            </div>
          ) : (
            accounts.map(acc => (
              <div key={acc.id} className={`${cardClass} p-5 flex items-center justify-between`}>
                <div className="flex items-center space-x-4">
                  <span className="text-2xl">{providerIcon(acc.provider)}</span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-900 dark:text-white">{acc.email_address}</span>
                      {acc.is_default && <span className="text-xs px-2 py-0.5 rounded-full bg-[#6D5DF6]/10 text-[#6D5DF6] font-medium">Default</span>}
                    </div>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="text-xs text-slate-500 dark:text-[#8E8BA3]">{providerLabel(acc.provider)}</span>
                      <span className={`text-xs font-medium ${statusColor(acc.connection_status)}`}>● {acc.connection_status}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {!acc.is_default && (
                    <button onClick={() => setDefault(acc.id)} className="text-xs px-3 py-1.5 rounded-lg border border-slate-200/80 dark:border-white/[0.06] text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/[0.03]">
                      Set Default
                    </button>
                  )}
                  <button onClick={() => deleteAccount(acc.id)} className="text-xs px-3 py-1.5 rounded-lg border border-red-200 dark:border-red-500/20 text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10">
                    Disconnect
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ── ADD VIEW (Choose Provider) ── */}
      {view === 'add' && (
        <div className="space-y-4">
          <button onClick={connectGoogle} className={`${cardClass} p-5 w-full text-left hover:border-blue-300 dark:hover:border-blue-500/30 transition-colors group`}>
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center">
                <svg className="w-6 h-6" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-[#6D5DF6]">Continue with Google</h3>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Gmail, Google Workspace</p>
              </div>
              <svg className="w-5 h-5 text-slate-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
            </div>
          </button>


          <button onClick={() => setView('smtp')} className={`${cardClass} p-5 w-full text-left hover:border-purple-300 dark:hover:border-purple-500/30 transition-colors group`}>
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-purple-50 dark:bg-purple-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-[#6D5DF6]">Other Email Provider (SMTP)</h3>
                <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Hostinger, GoDaddy, Zoho, cPanel</p>
              </div>
              <svg className="w-5 h-5 text-slate-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
            </div>
          </button>
        </div>
      )}

      {/* ── SMTP SETUP VIEW ── */}
      {view === 'smtp' && (
        <div className={`${cardClass} p-6`}>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Connect Business Email</h3>
          <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-6">Enter your SMTP credentials to connect your business email</p>

          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Email Provider</label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(SMTP_PRESETS).map(([key, val]) => (
                <button key={key} onClick={() => applyPreset(key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${selectedPreset === key ? 'bg-[#6D5DF6] text-white' : 'bg-slate-100 dark:bg-white/[0.03] text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-white/[0.06]'}`}>
                  {val.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email Address</label>
              <input value={smtpForm.email_address} onChange={e => setSmtpForm({ ...smtpForm, email_address: e.target.value })} placeholder="info@company.com" className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Password</label>
              <input type="password" value={smtpForm.smtp_password} onChange={e => setSmtpForm({ ...smtpForm, smtp_password: e.target.value })} placeholder="Email password or app password" className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Display Name (optional)</label>
              <input value={smtpForm.display_name} onChange={e => setSmtpForm({ ...smtpForm, display_name: e.target.value })} placeholder="Your Name" className={inputClass} />
            </div>

            <details className="group">
              <summary className="cursor-pointer text-sm font-medium text-[#6D5DF6] hover:underline">Advanced Settings</summary>
              <div className="mt-3 space-y-3 pl-2 border-l-2 border-[#6D5DF6]/20">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">SMTP Host</label>
                    <input value={smtpForm.smtp_host} onChange={e => setSmtpForm({ ...smtpForm, smtp_host: e.target.value })} className={inputClass} />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">SMTP Port</label>
                    <input type="number" value={smtpForm.smtp_port} onChange={e => setSmtpForm({ ...smtpForm, smtp_port: Number(e.target.value) })} className={inputClass} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">IMAP Host</label>
                    <input value={smtpForm.imap_host} onChange={e => setSmtpForm({ ...smtpForm, imap_host: e.target.value })} className={inputClass} />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">IMAP Port</label>
                    <input type="number" value={smtpForm.imap_port} onChange={e => setSmtpForm({ ...smtpForm, imap_port: Number(e.target.value) })} className={inputClass} />
                  </div>
                </div>
              </div>
            </details>

            <div className="flex space-x-3 pt-2">
              <button onClick={testSmtp} disabled={testing || !smtpForm.email_address} className={`${btnOutline} ${testing ? 'opacity-50' : ''}`}>
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
              <button onClick={connectSmtp} disabled={connecting || !smtpForm.email_address} className={`${btnPrimary} ${connecting ? 'opacity-50' : ''}`}>
                {connecting ? 'Connecting...' : 'Connect Account'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
