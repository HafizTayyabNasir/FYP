'use client';

import { useState, useEffect } from 'react';
import { useToast } from '../components/ToastProvider';
import Spinner from '../components/Spinner';

function getToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token') || '';
  }
  return '';
}

export default function InboxPage() {
  const showToast = useToast();
  const [allEmails, setAllEmails] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [syncing, setSyncing] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');
  const [generatingAI, setGeneratingAI] = useState(false);
  const [sendingReply, setSendingReply] = useState(false);

  useEffect(() => {
    loadAllEmails();
    const interval = setInterval(() => {
      if (!syncing) syncInbox(true);
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  async function loadAllEmails() {
    try {
      const imapSettings = JSON.parse(localStorage.getItem('settings_imap') || '{}');
      let userQ = imapSettings.username ? `&imap_user=${encodeURIComponent(imapSettings.username)}` : '';
      
      const [inboxRes, sentRes] = await Promise.all([
        fetch(`/api/v1/mail/messages?folder=inbox${userQ}`, { headers: { Authorization: `Bearer ${getToken()}` } }),
        fetch(`/api/v1/mail/messages?folder=sent`, { headers: { Authorization: `Bearer ${getToken()}` } })
      ]);
      
      let all = [];
      if (inboxRes.ok) {
        const data = await inboxRes.json();
        const inboxMsgs = (data.messages || []).map(m => ({ ...m, folder: 'inbox' }));
        all = [...all, ...inboxMsgs];
      }
      if (sentRes.ok) {
        const data = await sentRes.json();
        const sentMsgs = (data.messages || []).map(m => ({ ...m, folder: 'sent' }));
        all = [...all, ...sentMsgs];
      }
      
      setAllEmails(all);
      buildConversations(all);
    } catch (e) {
      console.error("Failed to load emails", e);
    }
  }

  function buildConversations(emails) {
    // Deduplicate emails by ID
    const seenIds = new Set();
    const uniqueEmails = [];
    for (const msg of emails) {
      const id = msg.id;
      if (id && seenIds.has(id)) continue;
      if (id) seenIds.add(id);
      uniqueEmails.push(msg);
    }

    const groups = {};
    uniqueEmails.forEach(msg => {
      const isSent = msg.folder === 'sent';
      let contactEmail = isSent ? msg.to_email : msg.from_email;
      if (!contactEmail) contactEmail = isSent ? msg.to_name : msg.from_name;
      if (!contactEmail) return;
      
      const contactEmailLower = contactEmail.toLowerCase().trim();
      const contactName = isSent ? msg.to_name : msg.from_name;
      
      if (!groups[contactEmailLower]) {
        groups[contactEmailLower] = {
          contactEmail: contactEmailLower,
          contactName: contactName || contactEmailLower,
          messages: [],
          lastUpdated: 0,
          unread: 0
        };
      }
      
      if (!msg.read && !isSent) groups[contactEmailLower].unread++;
      groups[contactEmailLower].messages.push(msg);
      
      const msgTime = new Date(msg.date || Date.now()).getTime();
      if (msgTime > groups[contactEmailLower].lastUpdated) {
        groups[contactEmailLower].lastUpdated = msgTime;
        if (contactName && contactName !== contactEmailLower) {
          groups[contactEmailLower].contactName = contactName;
        }
      }
    });
    
    Object.values(groups).forEach(g => {
      g.messages.sort((a, b) => new Date(a.date) - new Date(b.date));
    });
    
    const sorted = Object.values(groups).sort((a, b) => b.lastUpdated - a.lastUpdated);
    setConversations(sorted);
    
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      setFilteredConversations(sorted.filter(c => 
        c.contactName.toLowerCase().includes(q) || c.contactEmail.toLowerCase().includes(q) ||
        c.messages.some(m => (m.subject || '').toLowerCase().includes(q) || (m.body || '').toLowerCase().includes(q))
      ));
    } else {
      setFilteredConversations(sorted);
    }

    if (selectedConversation) {
      const updated = sorted.find(c => c.contactEmail === selectedConversation.contactEmail);
      if (updated) setSelectedConversation(updated);
    }
  }

  useEffect(() => {
    if (!searchQuery) {
      setFilteredConversations(conversations);
      return;
    }
    const q = searchQuery.toLowerCase();
    const delayDebounceFn = setTimeout(() => {
      setFilteredConversations(conversations.filter(c => 
        c.contactName.toLowerCase().includes(q) || c.contactEmail.toLowerCase().includes(q) ||
        c.messages.some(m => (m.subject || '').toLowerCase().includes(q) || (m.body || '').toLowerCase().includes(q))
      ));
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, conversations]);

  async function syncInbox(silent = false) {
    if (!silent) setSyncing(true);
    try {
      const imapSettings = JSON.parse(localStorage.getItem('settings_imap') || '{}');
      const response = await fetch('/api/v1/mail/sync', { 
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
          imap_host: imapSettings.host || null,
          imap_port: imapSettings.port ? parseInt(imapSettings.port) : 993,
          imap_user: imapSettings.username || null,
          imap_password: imapSettings.password || null
        })
      });
      if (response.ok) {
        await loadAllEmails();
        if (!silent) showToast('Inbox synced!', 'success');
      } else if (!silent) {
        const err = await response.json();
        showToast('Sync failed: ' + (err.detail || 'Error'), 'error');
      }
    } catch (error) {
      if (!silent) showToast('Failed to sync inbox', 'error');
    } finally {
      if (!silent) setSyncing(false);
    }
  }

  async function selectConversation(conv) {
    const targetEmail = conv.contactEmail;
    
    // Mark in allEmails
    const updatedEmails = allEmails.map(m => {
      const isSent = m.folder === 'sent';
      const cEmail = (isSent ? m.to_email : m.from_email) || '';
      if (cEmail.toLowerCase().trim() === targetEmail) {
        return { ...m, read: true };
      }
      return m;
    });
    setAllEmails(updatedEmails);

    // Update conversation unread count locally
    const updatedConv = {
      ...conv,
      unread: 0,
      messages: conv.messages.map(m => ({ ...m, read: true }))
    };
    setSelectedConversation(updatedConv);

    setConversations(prev => prev.map(c => c.contactEmail === targetEmail ? updatedConv : c));
    setFilteredConversations(prev => prev.map(c => c.contactEmail === targetEmail ? updatedConv : c));

    setReplyText('');
    setAiPrompt('');
    
    // Auto-scroll chat
    setTimeout(() => {
      const chatBox = document.getElementById('chat-messages');
      if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);

    // Call backend to mark read
    try {
      await fetch('/api/v1/mail/read', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ contact_email: targetEmail })
      });
    } catch (e) {
      console.error("Failed to mark conversation as read", e);
    }
  }

  async function generateReply() {
    const instruction = aiPrompt.trim() || "Draft a professional, friendly response that continues the conversation and naturally leads to securing a meeting or consultation.";
    setGeneratingAI(true);
    try {
      const chatHistory = selectedConversation.messages.map(m => ({
        direction: m.folder === 'sent' ? 'outbound' : 'inbound',
        body: m.body || m.preview || ''
      }));
      
      const response = await fetch('/api/v1/outreach/generate-reply', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ chat_history: chatHistory, prompt_instruction: aiPrompt })
      });
      
      if (response.ok) {
        const data = await response.json();
        setReplyText(data.reply_body);
        showToast('AI reply generated!', 'success');
      } else {
        const err = await response.json();
        showToast('Failed to generate: ' + err.detail, 'error');
      }
    } catch (error) {
      showToast('Error generating AI reply', 'error');
    } finally {
      setGeneratingAI(false);
    }
  }

  async function sendReply() {
    if (!replyText.trim()) return;
    setSendingReply(true);
    try {
      const lastMsg = selectedConversation.messages[selectedConversation.messages.length - 1];
      let sub = lastMsg.subject || 'Follow up';
      if (!sub.toLowerCase().startsWith('re:')) sub = 'Re: ' + sub;
      
      const response = await fetch('/api/v1/outreach/send', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
          to_email: selectedConversation.contactEmail,
          to_name: selectedConversation.contactName,
          subject: sub,
          body: replyText
        })
      });
      
      if (response.ok) {
        showToast('Message sent!', 'success');
        const newMsg = {
          id: Date.now().toString(),
          folder: 'sent',
          date: new Date().toISOString(),
          subject: sub,
          body: replyText,
          to_email: selectedConversation.contactEmail,
          to_name: selectedConversation.contactName,
          read: true
        };
        
        const updatedConv = { ...selectedConversation, messages: [...selectedConversation.messages, newMsg], lastUpdated: Date.now() };
        setSelectedConversation(updatedConv);
        
        const newConvs = conversations.map(c => c.contactEmail === updatedConv.contactEmail ? updatedConv : c).sort((a,b) => b.lastUpdated - a.lastUpdated);
        setConversations(newConvs);
        
        setReplyText('');
        setAiPrompt('');
        setTimeout(() => {
          const chatBox = document.getElementById('chat-messages');
          if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
      } else {
        const err = await response.json();
        showToast('Failed to send: ' + (err.detail || 'Error'), 'error');
      }
    } catch (error) {
      showToast('Failed to send message', 'error');
    } finally {
      setSendingReply(false);
    }
  }

  function formatDate(dateVal) {
    if (!dateVal) return '';
    const date = new Date(dateVal);
    if (date.toDateString() === new Date().toDateString()) return 'Today';
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

  function formatTime(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.06]">
      {/* Conversations Sidebar */}
      <div className="w-80 border-r bg-white dark:bg-white/[0.015] border-slate-200/80 dark:border-white/[0.06] flex flex-col">
        <div className="p-4 border-b border-slate-200/80 dark:border-white/[0.06] bg-white dark:bg-white/[0.015]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white flex items-center justify-center mr-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Messages</h2>
            </div>
            <button onClick={() => syncInbox()} disabled={syncing} className="p-2 text-slate-500 dark:text-[#8E8BA3] hover:text-[#6D5DF6] dark:text-[#A78BFA] hover:bg-[#6D5DF6]/10 dark:bg-[#A78BFA]/10 rounded-lg transition-all">
              <svg className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
          </div>
          <div className="relative mt-2">
            <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500 dark:text-[#8E8BA3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 pl-10 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="Search chats..." />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#060518]">
          {filteredConversations.map(conv => (
            <div key={conv.contactEmail} onClick={() => selectConversation(conv)}
              className={`p-4 border-b border-slate-200/80 dark:border-white/[0.06] cursor-pointer transition-all duration-200 ${
                selectedConversation?.contactEmail === conv.contactEmail ? 'bg-slate-200/50 dark:bg-[#6D5DF6]/10 border-l-4 border-l-[#6D5DF6] dark:border-l-[#A78BFA]' : 'hover:bg-slate-50 dark:bg-white/[0.03]'
              }`}>
              <div className="flex items-center justify-between mb-1">
                <p className={`text-sm truncate font-semibold ${conv.unread > 0 ? 'text-slate-900 dark:text-white' : 'text-slate-900 dark:text-white'}`}>{conv.contactName}</p>
                <span className="text-xs text-slate-500 dark:text-[#8E8BA3] ml-2 shrink-0">{formatDate(conv.lastUpdated)}</span>
              </div>
              {conv.contactName !== conv.contactEmail && <p className="text-xs text-[#6D5DF6] dark:text-[#A78BFA] truncate mb-1">{conv.contactEmail}</p>}
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-slate-500 dark:text-[#8E8BA3] truncate max-w-[80%]">{conv.messages[conv.messages.length - 1]?.subject || 'No Subject'}</p>
                {conv.unread > 0 && <span className="bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white text-[10px] font-bold px-2 py-0.5 rounded-full">{conv.unread}</span>}
              </div>
            </div>
          ))}
          {filteredConversations.length === 0 && (
            <div className="p-8 text-center text-slate-500 dark:text-[#8E8BA3]">
              <p className="font-medium">No messages found</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Chat Interface */}
      <div className="flex-1 flex flex-col bg-slate-100 dark:bg-[#08061a]">
        {selectedConversation ? (
          <div className="flex-1 flex flex-col h-full">
            {/* Header */}
            <div className="bg-white dark:bg-white/[0.015] border-b border-slate-200/80 dark:border-white/[0.06] p-4 flex items-center justify-between shadow-sm z-10">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-[#6D5DF6] dark:bg-[#6D5DF6]/20 text-[#6D5DF6] dark:text-[#A78BFA] flex items-center justify-center text-lg font-bold mr-3 border border-[#6D5DF6] dark:border-[#A78BFA]/30">
                  {selectedConversation.contactName[0].toUpperCase()}
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-white leading-tight">{selectedConversation.contactName}</h3>
                  <p className="text-xs text-slate-500 dark:text-[#8E8BA3]">{selectedConversation.contactEmail}</p>
                </div>
              </div>
            </div>
            
            {/* Messages */}
            <div id="chat-messages" className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50 dark:bg-[#060518]">
              {selectedConversation.messages.map(msg => (
                <div key={msg.id} className={`flex flex-col ${msg.folder === 'sent' ? 'items-end' : 'items-start'}`}>
                  <div className="max-w-[80%]">
                    <div className={`flex items-center mb-1 px-1 ${msg.folder === 'sent' ? 'justify-end' : 'justify-start'}`}>
                      <span className="text-xs text-slate-500 dark:text-[#8E8BA3]">{msg.folder === 'sent' ? 'You' : msg.from_name || msg.from_email}</span>
                      <span className="text-xs text-slate-500 dark:text-[#8E8BA3] mx-1">•</span>
                      <span className="text-xs text-slate-500 dark:text-[#8E8BA3]">{formatDate(msg.date)} at {formatTime(msg.date)}</span>
                    </div>
                    <div className={`p-4 rounded-2xl shadow-sm border ${
                      msg.folder === 'sent' 
                        ? 'bg-slate-200 dark:bg-[#6D5DF6]/20 border-slate-300 dark:border-[#6D5DF6]/20 text-slate-900 dark:text-white rounded-tr-sm' 
                        : 'bg-white dark:bg-white/[0.015] border-slate-200/80 dark:border-white/[0.06] text-slate-900 dark:text-white rounded-tl-sm'
                    }`}>
                      {msg.subject && (
                        <div className={`mb-2 pb-2 border-b ${msg.folder === 'sent' ? 'border-slate-300 dark:border-[#6D5DF6]/20' : 'border-slate-200/80 dark:border-white/[0.06]'}`}>
                          <p className="text-sm font-semibold opacity-90">Subj: {msg.subject}</p>
                        </div>
                      )}
                      <div className="text-sm whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={{ __html: msg.body?.replace(/\n/g, '<br>').replace(/  /g, '&nbsp;&nbsp;') }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Compose */}
            <div className="bg-white dark:bg-white/[0.015] border-t border-slate-200/80 dark:border-white/[0.06] p-4">
              <div className="flex gap-2 mb-3 items-center">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-4 w-4 text-[#A78BFA]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <input type="text" value={aiPrompt} onChange={e => setAiPrompt(e.target.value)} onKeyDown={e => e.key === 'Enter' && generateReply()}
                    placeholder="Instruct AI... (e.g. 'Politely say yes')" 
                    className="w-full px-4 py-2 pl-9 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" />
                </div>
                <button onClick={generateReply} disabled={generatingAI} className="px-4 py-2 text-sm border border-[#6D5DF6] dark:border-[#A78BFA] text-[#A78BFA] hover:bg-[#6D5DF6]/10 dark:hover:bg-[#A78BFA]/10 rounded-lg whitespace-nowrap flex items-center disabled:opacity-50">
                  {generatingAI ? <Spinner className="mr-2 h-4 w-4" /> : null}
                  {generatingAI ? 'Generating...' : 'Generate with AI'}
                </button>
              </div>
              <textarea value={replyText} onChange={e => setReplyText(e.target.value)} 
                className="w-full px-4 py-3 min-h-[120px] bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm mb-3 focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] resize-y" 
                placeholder="Write your reply..."></textarea>
              <div className="flex justify-between items-center">
                <button onClick={() => { setReplyText(''); setAiPrompt(''); }} className="text-slate-500 dark:text-[#8E8BA3] text-sm hover:text-red-400">Clear</button>
                <button onClick={sendReply} disabled={sendingReply || !replyText.trim()} className="bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-medium py-2 px-4 rounded-lg flex items-center disabled:opacity-50 text-sm">
                  {sendingReply ? <Spinner className="mr-2 h-4 w-4" /> : (
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                    </svg>
                  )}
                  {sendingReply ? 'Sending...' : 'Send Message'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500 dark:text-[#8E8BA3] bg-slate-50 dark:bg-[#060518]">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-white dark:bg-white/[0.015] flex items-center justify-center border border-slate-200/80 dark:border-white/[0.06] shadow-sm">
                <svg className="w-10 h-10 text-slate-500 dark:text-[#8E8BA3] opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <p className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Your Messages</p>
              <p className="text-sm">Select a conversation from the left to start chatting.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
