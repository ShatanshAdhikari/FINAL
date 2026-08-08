import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';
import logoDark from '../assets/logo.png';
import logoLight from '../assets/logo-light.png';
import { validateEmail } from '../utils/validation';

export default function ForgotPassword() {
  const { forgotPassword } = useAuth();
  const { theme } = useTheme();

  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const err = validateEmail(email);
    setError(err);
    setTouched(true);
    if (err) return;

    setLoading(true);
    try {
      await forgotPassword(email.trim());
      // The backend answers identically for unknown addresses, so the UI must
      // stay just as vague — anything more would leak which emails are registered.
      setSent(true);
    } catch (err2) {
      toast.error(err2.response?.data?.detail || 'Could not send the reset link');
    } finally {
      setLoading(false);
    }
  };

  const logo = theme === 'dark' ? logoDark : logoLight;

  if (sent) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
          <div className="text-5xl mb-4">📧</div>
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Check your email</h2>
          <p className="text-gray-400 text-sm mb-6">
            If an account exists for <span className="text-[var(--text-primary)]">{email.trim()}</span>,
            we've sent a link to reset your password. It expires in an hour and works once.
          </p>
          <Link to="/login" className="text-orange-400 hover:text-orange-300 font-medium text-sm">
            Back to Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-base)] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <img src={logo} alt="GetFit" className="w-56 rounded-2xl mb-3 p-2" />
          <p className="text-gray-400 text-sm">We'll email you a link to get back in</p>
        </div>

        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-8">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Forgot password</h2>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError(validateEmail(e.target.value));
                }}
                onBlur={() => setTouched(true)}
                className={`w-full bg-[var(--bg-nested)] border rounded-xl px-4 py-3 text-[var(--text-primary)] text-sm focus:outline-none transition-colors ${
                  touched && error
                    ? 'border-red-500 focus:border-red-500'
                    : 'border-[var(--border-input)] focus:border-orange-500'
                }`}
                placeholder="The email you signed up with"
              />
              {touched && error && <p className="text-red-400 text-xs mt-1">{error}</p>}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold py-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 mt-2"
            >
              {loading ? 'Sending link...' : 'Send reset link'}
            </button>
          </form>

          <p className="text-center text-gray-400 text-sm mt-6">
            Remembered it?{' '}
            <Link to="/login" className="text-orange-400 hover:text-orange-300 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
