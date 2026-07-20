'use client';

import { useState, useEffect } from 'react';
import { useToast } from '../components/ToastProvider';

export default function SettingsPage() {
  const showToast = useToast();
  const [activeTab, setActiveTab] = useState('api');

  const [apiKeys, setApiKeys] = useState({ groq: '', grok: '', openai: '' });
  const [apiStatus, setApiStatus] = useState({ groq: false, grok: false });
  const [profile, setProfile] = useState({ name: '', email: '', phone: '', title: '' });
  const [company, setCompany] = useState({ name: '', website: '', services: '', usp: '', signature: '' });
  const [templates, setTemplates] = useState([]);
  const [imap, setImap] = useState({ host: '', port: '993', username: '', password: '' });

  useEffect(() => {
    const keys = JSON.parse(localStorage.getItem('settings_apiKeys') || JSON.stringify(apiKeys));
    setApiKeys(keys);
    setApiStatus({ groq: !!keys.groq, grok: !!keys.grok });
    setProfile(JSON.parse(localStorage.getItem('settings_profile') || JSON.stringify(profile)));
    setCompany(JSON.parse(localStorage.getItem('settings_company') || JSON.stringify(company)));
    setTemplates(JSON.parse(localStorage.getItem('settings_templates') || '[]'));
    setImap(JSON.parse(localStorage.getItem('settings_imap') || JSON.stringify({ host: '', port: '993', username: '', password: '' })));
  }, []);

  const saveApiKeys = () => { localStorage.setItem('settings_apiKeys', JSON.stringify(apiKeys)); setApiStatus({ groq: !!apiKeys.groq, grok: !!apiKeys.grok }); showToast('API Keys saved!', 'success'); };
  const saveProfile = () => { localStorage.setItem('settings_profile', JSON.stringify(profile)); showToast('Profile saved!', 'success'); };
  const saveCompany = () => { localStorage.setItem('settings_company', JSON.stringify(company)); showToast('Company saved!', 'success'); };
  const saveTemplates = () => { localStorage.setItem('settings_templates', JSON.stringify(templates)); showToast('Templates saved!', 'success'); };
  const saveImap = () => { localStorage.setItem('settings_imap', JSON.stringify(imap)); showToast('IMAP Settings saved!', 'success'); };

  const addTemplate = () => setTemplates([...templates, { id: Date.now(), name: 'New Template', subject: '', body: '' }]);
  const deleteTemplate = (id) => setTemplates(templates.filter(t => t.id !== id));

  const tabs = [
    { id: 'api', label: 'API Keys', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
    { id: 'profile', label: 'Profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
    { id: 'company', label: 'Company Info', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
    { id: 'templates', label: 'Email Templates', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z' },
    { id: 'email', label: 'Email / IMAP Settings', icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  ];

  return (
    <div>
      <div className="mb-8 flex items-center">
        <div className="w-12 h-12 rounded-xl flex items-center justify-center mr-4">
          <svg className="w-6 h-6 text-slate-500 dark:text-[#8E8BA3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h2>
          <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Configure your account and integrations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-4 border border-slate-200/80 dark:border-white/[0.06] sticky top-4">
            <nav className="space-y-2">
              {tabs.map(tab => (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all flex items-center ${activeTab === tab.id ? 'text-[#6D5DF6] dark:text-[#A78BFA] font-semibold border border-[rgba(96,165,250,0.2)] bg-slate-50 dark:bg-white/[0.03]' : 'text-slate-500 dark:text-[#8E8BA3] hover:bg-slate-50 dark:bg-white/[0.03]'}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-3 ${activeTab === tab.id ? 'text-slate-900 dark:text-white' : 'bg-slate-50 dark:bg-white/[0.03] text-slate-500 dark:text-[#8E8BA3]'}`}>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={tab.icon}></path></svg>
                  </div>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="lg:col-span-2">
          {activeTab === 'api' && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">API Keys</h3>
              <div className="space-y-4">
                <div><label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">Groq API Key</label><input type="password" value={apiKeys.groq} onChange={e => setApiKeys({...apiKeys, groq: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">Grok (X.AI) API Key</label><input type="password" value={apiKeys.grok} onChange={e => setApiKeys({...apiKeys, grok: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">OpenAI API Key (Optional)</label><input type="password" value={apiKeys.openai} onChange={e => setApiKeys({...apiKeys, openai: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" /></div>
                <button onClick={saveApiKeys} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">Save API Keys</button>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Profile</h3>
              <div className="space-y-4">
                <input value={profile.name} onChange={e => setProfile({...profile, name: e.target.value})} placeholder="Full Name" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <input value={profile.email} onChange={e => setProfile({...profile, email: e.target.value})} placeholder="Email" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <input value={profile.phone} onChange={e => setProfile({...profile, phone: e.target.value})} placeholder="Phone" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <input value={profile.title} onChange={e => setProfile({...profile, title: e.target.value})} placeholder="Job Title" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <button onClick={saveProfile} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">Save Profile</button>
              </div>
            </div>
          )}

          {activeTab === 'company' && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Company Info</h3>
              <div className="space-y-4">
                <input value={company.name} onChange={e => setCompany({...company, name: e.target.value})} placeholder="Company Name" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <input value={company.website} onChange={e => setCompany({...company, website: e.target.value})} placeholder="Website" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                <textarea value={company.services} onChange={e => setCompany({...company, services: e.target.value})} placeholder="Services Offered" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" rows="3" />
                <textarea value={company.usp} onChange={e => setCompany({...company, usp: e.target.value})} placeholder="Unique Selling Points" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" rows="2" />
                <textarea value={company.signature} onChange={e => setCompany({...company, signature: e.target.value})} placeholder="Email Signature" className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" rows="4" />
                <button onClick={saveCompany} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">Save Company Info</button>
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">Email Templates</h3>
                <button onClick={addTemplate} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">+ New Template</button>
              </div>
              <div className="space-y-4">
                {templates.map((template, index) => (
                  <div key={template.id} className="border border-slate-200/80 dark:border-white/[0.06] rounded-lg p-4 bg-slate-100 dark:bg-[#08061a]">
                    <div className="flex justify-between items-center mb-2">
                       <input value={template.name} onChange={e => { const nt = [...templates]; nt[index].name = e.target.value; setTemplates(nt); }} className="font-medium bg-transparent border-0 text-lg focus:outline-none" />
                      <button onClick={() => deleteTemplate(template.id)} className="text-red-500 hover:text-red-400">✕</button>
                    </div>
                    <input value={template.subject} onChange={e => { const nt = [...templates]; nt[index].subject = e.target.value; setTemplates(nt); }} placeholder="Subject" className="w-full px-4 py-2 mb-2 bg-white dark:bg-white/[0.015] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm" />
                    <textarea value={template.body} onChange={e => { const nt = [...templates]; nt[index].body = e.target.value; setTemplates(nt); }} placeholder="Body" rows="4" className="w-full px-4 py-2 bg-white dark:bg-white/[0.015] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm" />
                  </div>
                ))}
                {templates.length > 0 && <button onClick={saveTemplates} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">Save All Templates</button>}
              </div>
            </div>
          )}

          {activeTab === 'email' && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06]">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Email / IMAP Settings</h3>
              <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-4">Configure your IMAP settings to retrieve replies in your Inbox.</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">IMAP Host (e.g. imap.gmail.com)</label>
                  <input value={imap.host} onChange={e => setImap({...imap, host: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">IMAP Port</label>
                  <input value={imap.port} onChange={e => setImap({...imap, port: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">IMAP Username / Email Address</label>
                  <input value={imap.username} onChange={e => setImap({...imap, username: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm mb-1 text-slate-500 dark:text-[#8E8BA3]">IMAP Password / App Password</label>
                  <input type="password" value={imap.password} onChange={e => setImap({...imap, password: e.target.value})} className="w-full px-4 py-2 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white" />
                </div>
                <button onClick={saveImap} className="px-4 py-2 bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white rounded-lg text-sm">Save Email Settings</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
