'use client';

import { useState, useEffect } from 'react';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/ToastProvider';

const API = process.env.NEXT_PUBLIC_API_URL || '';
function getToken() { return typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''; }

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const showToast = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  async function fetchUsers() {
    try {
      const res = await fetch(`${API}/api/v1/admin/users`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      if (res.ok) {
        setUsers(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
    try {
      const res = await fetch(`${API}/api/v1/admin/users/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      if (res.ok) {
        showToast('User deleted successfully', 'success');
        setUsers(users.filter(u => u.id !== id));
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to delete user', 'error');
      }
    } catch (e) {
      showToast('Error deleting user', 'error');
    }
  }

  if (loading) return <div className="flex justify-center p-12"><Spinner className="h-8 w-8 text-[#6D5DF6]" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">User Management</h2>
        <button className="bg-[#6D5DF6] hover:bg-[#5b4ee4] text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
          + Add User
        </button>
      </div>

      <div className="bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-white/5 text-slate-500 dark:text-[#8E8BA3] font-semibold border-b border-slate-200 dark:border-white/10">
              <tr>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Email</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Plan</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-white/10">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900 dark:text-white">{user.full_name}</td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${user.role === 'admin' ? 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300' : 'bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-slate-300'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 uppercase text-xs font-bold text-slate-500">{user.plan}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${user.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => deleteUser(user.id)}
                      className="text-red-500 hover:text-red-700 dark:hover:text-red-400 font-medium px-2 py-1 rounded transition-colors hover:bg-red-50 dark:hover:bg-red-500/10"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">No users found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
