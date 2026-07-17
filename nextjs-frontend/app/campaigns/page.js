'use client';

import { useState, useEffect } from 'react';
import { useToast } from '../components/ToastProvider';
import Spinner from '../components/Spinner';

export default function CampaignsPage() {
  const showToast = useToast();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({ name: '', description: '', status: 'draft' });
  const [creating, setCreating] = useState(false);

  useEffect(() => { loadCampaigns(); }, []);

  async function loadCampaigns() {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/campaigns');
      if (res.ok) {
        const data = await res.json();
        setCampaigns(data.campaigns || data || []);
      }
    } catch (e) { console.error('Failed to load campaigns:', e); }
    finally { setLoading(false); }
  }

  async function createCampaign() {
    if (!createForm.name.trim()) { showToast('Enter a campaign name', 'warning'); return; }
    setCreating(true);
    try {
      const res = await fetch('/api/v1/campaigns', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createForm)
      });
      if (res.ok) {
        showToast('Campaign created!', 'success');
        setShowCreateModal(false);
        setCreateForm({ name: '', description: '', status: 'draft' });
        loadCampaigns();
      } else { const err = await res.json(); showToast(err.detail || 'Failed', 'error'); }
    } catch (e) { showToast('Failed: ' + e.message, 'error'); }
    finally { setCreating(false); }
  }

  async function deleteCampaign(id) {
    if (!confirm('Delete this campaign?')) return;
    try {
      const res = await fetch(`/api/v1/campaigns/${id}`, { method: 'DELETE' });
      if (res.ok) { showToast('Campaign deleted', 'success'); loadCampaigns(); }
      else showToast('Delete failed', 'error');
    } catch { showToast('Delete failed', 'error'); }
  }

  async function updateStatus(id, status) {
    try {
      const res = await fetch(`/api/v1/campaigns/${id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (res.ok) { showToast('Status updated', 'success'); loadCampaigns(); }
      else showToast('Update failed', 'error');
    } catch { showToast('Update failed', 'error'); }
  }

  const statusColors = {
    draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    paused: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Campaigns</h2>
          <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">Manage your outreach campaigns</p>
        </div>
      </div>

      {/* Campaign Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total', value: campaigns.length, color: 'text-[#6D5DF6] dark:text-[#A78BFA]' },
          { label: 'Active', value: campaigns.filter(c => c.status === 'active').length, color: 'text-emerald-400' },
          { label: 'Draft', value: campaigns.filter(c => c.status === 'draft').length, color: 'text-gray-400' },
          { label: 'Completed', value: campaigns.filter(c => c.status === 'completed').length, color: 'text-blue-400' },
        ].map((s, i) => (
          <div key={i} className="bg-white dark:bg-white/[0.015] rounded-xl p-4 border border-slate-200/80 dark:border-white/[0.06]">
            <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">{s.label}</p>
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Campaigns List */}
      <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
        {loading ? (
          <div className="text-center py-12 text-slate-500 dark:text-[#8E8BA3] flex items-center justify-center"><Spinner className="mr-2 h-5 w-5" /> Loading...</div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-12 text-slate-500 dark:text-[#8E8BA3]">
            <p className="text-lg font-medium mb-2">No campaigns yet</p>
            <p className="text-sm mb-4">Create your first outreach campaign</p>
            <button onClick={() => setShowCreateModal(true)} className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] font-medium">+ Create Campaign</button>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map(campaign => (
              <div key={campaign.id} className="bg-slate-100 dark:bg-[#08061a] rounded-lg p-5 border border-slate-200/80 dark:border-white/[0.06] hover:border-[#6D5DF6] dark:border-[#A78BFA]/30 transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-semibold text-slate-900 dark:text-white text-lg">{campaign.name}</h4>
                      <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColors[campaign.status] || statusColors.draft}`}>
                        {campaign.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500 dark:text-[#8E8BA3]">{campaign.description || 'No description'}</p>
                    <p className="text-xs text-slate-500 dark:text-[#8E8BA3] mt-2">Created: {new Date(campaign.created_at || Date.now()).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <select value={campaign.status} onChange={e => updateStatus(campaign.id, e.target.value)}
                      className="px-3 py-1.5 bg-white dark:bg-white/[0.015] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white text-sm focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]">
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="paused">Paused</option>
                      <option value="completed">Completed</option>
                    </select>
                    <button onClick={() => deleteCampaign(campaign.id)} className="p-2 text-red-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] w-full max-w-md shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Create Campaign</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Campaign Name *</label>
                <input value={createForm.name} onChange={e => setCreateForm(p => ({ ...p, name: e.target.value }))}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="My Campaign" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Description</label>
                <textarea value={createForm.description} onChange={e => setCreateForm(p => ({ ...p, description: e.target.value }))} rows="3"
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]" placeholder="Campaign description..." />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-sm text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white">Cancel</button>
              <button onClick={createCampaign} disabled={creating} className="bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm disabled:opacity-50">
                {creating ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
