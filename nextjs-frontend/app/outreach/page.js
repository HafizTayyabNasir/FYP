'use client';

import { useState, useEffect, useRef } from 'react';
import { useToast } from '../components/ToastProvider';
import Spinner from '../components/Spinner';
import RichTextEditor from '../components/RichTextEditor';

const API = process.env.NEXT_PUBLIC_API_URL || '';
function getToken() { if (typeof window !== 'undefined') return localStorage.getItem('access_token') || ''; return ''; }

export default function OutreachPage() {
  const showToast = useToast();
  const editorRef = useRef(null);

  const [businessName, setBusinessName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [industry, setIndustry] = useState('');
  const [locationField, setLocationField] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [businessGoal, setBusinessGoal] = useState('');
  const [additionalNotes, setAdditionalNotes] = useState('');

  const [seoScore, setSeoScore] = useState(0);
  const [sslScore, setSslScore] = useState(0);
  const [speedScore, setSpeedScore] = useState(0);
  const [responsiveScore, setResponsiveScore] = useState(0);
  const [socialScore, setSocialScore] = useState(0);
  const [imageScore, setImageScore] = useState(0);

  const [generating, setGenerating] = useState(false);
  const [crawlingEmail, setCrawlingEmail] = useState(false);
  const [sending, setSending] = useState(false);
  const [emailResult, setEmailResult] = useState(null);
  const [subjectLines, setSubjectLines] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [toEmail, setToEmail] = useState('');
  const [emailBody, setEmailBody] = useState('');

  // Connected email accounts
  const [emailAccounts, setEmailAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [showConnectModal, setShowConnectModal] = useState(false);

  // Fetch connected email accounts
  useEffect(() => {
    async function loadAccounts() {
      try {
        const res = await fetch(`${API}/api/v1/email-accounts/`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        if (res.ok) {
          const data = await res.json();
          setEmailAccounts(data.accounts || []);
          const def = (data.accounts || []).find(a => a.is_default);
          if (def) setSelectedAccountId(def.id);
        }
      } catch (e) { /* no accounts connected */ }
    }
    loadAccounts();
  }, []);

  useEffect(() => {
    // Load data from audit page redirect (Write Email button)
    const auditOutreach = sessionStorage.getItem('auditToOutreach');
    if (auditOutreach) {
      try {
        const { url, audit, business } = JSON.parse(auditOutreach);
        if (url) setWebsiteUrl(url);
        if (audit) {
          setSeoScore(audit.seo?.score || audit.seo_metadata?.score || 0);
          setSslScore(audit.ssl?.score || audit.ssl_certificate?.score || 0);
          setSpeedScore(audit.load_speed?.score || 0);
          setResponsiveScore(audit.responsiveness?.score || 0);
          setSocialScore(audit.social_links?.score || 0);
          setImageScore(audit.image_alt?.score || audit.image_alt_tags?.score || 0);
        }
        if (business) {
          setBusinessName(business.business_name || '');
          setIndustry(business.industry || '');
          setLocationField(business.location || '');
          setTargetAudience(business.target_customers || '');
          setBusinessGoal(business.business_goal || '');
        }
        sessionStorage.removeItem('auditToOutreach');
      } catch {}
    }

    // Legacy: from business list page
    const savedBiz = sessionStorage.getItem('selectedBusiness');
    if (savedBiz) {
      try {
        const biz = JSON.parse(savedBiz);
        setBusinessName(biz.business_name || biz.name || '');
        setWebsiteUrl(biz.website || '');
        setToEmail(biz.email || '');
        if (biz.overall_score) {
          setSeoScore(biz.seo_score || 0);
          setSslScore(biz.ssl_score || 0);
          setSpeedScore(biz.speed_score || 0);
          setResponsiveScore(biz.responsive_score || 0);
          setSocialScore(biz.social_score || 0);
          setImageScore(biz.image_score || 0);
        }
        sessionStorage.removeItem('selectedBusiness');
      } catch {}
    }

    // Legacy: from audit page "Outreach" button
    const auditData = sessionStorage.getItem('auditData');
    if (auditData) {
      try {
        const audit = JSON.parse(auditData);
        setWebsiteUrl(audit.url || '');
        setSeoScore(audit.seo_metadata?.score || audit.seo?.score || 0);
        setSslScore(audit.ssl_certificate?.score || audit.ssl?.score || 0);
        setSpeedScore(audit.load_speed?.score || 0);
        setResponsiveScore(audit.responsiveness?.score || 0);
        setSocialScore(audit.social_links?.score || 0);
        setImageScore(audit.image_alt_tags?.score || audit.image_alt?.score || 0);
        sessionStorage.removeItem('auditData');
      } catch {}
    }
  }, []);

  async function crawlForEmail() {
    if (!websiteUrl.trim()) { showToast('Enter a website URL first', 'warning'); return; }
    setCrawlingEmail(true);
    try {
      const res = await fetch('/api/v1/businesses/crawl-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: websiteUrl })
      });
      if (res.ok) {
        const data = await res.json();
        const foundEmail = data.email || (data.all_emails?.length > 0 ? data.all_emails[0] : null);
        if (foundEmail) {
          setToEmail(foundEmail);
          showToast(`Found: ${foundEmail}`, 'success');
        } else {
          showToast('No email found on website', 'warning');
        }
      } else {
        showToast('Email crawl failed', 'error');
      }
    } catch (e) { showToast('Email crawl failed', 'error'); }
    finally { setCrawlingEmail(false); }
  }

  async function generateEmail() {
    if (!websiteUrl.trim()) { showToast('Enter a website URL', 'warning'); return; }
    setGenerating(true);
    try {
      const payload = {
        business_name: businessName || 'Business',
        website_url: websiteUrl,
        industry: industry || null,
        location: locationField || null,
        target_audience: targetAudience || null,
        business_goal: businessGoal || null,
        seo_score: seoScore, ssl_score: sslScore, load_speed_score: speedScore,
        responsiveness_score: responsiveScore, social_links_score: socialScore,
        image_alt_score: imageScore, specific_issues: [], additional_notes: additionalNotes || null
      };

      const res = await fetch('/api/v1/outreach/generate-email', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setEmailResult(data);
        setSubjectLines(data.subject_lines || []);
        setSelectedSubject(data.subject_lines?.[0] || 'Website Improvement');

        let body = data.email_body || data.body || '';
        body = body.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>').replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
        const html = '<p>' + body + '</p>';
        setEmailBody(html);

        // Set content in editor via DOM
        const editorEl = document.querySelector('[contenteditable]');
        if (editorEl && editorEl._setContent) editorEl._setContent(html);
        else if (editorEl) editorEl.innerHTML = html;

        showToast('Email generated!', 'success');
      } else {
        const err = await res.json();
        showToast(typeof err.detail === 'string' ? err.detail : 'Generation failed', 'error');
      }
    } catch (e) { showToast('Generation failed: ' + e.message, 'error'); }
    finally { setGenerating(false); }
  }

  async function sendEmail() {
    if (!toEmail || !selectedSubject) { showToast('Fill recipient and subject', 'warning'); return; }
    
    if (emailAccounts.length === 0) {
      setShowConnectModal(true);
      return;
    }

    setSending(true);
    try {
      const payload = {
        to_email: toEmail, subject: selectedSubject,
        body: emailBody.replace(/<[^>]*>?/gm, ''), html_body: emailBody,
        ...(selectedAccountId ? { account_id: selectedAccountId } : {})
      };
      const res = await fetch('/api/v1/outreach/send', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('Email sent successfully!', 'success');
        setEmailBody(''); setToEmail(''); setSelectedSubject(''); setEmailResult(null);
        const editorEl = document.querySelector('[contenteditable]');
        if (editorEl && editorEl._setContent) editorEl._setContent('');
        else if (editorEl) editorEl.innerHTML = '';
      } else { const err = await res.json(); showToast(err.detail || 'Send failed', 'error'); }
    } catch (e) { showToast('Send failed', 'error'); }
    finally { setSending(false); }
  }

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left - Input Form */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Business Details</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Business Name</label>
                <input value={businessName} onChange={e => setBusinessName(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="Business name" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Website URL *</label>
                <input value={websiteUrl} onChange={e => setWebsiteUrl(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="https://example.com" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Industry</label>
                  <input value={industry} onChange={e => setIndustry(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="e.g. Healthcare" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Location</label>
                  <input value={locationField} onChange={e => setLocationField(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="City, Country" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Additional Notes</label>
                <textarea value={additionalNotes} onChange={e => setAdditionalNotes(e.target.value)} rows="3" className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="Any specific points..." />
              </div>
            </div>
          </div>

          {/* Audit Scores */}
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Audit Scores (auto-filled from audit)</h3>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: 'SEO', value: seoScore, setter: setSeoScore },
                { label: 'SSL', value: sslScore, setter: setSslScore },
                { label: 'Speed', value: speedScore, setter: setSpeedScore },
                { label: 'Responsive', value: responsiveScore, setter: setResponsiveScore },
                { label: 'Social', value: socialScore, setter: setSocialScore },
                { label: 'Images', value: imageScore, setter: setImageScore },
              ].map((s, i) => (
                <div key={i}>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1">{s.label}</label>
                  <input type="number" min="0" max="5" step="0.1" value={s.value} onChange={e => s.setter(parseFloat(e.target.value) || 0)} className="w-full px-3 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" />
                </div>
              ))}
            </div>
          </div>

          <button onClick={generateEmail} disabled={generating} className="w-full bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center">
            {generating ? <><Spinner className="mr-2 h-4 w-4" /> Generating...</> : '🤖 Generate Outreach Email'}
          </button>
        </div>

        {/* Right - Email Output */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Compose Email</h3>
            <div className="space-y-4">
              {/* Send From (Account Selector) */}
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Send From</label>
                {emailAccounts.length > 0 ? (
                  <select value={selectedAccountId} onChange={e => setSelectedAccountId(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]">
                    <option value="">System Default</option>
                    {emailAccounts.map(acc => (
                      <option key={acc.id} value={acc.id}>
                        {acc.provider === 'google' ? '🔵' : '⚙️'} {acc.email_address} ({acc.provider}){acc.is_default ? ' ★' : ''}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center gap-3 px-4 py-2.5 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg">
                    <span className="text-sm text-amber-700 dark:text-amber-400">No email account connected</span>
                    <a href="/settings/email-accounts" className="text-sm font-medium text-[#6D5DF6] hover:underline">Connect →</a>
                  </div>
                )}
              </div>

              {/* Recipient with Find Email */}
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Recipient Email</label>
                <div className="flex gap-2">
                  <input value={toEmail} onChange={e => setToEmail(e.target.value)} className="flex-1 px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="recipient@email.com" />
                  <button onClick={crawlForEmail} disabled={crawlingEmail} className="px-3 py-2.5 text-sm bg-[#6D5DF6] hover:bg-[#5b4ee4] text-white rounded-lg disabled:opacity-50 whitespace-nowrap flex items-center gap-1.5 transition-colors">
                    {crawlingEmail ? <><Spinner className="h-3.5 w-3.5" /> Finding...</> : '🔍 Find Email'}
                  </button>
                </div>
              </div>

              {/* Subject Lines */}
              {subjectLines.length > 0 ? (
                <div>
                  <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Subject Line</label>
                  <select value={selectedSubject} onChange={e => setSelectedSubject(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]">
                    {subjectLines.map((s, i) => <option key={i} value={s}>{s}</option>)}
                  </select>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Subject Line</label>
                  <input value={selectedSubject} onChange={e => setSelectedSubject(e.target.value)} className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="Email subject..." />
                </div>
              )}

              {/* Rich Text Email Editor */}
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Email Body</label>
                <RichTextEditor
                  value={emailBody}
                  onChange={setEmailBody}
                  placeholder="Generate an email or start typing..."
                  minHeight="320px"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button onClick={sendEmail} disabled={sending || !emailBody} className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center">
                  {sending ? <><Spinner className="mr-2 h-4 w-4" /> Sending...</> : '📤 Send Email'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Connect Email Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-[#0B0914] rounded-2xl p-6 max-w-md w-full border border-slate-200 dark:border-white/10 shadow-xl">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-amber-100 dark:bg-amber-500/20 mb-4">
                <span className="text-xl">📧</span>
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Connect Email Account Required</h3>
              <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-6">
                To send outreach emails, you need to connect your personal or business email account first. This ensures emails are sent directly from your address for better deliverability.
              </p>
              <div className="flex gap-3 w-full">
                <button 
                  onClick={() => setShowConnectModal(false)}
                  className="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-white rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <a 
                  href="/settings/email-accounts"
                  className="flex-1 px-4 py-2.5 bg-[#6D5DF6] hover:bg-[#5b4ee4] text-white rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  Connect Email
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
