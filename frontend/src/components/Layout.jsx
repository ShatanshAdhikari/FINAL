import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  LayoutDashboard, Dumbbell, Apple, Footprints, User, LogOut, Shield
} from 'lucide-react';
import logoDark from '../assets/logo.png';
import logoLight from '../assets/logo-light.png';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workout',   icon: Dumbbell,         label: 'Workout'   },
  { to: '/calories',  icon: Apple,             label: 'Calories'  },
  { to: '/steps',     icon: Footprints,        label: 'Steps'     },
  { to: '/profile',   icon: User,              label: 'Profile'   },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-[var(--bg-base)]">

      {/* ── Desktop Sidebar ───────────────────────────────── */}
      <aside className="hidden md:flex w-64 bg-[var(--bg-surface)] border-r border-[var(--border)] flex-col fixed h-full z-10">
        {/* Logo */}
        <div className="p-4 border-b border-[var(--border)] flex items-center justify-center">
          <img src={theme === 'dark' ? logoDark : logoLight} alt="GetFit" className="w-48 rounded-xl p-2" />
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                    : 'text-gray-400 hover:bg-[var(--bg-muted)] hover:text-[var(--text-primary)]'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}

          {user?.is_admin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                    : 'text-gray-400 hover:bg-[var(--bg-muted)] hover:text-[var(--text-primary)]'
                }`
              }
            >
              <Shield size={18} />
              Admin Panel
            </NavLink>
          )}
        </nav>

        {/* User info + logout */}
        <div className="p-4 border-t border-[var(--border)]">
          <div className="flex items-center gap-3 mb-3 px-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-[var(--text-primary)] text-sm font-bold">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[var(--text-primary)] text-sm font-medium truncate">{user?.username}</p>
              <p className="text-gray-500 text-xs truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-xl text-sm text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-all"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* ── Main Content ──────────────────────────────────── */}
      {/* pb-20 on mobile so content doesn't hide behind bottom nav */}
      <main className="flex-1 md:ml-64 p-4 md:p-8 pb-24 md:pb-8 overflow-y-auto min-h-screen">
        <Outlet />
      </main>

      {/* ── Mobile Bottom Nav Bar ─────────────────────────── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-20 bg-[var(--bg-surface)] border-t border-[var(--border)]">
        <div className="flex items-center justify-around px-1 py-2">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl text-[10px] font-medium transition-all min-w-0 ${
                  isActive ? 'text-orange-400' : 'text-gray-500'
                }`
              }
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}

          {user?.is_admin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl text-[10px] font-medium transition-all ${
                  isActive ? 'text-purple-400' : 'text-gray-500'
                }`
              }
            >
              <Shield size={20} />
              <span>Admin</span>
            </NavLink>
          )}

          <button
            onClick={handleLogout}
            className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl text-[10px] font-medium text-gray-500 hover:text-red-400 transition-all"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </nav>

    </div>
  );
}
