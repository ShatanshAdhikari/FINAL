import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import logo from '../assets/logo.png';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { validateEmail, validateUsername, isClean } from '../utils/validation';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '' });
  const [errors, setErrors] = useState({ email: '', username: '' });
  const [touched, setTouched] = useState({ email: false, username: false });
  const [loading, setLoading] = useState(false);
  const [sentTo, setSentTo] = useState(null);   // email address once registered
  const { register } = useAuth();

  const validators = { email: validateEmail, username: validateUsername };

  const update = (key, value) => {
    setForm((f) => ({ ...f, [key]: value }));
    setErrors((e) => ({ ...e, [key]: validators[key](value) }));
  };

  const markTouched = (key) => setTouched((t) => ({ ...t, [key]: true }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const nextErrors = {
      email: validateEmail(form.email),
      username: validateUsername(form.username),
    };
    setErrors(nextErrors);
    setTouched({ email: true, username: true });
    if (!isClean(nextErrors)) return;

    setLoading(true);
    try {
      const res = await register(form.email.trim(), form.username.trim());
      setSentTo(res.email || form.email.trim());
      if (res.email_sent === false) {
        toast('Dev mode: check the backend log for your set-password link', { icon: '📧' });
      } else {
        toast.success('Confirmation email sent 📧');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
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

  // Success screen after registration.
  if (sentTo) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center">
          <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
            <div className="text-5xl mb-4">📧</div>
            <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Check your email</h2>
            <p className="text-gray-400 text-sm mb-6">
              We sent a confirmation link to <span className="text-orange-400">{sentTo}</span>.
              Click it to set your password and activate your account.
            </p>
            <p className="text-gray-500 text-xs mb-6">
              The link expires in 24 hours. Don't see it? Check your spam folder.
            </p>
            <Link
              to="/login"
              className="inline-block w-full bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold py-3 rounded-xl hover:opacity-90 transition-opacity"
            >
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <img src={logo} alt="GetFit" className="w-56 rounded-2xl mb-3 bg-[var(--bg-base)] p-2" />
          <p className="text-gray-400 text-sm">Start your fitness journey today</p>
        </div>

        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Create Account</h2>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => update('email', e.target.value)}
                onBlur={() => markTouched('email')}
                className={inputClass('email')}
                placeholder="your@email.com"
              />
              {touched.email && errors.email && (
                <p className="text-red-400 text-xs mt-1">{errors.email}</p>
              )}
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Username</label>
              <input
                type="text"
                value={form.username}
                onChange={(e) => update('username', e.target.value)}
                onBlur={() => markTouched('username')}
                className={inputClass('username')}
                placeholder="Choose a username"
              />
              {touched.username && errors.username && (
                <p className="text-red-400 text-xs mt-1">{errors.username}</p>
              )}
            </div>
            <p className="text-gray-500 text-xs">
              You'll set your password from a link we email you.
            </p>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold py-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 mt-2"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-[var(--border)]" />
            <span className="text-gray-500 text-xs">or</span>
            <div className="flex-1 h-px bg-[var(--border)]" />
          </div>
          <GoogleSignInButton />

          <p className="text-center text-gray-400 text-sm mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-orange-400 hover:text-orange-300 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
