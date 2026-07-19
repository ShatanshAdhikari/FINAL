import axios from 'axios';

// Dev: unset → '/api', which Vite proxies to the local backend.
// Prod (Vercel): VITE_API_BASE = full Render backend URL, e.g.
//   https://getfit-api.onrender.com  → requests go cross-origin directly.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401 — but NOT during the login request itself
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const isAuthEndpoint = error.config?.url?.startsWith('/auth/');
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
