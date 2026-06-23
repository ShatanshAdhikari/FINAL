import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import toast from 'react-hot-toast';

const steps = ['Personal Info', 'Fitness Goals', 'Workout Preferences'];

const goals = [
  { value: 'fat_loss', label: '🔥 Fat Loss', desc: 'Burn fat and get lean' },
  { value: 'muscle_gain', label: '💪 Muscle Gain', desc: 'Build muscle and size' },
  { value: 'strength', label: '🏋️ Strength', desc: 'Get stronger and powerful' },
  { value: 'endurance', label: '🏃 Endurance', desc: 'Improve stamina and cardio' },
];

const levels = [
  { value: 'beginner', label: 'Beginner', desc: 'Less than 1 year of training' },
  { value: 'intermediate', label: 'Intermediate', desc: '1-3 years of training' },
  { value: 'advanced', label: 'Advanced', desc: '3+ years of consistent training' },
];

const activityLevels = [
  { value: 'sedentary', label: 'Sedentary', desc: 'Little or no exercise' },
  { value: 'light', label: 'Light', desc: '1-3 days/week' },
  { value: 'moderate', label: 'Moderate', desc: '3-5 days/week' },
  { value: 'active', label: 'Active', desc: '6-7 days/week' },
  { value: 'very_active', label: 'Very Active', desc: 'Athlete/physical job' },
];

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const { refreshUser } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    age: '', gender: 'male', weight: '', height: '',
    goal: '', fitness_level: '', activity_level: '',
    workout_frequency: 3, equipment: 'none',
  });

  const update = (key, val) => setForm(prev => ({ ...prev, [key]: val }));

  const handleFinish = async () => {
    setLoading(true);
    if (!form.activity_level) {
      toast.error('Please select an activity level');
      setLoading(false);
      return;
    }
    try {
      await api.put('/profile/', {
        ...form,
        age: parseInt(form.age),
        weight: parseFloat(form.weight),
        height: parseFloat(form.height),
        workout_frequency: parseInt(form.workout_frequency),
      });
      await refreshUser();
      toast.success('Profile set up! Let\'s get fit 🎯');
      navigate('/dashboard');
    } catch {
      toast.error('Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((_, i) => (
              <div key={i} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  i <= step ? 'bg-orange-500 text-white' : 'bg-[#222] text-gray-500'
                }`}>
                  {i + 1}
                </div>
                {i < steps.length - 1 && (
                  <div className={`h-1 w-24 mx-2 rounded ${i < step ? 'bg-orange-500' : 'bg-[#222]'}`} />
                )}
              </div>
            ))}
          </div>
          <h2 className="text-2xl font-bold text-white">{steps[step]}</h2>
          <p className="text-gray-400 text-sm mt-1">Step {step + 1} of {steps.length}</p>
        </div>

        <div className="bg-[#111118] rounded-2xl border border-[#222] p-8">
          {step === 0 && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Age</label>
                  <input
                    type="number" min="10" max="100"
                    value={form.age}
                    onChange={(e) => update('age', e.target.value)}
                    className="w-full bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                    placeholder="25"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Gender</label>
                  <select
                    value={form.gender}
                    onChange={(e) => update('gender', e.target.value)}
                    className="w-full bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Weight (kg)</label>
                  <input
                    type="number" min="30" max="300" step="0.1"
                    value={form.weight}
                    onChange={(e) => update('weight', e.target.value)}
                    className="w-full bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                    placeholder="70"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Height (cm)</label>
                  <input
                    type="number" min="100" max="250"
                    value={form.height}
                    onChange={(e) => update('height', e.target.value)}
                    className="w-full bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                    placeholder="175"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm text-gray-400 mb-3">What's your main goal?</label>
                <div className="grid grid-cols-2 gap-3">
                  {goals.map(g => (
                    <button
                      key={g.value}
                      onClick={() => update('goal', g.value)}
                      className={`p-4 rounded-xl border text-left transition-all ${
                        form.goal === g.value
                          ? 'border-orange-500 bg-orange-500/10 text-white'
                          : 'border-[#333] bg-[#1a1a24] text-gray-300 hover:border-gray-500'
                      }`}
                    >
                      <div className="font-semibold">{g.label}</div>
                      <div className="text-xs text-gray-400 mt-1">{g.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-3">Fitness Level</label>
                <div className="space-y-2">
                  {levels.map(l => (
                    <button
                      key={l.value}
                      onClick={() => update('fitness_level', l.value)}
                      className={`w-full p-4 rounded-xl border text-left transition-all ${
                        form.fitness_level === l.value
                          ? 'border-orange-500 bg-orange-500/10 text-white'
                          : 'border-[#333] bg-[#1a1a24] text-gray-300 hover:border-gray-500'
                      }`}
                    >
                      <span className="font-semibold">{l.label}</span>
                      <span className="text-xs text-gray-400 ml-2">— {l.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm text-gray-400 mb-3">Activity Level</label>
                <div className="space-y-2">
                  {activityLevels.map(a => (
                    <button
                      key={a.value}
                      onClick={() => update('activity_level', a.value)}
                      className={`w-full p-3 rounded-xl border text-left transition-all ${
                        form.activity_level === a.value
                          ? 'border-orange-500 bg-orange-500/10 text-white'
                          : 'border-[#333] bg-[#1a1a24] text-gray-300 hover:border-gray-500'
                      }`}
                    >
                      <span className="font-semibold text-sm">{a.label}</span>
                      <span className="text-xs text-gray-400 ml-2">{a.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Workout Days per Week: <span className="text-orange-400 font-bold">{form.workout_frequency}</span>
                </label>
                <input
                  type="range" min="1" max="7"
                  value={form.workout_frequency}
                  onChange={(e) => update('workout_frequency', e.target.value)}
                  className="w-full accent-orange-500"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1 day</span><span>7 days</span>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3 mt-8">
            {step > 0 && (
              <button
                onClick={() => setStep(s => s - 1)}
                className="flex-1 py-3 rounded-xl border border-[#333] text-gray-300 hover:border-gray-500 transition-colors"
              >
                Back
              </button>
            )}
            {step < steps.length - 1 ? (
              <button
                onClick={() => {
                  if (step === 0) {
                    if (!form.age || !form.weight || !form.height) {
                      toast.error('Please fill in age, weight, and height');
                      return;
                    }
                  }
                  if (step === 1) {
                    if (!form.goal || !form.fitness_level) {
                      toast.error('Please select a goal and fitness level');
                      return;
                    }
                  }
                  setStep(s => s + 1);
                }}
                className="flex-1 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold hover:opacity-90 transition-opacity"
              >
                Continue
              </button>
            ) : (
              <button
                onClick={handleFinish}
                disabled={loading}
                className="flex-1 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 text-white font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Finish Setup 🎯'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
