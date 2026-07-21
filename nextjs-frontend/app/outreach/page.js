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



  useEffect(() => {
    let targetUrl = '';
    let extractedEmail = '';

    const auditOutreach = sessionStorage.getItem('auditToOutreach');
    const savedBiz = sessionStorage.getItem('selectedBusiness');
    const auditData = sessionStorage.getItem('auditData');
    
    let loadedNew = false;

    if (auditOutreach) {
      try {
        const { url, audit, business } = JSON.parse(auditOutreach);
        if (url) { setWebsiteUrl(url); targetUrl = url; }
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
          extractedEmail = business.contact_info?.email || business.crawled_email || business.email || '';
        }
        loadedNew = true;
        sessionStorage.removeItem('auditToOutreach');
      } catch {}
    } else if (savedBiz) {
      try {
        const biz = JSON.parse(savedBiz);
        setBusinessName(biz.business_name || biz.name || '');
        if (biz.website) { setWebsiteUrl(biz.website); targetUrl = biz.website; }
        if (biz.email || biz.crawled_email) extractedEmail = biz.email || biz.crawled_email;
        if (biz.overall_score) {
          setSeoScore(biz.seo_score || 0); setSslScore(biz.ssl_score || 0);
          setSpeedScore(biz.speed_score || 0); setResponsiveScore(biz.responsive_score || 0);
          setSocialScore(biz.social_score || 0); setImageScore(biz.image_score || 0);
        }
        loadedNew = true;
        sessionStorage.removeItem('selectedBusiness');
      } catch {}
    } else if (auditData) {
      try {
        const audit = JSON.parse(auditData);
        if (audit.url) { setWebsiteUrl(audit.url); targetUrl = audit.url; }
        setSeoScore(audit.seo_metadata?.score || audit.seo?.score || 0);
        setSslScore(audit.ssl_certificate?.score || audit.ssl?.score || 0);
        setSpeedScore(audit.load_speed?.score || 0);
        setResponsiveScore(audit.responsiveness?.score || 0);
        setSocialScore(audit.social_links?.score || 0);
        setImageScore(audit.image_alt_tags?.score || audit.image_alt?.score || 0);
        loadedNew = true;
        sessionStorage.removeItem('auditData');
      } catch {}
    }

    if (!loadedNew) {
      // Restore from draft
      try {
        const draft = localStorage.getItem('outreachFormDraft');
        if (draft) {
          const d = JSON.parse(draft);
          if (d.businessName) setBusinessName(d.businessName);
          if (d.websiteUrl) setWebsiteUrl(d.websiteUrl);
          if (d.industry) setIndustry(d.industry);
          if (d.locationField) setLocationField(d.locationField);
          if (d.targetAudience) setTargetAudience(d.targetAudience);
          if (d.businessGoal) setBusinessGoal(d.businessGoal);
          if (d.additionalNotes) setAdditionalNotes(d.additionalNotes);
          if (d.seoScore !== undefined) setSeoScore(d.seoScore);
          if (d.sslScore !== undefined) setSslScore(d.sslScore);
          if (d.speedScore !== undefined) setSpeedScore(d.speedScore);
          if (d.responsiveScore !== undefined) setResponsiveScore(d.responsiveScore);
          if (d.socialScore !== undefined) setSocialScore(d.socialScore);
          if (d.imageScore !== undefined) setImageScore(d.imageScore);
          if (d.toEmail) setToEmail(d.toEmail);
          if (d.emailBody) {
             setEmailBody(d.emailBody);
             setTimeout(() => {
                const editorEl = document.querySelector('[contenteditable]');
                if (editorEl && editorEl._setContent) editorEl._setContent(d.emailBody);
                else if (editorEl) editorEl.innerHTML = d.emailBody;
             }, 300);
          }
          if (d.selectedSubject) setSelectedSubject(d.selectedSubject);
          if (d.subjectLines) setSubjectLines(d.subjectLines);
        }
      } catch {}
    } else {
      if (extractedEmail) {
        setToEmail(extractedEmail);
      } else if (targetUrl) {
        fetch('/api/v1/businesses/crawl-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
          body: JSON.stringify({ url: targetUrl })
        })
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            const found = data.email || (data.all_emails?.length > 0 ? data.all_emails[0] : null);
            if (found) setToEmail(found);
          }
        })
        .catch(() => {});
      }
    }
  }, []);

  // Auto-save form draft to localStorage
  useEffect(() => {
    if (!businessName && !websiteUrl && !emailBody) return;
    const currentState = {
      businessName, websiteUrl, industry, locationField, targetAudience, businessGoal, additionalNotes,
      seoScore, sslScore, speedScore, responsiveScore, socialScore, imageScore,
      toEmail, emailBody, selectedSubject, subjectLines
    };
    localStorage.setItem('outreachFormDraft', JSON.stringify(currentState));
  }, [businessName, websiteUrl, industry, locationField, targetAudience, businessGoal, additionalNotes, seoScore, sslScore, speedScore, responsiveScore, socialScore, imageScore, toEmail, emailBody, selectedSubject, subjectLines]);

  async function crawlForEmail() {
    if (!websiteUrl.trim()) { showToast('Enter a website URL first', 'warning'); return; }
    setCrawlingEmail(true);
    try {
      const res = await fetch('/api/v1/businesses/crawl-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
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
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` }, body: JSON.stringify(payload)
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
    const recipient = (toEmail || '').trim();
    const subject = (selectedSubject || '').trim();
    const plainBody = emailBody ? emailBody.replace(/<[^>]*>?/gm, '').trim() : '';

    if (!recipient) {
      showToast('Please enter a recipient email address', 'warning');
      return;
    }
    if (!subject) {
      showToast('Please enter a subject line', 'warning');
      return;
    }
    if (!plainBody) {
      showToast('Please enter email body content', 'warning');
      return;
    }

    setSending(true);
    try {
      const payload = {
        to_email: recipient,
        subject: subject,
        body: plainBody,
        html_body: emailBody
      };
      const res = await fetch('/api/v1/outreach/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('Email sent successfully!', 'success');
        setEmailBody(''); setToEmail(''); setSelectedSubject(''); setSubjectLines([]); setEmailResult(null);
        const editorEl = document.querySelector('[contenteditable]');
        if (editorEl && editorEl._setContent) editorEl._setContent('');
        else if (editorEl) editorEl.innerHTML = '';
      } else {
        let errDetail = 'Send failed';
        try {
          const err = await res.json();
          errDetail = typeof err.detail === 'string' ? err.detail : (err.message || errDetail);
        } catch {
          try {
            const rawText = await res.text();
            if (rawText) errDetail = rawText.slice(0, 100);
          } catch {}
        }
        showToast(errDetail, 'error');
      }
    } catch (e) {
      showToast('Send failed: ' + e.message, 'error');
    } finally {
      setSending(false);
    }
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
              {/* Send From (Centralized Sender) */}
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Send From</label>
                <div className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <span>team@elvionsolutions.com</span>
                  <span className="ml-auto text-xs px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-500 font-bold">Company System Email</span>
                </div>
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

              {/* Subject Line (Freely Editable Input + AI Suggestions) */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3]">Subject Line *</label>
                  {subjectLines.length > 0 && (
                    <span className="text-xs text-[#6D5DF6] dark:text-[#A78BFA] font-medium">AI Suggestions Available</span>
                  )}
                </div>
                <input 
                  type="text"
                  value={selectedSubject} 
                  onChange={e => setSelectedSubject(e.target.value)} 
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" 
                  placeholder="Email subject line..." 
                />
                
                {/* AI Subject Suggestions Pills */}
                {subjectLines.length > 0 && (
                  <div className="mt-2.5 space-y-1.5">
                    <p className="text-[11px] font-medium text-slate-400 dark:text-[#8E8BA3]">Click an AI suggestion to apply:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {subjectLines.map((s, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => setSelectedSubject(s)}
                          className={`text-xs px-2.5 py-1 rounded-md transition-all text-left truncate max-w-full ${
                            selectedSubject === s
                              ? 'bg-[#6D5DF6] text-white font-medium shadow-sm'
                              : 'bg-slate-200/60 dark:bg-white/[0.05] text-slate-700 dark:text-slate-300 hover:bg-[#6D5DF6]/20 dark:hover:bg-[#A78BFA]/20 hover:text-[#6D5DF6] dark:hover:text-[#A78BFA]'
                          }`}
                          title={s}
                        >
                          ✨ {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

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
    </div>
  );
}
