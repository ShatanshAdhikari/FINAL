import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

// "Sign in with Google". Renders the real Google button when a client id is
// configured, otherwise a clearly-disabled placeholder so the UI never breaks.
export default function GoogleSignInButton() {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();

  if (!CLIENT_ID) {
    return (
      <div
        title="Set VITE_GOOGLE_CLIENT_ID in frontend/.env to enable Google sign-in"
        className="w-full text-center py-3 rounded-xl border border-[var(--border-input)] text-gray-500 text-sm cursor-not-allowed select-none"
      >
        Google sign-in not configured
      </div>
    );
  }

  const handleSuccess = async (credentialResponse) => {
    const credential = credentialResponse?.credential;
    if (!credential) {
      toast.error('Google did not return a credential');
      return;
    }
    try {
      const data = await googleLogin(credential);
      toast.success('Signed in with Google 💪');
      const u = data.user;
      const profileComplete = u?.goal && u?.fitness_level && u?.weight;
      navigate(profileComplete ? '/dashboard' : '/onboarding');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Google sign-in failed');
    }
  };

  return (
    <div className="flex justify-center">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => toast.error('Google sign-in was cancelled or failed')}
        theme="filled_black"
        text="continue_with"
        shape="pill"
        width="320"
      />
    </div>
  );
}
