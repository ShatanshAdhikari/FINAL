import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Users, Trash2, ToggleLeft, ToggleRight, ArrowLeft, ShieldPlus, ShieldMinus, ShieldCheck, ShieldX } from 'lucide-react';

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
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to delete user');
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

  const promoteAdmin = async (id, username) => {
    try {
      await api.patch(`/admin/users/${id}/promote-admin`);
      toast.success(`${username} promoted to admin`);
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to promote user');
    }
  };

  const demoteAdmin = async (id, username) => {
    if (!confirm(`Remove admin role from "${username}"?`)) return;
    try {
      await api.patch(`/admin/users/${id}/demote-admin`);
      toast.success(`${username} demoted to regular user`);
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to demote user');
    }
  };

  const promoteSuperAdmin = async (id, username) => {
    if (!confirm(`Promote "${username}" to super-admin? This grants full control.`)) return;
    try {
      await api.patch(`/admin/users/${id}/promote-super-admin`);
      toast.success(`${username} promoted to super-admin`);
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to promote user');
    }
  };

  const demoteSuperAdmin = async (id, username) => {
    if (!confirm(`Demote "${username}" from super-admin to admin?`)) return;
    try {
      await api.patch(`/admin/users/${id}/demote-super-admin`);
      toast.success(`${username} demoted to admin`);
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to demote user');
    }
  };

  const RoleBadge = ({ u }) => {
    if (u.is_super_admin) return (
      <span className="text-xs bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-1.5 py-0.5 rounded">super-admin</span>
    );
    if (u.is_admin) return (
      <span className="text-xs bg-purple-500/20 text-purple-400 border border-purple-500/30 px-1.5 py-0.5 rounded">admin</span>
    );
    return (
      <span className="text-xs bg-[var(--bg-muted)] text-gray-500 border border-[var(--border)] px-1.5 py-0.5 rounded">user</span>
    );
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
            <p className="text-gray-400 text-sm">
              {user?.is_super_admin ? 'Super Admin — full role management enabled' : 'Admin — manage users and view statistics'}
            </p>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Users',    value: stats.total_users,         color: 'text-[var(--text-primary)]' },
              { label: 'Active Users',   value: stats.active_users,        color: 'text-green-400'  },
              { label: 'Admins',         value: stats.admin_users,         color: 'text-purple-400' },
              { label: 'Super Admins',   value: stats.super_admin_users,   color: 'text-yellow-400' },
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
                    {['ID', 'Username', 'Email', 'Role', 'Status', 'Joined', 'Actions'].map(h => (
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
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-white text-xs font-bold">
                            {u.username?.[0]?.toUpperCase() ?? '?'}
                          </div>
                          <span className="text-[var(--text-primary)] text-sm font-medium">{u.username}</span>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-gray-400 text-sm">{u.email}</td>

                      <td className="px-6 py-4">
                        <RoleBadge u={u} />
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
                        {u.id === user?.id ? (
                          <span className="text-gray-600 text-xs">You</span>
                        ) : (
                          <div className="flex items-center gap-2">
                            {/* Active toggle — admins can do this */}
                            {!u.is_super_admin && (
                              <button
                                onClick={() => toggleUser(u.id)}
                                className="text-gray-400 hover:text-green-400 transition-colors"
                                title={u.is_active ? 'Deactivate' : 'Activate'}
                              >
                                {u.is_active ? <ToggleRight size={18} /> : <ToggleLeft size={18} />}
                              </button>
                            )}

                            {/* Role management — super-admins only */}
                            {user?.is_super_admin && (
                              <>
                                {!u.is_admin && !u.is_super_admin && (
                                  <button
                                    onClick={() => promoteAdmin(u.id, u.username)}
                                    className="text-gray-400 hover:text-purple-400 transition-colors"
                                    title="Promote to admin"
                                  >
                                    <ShieldPlus size={16} />
                                  </button>
                                )}
                                {u.is_admin && !u.is_super_admin && (
                                  <>
                                    <button
                                      onClick={() => demoteAdmin(u.id, u.username)}
                                      className="text-gray-400 hover:text-orange-400 transition-colors"
                                      title="Remove admin role"
                                    >
                                      <ShieldMinus size={16} />
                                    </button>
                                    <button
                                      onClick={() => promoteSuperAdmin(u.id, u.username)}
                                      className="text-gray-400 hover:text-yellow-400 transition-colors"
                                      title="Promote to super-admin"
                                    >
                                      <ShieldCheck size={16} />
                                    </button>
                                  </>
                                )}
                                {u.is_super_admin && (
                                  <button
                                    onClick={() => demoteSuperAdmin(u.id, u.username)}
                                    className="text-gray-400 hover:text-yellow-400 transition-colors"
                                    title="Demote to admin"
                                  >
                                    <ShieldX size={16} />
                                  </button>
                                )}
                              </>
                            )}

                            {/* Delete — admins can delete users, super-admins can delete admins */}
                            {!u.is_super_admin && (user?.is_super_admin || !u.is_admin) && (
                              <button
                                onClick={() => deleteUser(u.id, u.username)}
                                className="text-gray-400 hover:text-red-400 transition-colors"
                                title="Delete user"
                              >
                                <Trash2 size={16} />
                              </button>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Role legend — only shown to super admins */}
        {user?.is_super_admin && (
          <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-5">
            <h3 className="text-[var(--text-primary)] font-semibold text-sm mb-3">Role Management Guide</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-400">
              <div className="flex items-center gap-2"><ShieldPlus size={14} className="text-purple-400" /> Promote regular user to admin</div>
              <div className="flex items-center gap-2"><ShieldMinus size={14} className="text-orange-400" /> Remove admin role (back to user)</div>
              <div className="flex items-center gap-2"><ShieldCheck size={14} className="text-yellow-400" /> Promote admin to super-admin</div>
              <div className="flex items-center gap-2"><ShieldX size={14} className="text-yellow-400" /> Demote super-admin back to admin</div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
