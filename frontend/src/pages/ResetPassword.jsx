import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';
import logoDark from '../assets/logo.png';
import logoLight from '../assets/logo-light.png';
import { validatePassword, isClean } from '../utils/validation';

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get('token') || '';
  const { resetPassword } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();

  const [form, setForm] = useState({ password: '', confirm: '' });
  const [errors, setErrors] = useState({ password: '', confirm: '' });
  const [touched, setTouched] = useState({ password: false, confirm: false });
  const [loading, setLoading] = useState(false);

  const validate = (key, value, all = form) => {
    if (key === 'password') return validatePassword(value);
    if (key === 'confirm') return value !== all.password ? 'Passwords do not match' : '';
    return '';
  };

  const update = (key, value) => {
    const next = { ...form, [key]: value };
    setForm(next);
    setErrors((e) => ({
      ...e,
      [key]: validate(key, value, next),
      // keep confirm in sync when password changes
      confirm: key === 'password' ? validate('confirm', next.confirm, next) : e.confirm,
    }));
  };

  const markTouched = (key) => setTouched((t) => ({ ...t, [key]: true }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const nextErrors = {
      password: validate('password', form.password),
      confirm: validate('confirm', form.confirm),
    };
    setErrors(nextErrors);
    setTouched({ password: true, confirm: true });
    if (!isClean(nextErrors)) return;

    setLoading(true);
    try {
      await resetPassword(token, form.password);
      toast.success('Password updated — you are signed in');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not reset your password');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (key) =>
    `w-full bg-[var(--bg-nested)] border rounded-xl px-4 py-3 text-[var(--text-primary)] text-sm focus:outline-none transition-colors ${
      touched[key] && errors[key]
        ? 'border-red-500 focus:border-red-500'
        : 'border-[var(--border-input)] focus:border-orange-500'
    }`;

  if (!token) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Invalid link</h2>
          <p className="text-gray-400 text-sm mb-6">
            This reset link is missing or malformed. Request a fresh one and use the link
            from that email.
          </p>
          <Link to="/forgot-password" className="text-orange-400 hover:text-orange-300 font-medium text-sm">
            Request a new link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <img src={theme === 'dark' ? logoDark : logoLight} alt="GetFit" className="w-56 rounded-2xl mb-3 p-2" />
          <p className="text-gray-400 text-sm">Choose a new password</p>
        </div>

        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Reset password</h2>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div>
              <label className="block text-sm text-gray-400 mb-1">New password</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => update('password', e.target.value)}
                onBlur={() => markTouched('password')}
                className={inputClass('password')}
                placeholder="At least 8 characters, a letter and a number"
              />
              {touched.password && errors.password && (
                <p className="text-red-400 text-xs mt-1">{errors.password}</p>
              )}
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Confirm new password</label>
              <input
                type="password"
                value={form.confirm}
                onChange={(e) => update('confirm', e.target.value)}
                onBlur={() => markTouched('confirm')}
                className={inputClass('confirm')}
                placeholder="Repeat your new password"
              />
              {touched.confirm && errors.confirm && (
                <p className="text-red-400 text-xs mt-1">{errors.confirm}</p>
              )}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold py-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 mt-2"
            >
              {loading ? 'Updating password...' : 'Update password & sign in'}
            </button>
          </form>

          <p className="text-center text-gray-400 text-sm mt-6">
            Link expired?{' '}
            <Link to="/forgot-password" className="text-orange-400 hover:text-orange-300 font-medium">
              Request a new one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
