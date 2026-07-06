import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import WorkoutPlan from './pages/WorkoutPlan';
import CalorieTracker from './pages/CalorieTracker';
import StepTracker from './pages/StepTracker';
import Profile from './pages/Profile';
import AdminPanel from './pages/AdminPanel';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  return children;
}

function AdminRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (!user.is_admin) return <Navigate to="/dashboard" />;
  return children;
}

function PublicRoute({ children }) {
  const { user } = useAuth();
  if (user) {
    // A freshly-registered user has no profile yet — send them to onboarding,
    // not the dashboard. This also makes the destination agree with Register's
    // own navigate('/onboarding'), avoiding a redirect race that skipped onboarding.
    const profileComplete = user.goal && user.fitness_level && user.weight;
    return <Navigate to={profileComplete ? '/dashboard' : '/onboarding'} />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#1a1a2e', color: '#f1f1f1', border: '1px solid #333' },
          }}
        />
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
          <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
            <Route path="/workout" element={<ErrorBoundary><WorkoutPlan /></ErrorBoundary>} />
            <Route path="/calories" element={<ErrorBoundary><CalorieTracker /></ErrorBoundary>} />
            <Route path="/steps" element={<ErrorBoundary><StepTracker /></ErrorBoundary>} />
            <Route path="/profile" element={<ErrorBoundary><Profile /></ErrorBoundary>} />
          </Route>
          <Route path="/admin" element={<AdminRoute><ErrorBoundary><AdminPanel /></ErrorBoundary></AdminRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
