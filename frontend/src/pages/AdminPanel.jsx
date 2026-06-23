import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Users, Trash2, ToggleLeft, ToggleRight, ArrowLeft } from 'lucide-react';

export default function AdminPanel() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [usersRes, statsRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/stats'),
      ]);
      setUsers(usersRes.data);
      setStats(statsRes.data);
    } catch {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const deleteUser = async (id, username) => {
    if (!confirm(`Delete user "${username}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/admin/users/${id}`);
      toast.success('User deleted');
      fetchData();
    } catch {
      toast.error('Failed to delete user');
    }
  };

  const toggleUser = async (id) => {
    try {
      const res = await api.patch(`/admin/users/${id}/toggle-active`);
      toast.success(res.data.message);
      fetchData();
    } catch {
      toast.error('Failed to update user');
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-base)] p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] text-gray-400 hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">Admin Panel</h1>
            <p className="text-gray-400 text-sm">Manage users and view system statistics</p>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: 'Total Users', value: stats.total_users, color: 'text-[var(--text-primary)]' },
              { label: 'Active Users', value: stats.active_users, color: 'text-green-400' },
              { label: 'Calorie Logs', value: stats.total_calorie_logs, color: 'text-orange-400' },
              { label: 'Workout Logs', value: stats.total_workout_logs, color: 'text-blue-400' },
              { label: 'Step Logs', value: stats.total_step_logs, color: 'text-purple-400' },
            ].map(s => (
              <div key={s.label} className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-5 text-center">
                <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-gray-400 text-xs mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Users Table */}
        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] overflow-hidden">
          <div className="p-6 border-b border-[var(--border)] flex items-center gap-2">
            <Users size={18} className="text-purple-400" />
            <h2 className="text-[var(--text-primary)] font-semibold">All Users</h2>
            <span className="ml-auto text-gray-500 text-sm">{users.length} users</span>
          </div>
          {loading ? (
            <div className="p-12 text-center text-gray-500">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    {['ID', 'Username', 'Email', 'Goal', 'Level', 'Status', 'Joined', 'Actions'].map(h => (
                      <th key={h} className="text-left text-xs text-gray-500 font-medium px-6 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-muted)] transition-colors">
                      <td className="px-6 py-4 text-gray-500 text-sm">#{u.id}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-[var(--text-primary)] text-xs font-bold">
                            {u.username?.[0]?.toUpperCase() ?? '?'}
                          </div>
                          <span className="text-[var(--text-primary)] text-sm font-medium">{u.username}</span>
                          {u.is_admin && <span className="text-xs bg-purple-500/20 text-purple-400 px-1.5 py-0.5 rounded">admin</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-400 text-sm">{u.email}</td>
                      <td className="px-6 py-4 text-sm">
                        {u.goal ? (
                          <span className="text-orange-400">{u.goal.replace(/_/g, ' ')}</span>
                        ) : <span className="text-gray-600">—</span>}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {u.fitness_level ? (
                          <span className="text-blue-400">{u.fitness_level}</span>
                        ) : <span className="text-gray-600">—</span>}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          u.is_active
                            ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-500 text-xs">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {u.id !== user?.id && (
                            <>
                              <button
                                onClick={() => toggleUser(u.id)}
                                className="text-gray-400 hover:text-green-400 transition-colors"
                                title={u.is_active ? 'Deactivate' : 'Activate'}
                              >
                                {u.is_active ? <ToggleRight size={18} /> : <ToggleLeft size={18} />}
                              </button>
                              <button
                                onClick={() => deleteUser(u.id, u.username)}
                                className="text-gray-400 hover:text-red-400 transition-colors"
                                title="Delete user"
                              >
                                <Trash2 size={16} />
                              </button>
                            </>
                          )}
                          {u.id === user?.id && <span className="text-gray-600 text-xs">You</span>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
