import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { User, Save, Sun, Moon } from 'lucide-react';

const goals = ['fat_loss', 'muscle_gain', 'strength', 'endurance'];
const levels = ['beginner', 'intermediate', 'advanced'];
const activityLevels = ['sedentary', 'light', 'moderate', 'active', 'very_active'];

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const { theme, toggle } = useTheme();
  const [form, setForm] = useState({
    age: '', gender: 'male', weight: '', height: '',
    fitness_level: '', goal: '', activity_level: '',
    workout_frequency: 3, equipment: '',
  });
  const [loading, setLoading] = useState(false);
  const [nutritionPlan, setNutritionPlan] = useState(null);

  useEffect(() => {
    if (user) {
      setForm({
        age: user.age || '',
        gender: user.gender || 'male',
        weight: user.weight || '',
        height: user.height || '',
        fitness_level: user.fitness_level || '',
        goal: user.goal || '',
        activity_level: user.activity_level || '',
        workout_frequency: user.workout_frequency || 3,
        equipment: user.equipment || '',
      });
    }
    void api.get('/profile/nutrition-plan').then(r => setNutritionPlan(r.data)).catch(() => {});
  }, [user]);

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.put('/profile/', {
        ...form,
        age: form.age ? parseInt(form.age) : undefined,
        weight: form.weight ? parseFloat(form.weight) : undefined,
        height: form.height ? parseFloat(form.height) : undefined,
        workout_frequency: parseInt(form.workout_frequency),
      });
      await refreshUser();
      toast.success('Profile saved!');
      void api.get('/profile/nutrition-plan').then(r => setNutritionPlan(r.data)).catch(() => {});
    } catch {
      toast.error('Failed to save');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Profile</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your personal information and fitness settings</p>
      </div>

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6 flex items-center gap-4">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-[var(--text-primary)] text-3xl font-bold">
          {user?.username?.[0]?.toUpperCase()}
        </div>
        <div>
          <div className="text-[var(--text-primary)] font-bold text-xl">{user?.username}</div>
          <div className="text-gray-400 text-sm">{user?.email}</div>
          {user?.is_admin && (
            <span className="mt-1 inline-block px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded-lg border border-purple-500/30">
              Admin
            </span>
          )}
        </div>
      </div>

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
        <h2 className="text-[var(--text-primary)] font-semibold mb-4">Appearance</h2>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {theme === 'dark'
              ? <Moon size={18} className="text-orange-400" />
              : <Sun size={18} className="text-orange-400" />}
            <div>
              <div className="text-[var(--text-primary)] text-sm font-medium">Theme</div>
              <div className="text-gray-400 text-xs">{theme === 'dark' ? 'Dark mode' : 'Light mode'}</div>
            </div>
          </div>
          <button
            onClick={toggle}
            aria-label="Toggle theme"
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-[var(--bg-muted)] text-[var(--text-primary)] hover:opacity-90 transition-opacity"
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            Switch to {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
        </div>
      </div>

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
        <h2 className="text-[var(--text-primary)] font-semibold mb-4 flex items-center gap-2">
          <User size={18} className="text-orange-400" /> Personal Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Age</label>
            <input type="number" value={form.age} onChange={e => update('age', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500" placeholder="25" />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Gender</label>
            <select value={form.gender} onChange={e => update('gender', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500">
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Weight (kg)</label>
            <input type="number" value={form.weight} onChange={e => update('weight', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500" placeholder="70" />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Height (cm)</label>
            <input type="number" value={form.height} onChange={e => update('height', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500" placeholder="175" />
          </div>
        </div>
      </div>

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
        <h2 className="text-[var(--text-primary)] font-semibold mb-4">Fitness Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Goal</label>
            <select value={form.goal} onChange={e => update('goal', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500">
              <option value="">Select goal</option>
              {goals.map(g => <option key={g} value={g}>{g.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Fitness Level</label>
            <select value={form.fitness_level} onChange={e => update('fitness_level', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500">
              <option value="">Select level</option>
              {levels.map(l => <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Activity Level</label>
            <select value={form.activity_level} onChange={e => update('activity_level', e.target.value)}
              className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500">
              <option value="">Select activity level</option>
              {activityLevels.map(a => <option key={a} value={a}>{a.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-2">
              Workout Days/Week: <span className="text-orange-400 font-bold">{form.workout_frequency}</span>
            </label>
            <input type="range" min="1" max="7" value={form.workout_frequency}
              onChange={e => update('workout_frequency', e.target.value)}
              className="w-full accent-orange-500 mt-1" />
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={loading}
          className="mt-6 flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-red-600 text-[var(--text-primary)] font-semibold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <Save size={16} />
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {nutritionPlan && (
        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <h2 className="text-[var(--text-primary)] font-semibold mb-4">Your Nutrition Plan</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'BMR', value: `${nutritionPlan.bmr} kcal` },
              { label: 'TDEE', value: `${nutritionPlan.tdee} kcal` },
              { label: 'Daily Goal', value: `${nutritionPlan.calorie_goal} kcal` },
              { label: 'Protein', value: `${nutritionPlan.macros.protein_g}g` },
            ].map(item => (
              <div key={item.label} className="bg-[var(--bg-nested)] rounded-xl p-4 text-center">
                <div className="text-gray-400 text-xs mb-1">{item.label}</div>
                <div className="text-[var(--text-primary)] font-bold">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
