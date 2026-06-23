import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { Dumbbell, Zap, Clock, ChevronDown, ChevronUp, Activity, Trash2 } from 'lucide-react';
import { CardSkeleton } from '../components/Skeleton';

function CaloriePredictor({ user }) {
  const [predForm, setPredForm] = useState({ duration_minutes: '', heart_rate: '' });
  const [prediction, setPrediction] = useState(null); // { calories, low, high }
  const [predLoading, setPredLoading] = useState(false);

  const missingFields = ['gender', 'age', 'weight', 'height'].filter(f => !user?.[f]);
  const canPredict = missingFields.length === 0;

  const predictCalories = async () => {
    if (!predForm.duration_minutes || !predForm.heart_rate) {
      toast.error('Enter duration and heart rate');
      return;
    }
    setPredLoading(true);
    try {
      const res = await api.post('/workout/predict-calories', {
        duration_minutes: parseFloat(predForm.duration_minutes),
        heart_rate: parseFloat(predForm.heart_rate),
      });
      setPrediction({
        calories: res.data.predicted_calories_burned,
        low: res.data.confidence_low,
        high: res.data.confidence_high,
      });
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Prediction failed');
    } finally {
      setPredLoading(false);
    }
  };

  return (
    <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
      <h2 className="text-[var(--text-primary)] font-semibold mb-1 flex items-center gap-2">
        <Zap size={18} className="text-yellow-400" /> Calorie Burn Predictor (ML Model)
      </h2>
      <p className="text-gray-400 text-xs mb-4">Uses Lasso Regression (degree 3) to predict calories burned based on heart rate</p>

      {!canPredict && (
        <div className="mb-4 flex items-start gap-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
          <Zap size={16} className="text-yellow-400 mt-0.5 shrink-0" />
          <div className="text-xs">
            <span className="text-yellow-400 font-medium">Profile incomplete. </span>
            <span className="text-gray-400">
              Missing: <span className="text-[var(--text-primary)]">{missingFields.join(', ')}</span>.{' '}
            </span>
            <Link to="/profile" className="text-yellow-400 underline hover:text-yellow-300">
              Update profile →
            </Link>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Duration (min)</label>
          <input
            type="number"
            value={predForm.duration_minutes}
            onChange={(e) => setPredForm({ ...predForm, duration_minutes: e.target.value })}
            className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-3 py-2 text-[var(--text-primary)] text-sm focus:outline-none focus:border-yellow-500 disabled:opacity-40"
            placeholder="30"
            disabled={!canPredict}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Avg Heart Rate (BPM)</label>
          <input
            type="number"
            value={predForm.heart_rate}
            onChange={(e) => setPredForm({ ...predForm, heart_rate: e.target.value })}
            className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-3 py-2 text-[var(--text-primary)] text-sm focus:outline-none focus:border-yellow-500 disabled:opacity-40"
            placeholder="140"
            disabled={!canPredict}
          />
        </div>
        <div className="flex items-end">
          <button
            onClick={predictCalories}
            disabled={predLoading || !canPredict}
            className="w-full py-2 bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 rounded-xl text-sm font-medium hover:bg-yellow-500/30 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {predLoading ? 'Predicting...' : 'Predict'}
          </button>
        </div>
      </div>

      {prediction !== null && (
        <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
          <div className="text-yellow-400 font-bold text-2xl">{Math.round(prediction.calories)} kcal</div>
          <div className="text-gray-400 text-xs mt-1">
            Estimated calories burned
            <span className="ml-2 text-gray-500">
              ({Math.round(prediction.low)}–{Math.round(prediction.high)} kcal range)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function WorkoutPlan() {
  const { user } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedDay, setExpandedDay] = useState(null);

  const [logForm, setLogForm] = useState({ exercise_name: '', duration_minutes: '', sets: '', reps: '', heart_rate: '', calories_burned: '' });
  const [logs, setLogs] = useState([]);

  const fetchPlan = useCallback(async () => {
    try {
      const res = await api.get('/workout/plan');
      setPlan(res.data);
      setExpandedDay(Object.keys(res.data.weekly_plan)[0]);
    } catch {
      toast.error('Complete your profile to get a workout plan');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    try {
      const res = await api.get('/workout/logs');
      setLogs(res.data);
    } catch {}
  }, []);

  useEffect(() => {
    void fetchPlan();
    void fetchLogs();
  }, [fetchPlan, fetchLogs]);

  const deleteLog = async (id) => {
    try {
      await api.delete(`/workout/log/${id}`);
      setLogs(prev => prev.filter(l => l.id !== id));
      toast.success('Workout removed');
    } catch {
      toast.error('Failed to delete workout');
    }
  };

  const logWorkout = async () => {
    if (!logForm.exercise_name || !logForm.duration_minutes) {
      toast.error('Exercise name and duration are required');
      return;
    }
    try {
      await api.post('/workout/log', {
        exercise_name: logForm.exercise_name,
        duration_minutes: parseFloat(logForm.duration_minutes),
        sets: logForm.sets ? parseInt(logForm.sets) : null,
        reps: logForm.reps ? parseInt(logForm.reps) : null,
        heart_rate: logForm.heart_rate ? parseFloat(logForm.heart_rate) : null,
        calories_burned: logForm.calories_burned ? parseFloat(logForm.calories_burned) : null,
      });
      toast.success('Workout logged! 💪');
      setLogForm({ exercise_name: '', duration_minutes: '', sets: '', reps: '', heart_rate: '', calories_burned: '' });
      void fetchLogs();
    } catch {
      toast.error('Failed to log workout');
    }
  };

  const goalColors = {
    fat_loss: 'text-orange-400 bg-orange-400/10',
    muscle_gain: 'text-blue-400 bg-blue-400/10',
    strength: 'text-red-400 bg-red-400/10',
    endurance: 'text-green-400 bg-green-400/10',
  };

  if (loading) return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3"><CardSkeleton /><CardSkeleton /><CardSkeleton /></div>
      <CardSkeleton />
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Your Workout Plan</h1>
        <p className="text-gray-400 text-sm mt-1">Personalized rule-based weekly routine</p>
      </div>

      {plan && (
        <div className="grid grid-cols-3 gap-3 mb-2">
          {[
            { label: 'Goal', value: plan.goal.replace(/_/g, ' ').toUpperCase() },
            { label: 'Level', value: plan.fitness_level.charAt(0).toUpperCase() + plan.fitness_level.slice(1) },
            { label: 'Days/Week', value: plan.days_per_week },
          ].map(s => (
            <div key={s.label} className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl p-4 text-center">
              <div className="text-gray-400 text-xs mb-1">{s.label}</div>
              <div className="text-[var(--text-primary)] font-bold">{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {plan ? (
        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <h2 className="text-[var(--text-primary)] font-semibold mb-4 flex items-center gap-2">
            <Dumbbell size={18} className="text-orange-400" /> Weekly Schedule
          </h2>
          <div className="space-y-3">
            {Object.entries(plan.weekly_plan).map(([day, data]) => (
              <div key={day} className="border border-[var(--border-subtle)] rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpandedDay(expandedDay === day ? null : day)}
                  className="w-full flex items-center justify-between p-4 hover:bg-[var(--bg-muted)] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-20 text-orange-400 font-semibold text-sm">{day}</div>
                    <span className={`px-2 py-1 rounded-lg text-xs font-medium ${goalColors[plan.goal] || 'text-gray-400 bg-gray-400/10'}`}>
                      {data.type}
                    </span>
                    <span className="text-gray-500 text-xs">{data.exercises.length} exercises</span>
                  </div>
                  {expandedDay === day ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </button>
                {expandedDay === day && (
                  <div className="border-t border-[var(--border-subtle)] p-4 space-y-3">
                    {data.exercises.map((ex, i) => (
                      <div key={i} className="flex items-start justify-between bg-[var(--bg-nested)] rounded-xl p-3">
                        <div>
                          <div className="text-[var(--text-primary)] font-medium text-sm">{ex.name}</div>
                          <div className="text-gray-500 text-xs mt-1">{ex.muscles}</div>
                        </div>
                        <div className="text-right text-xs space-y-1">
                          <div className="text-orange-400">{ex.sets} sets × {ex.reps} reps</div>
                          <div className="text-gray-500 flex items-center gap-1 justify-end">
                            <Clock size={10} /> {ex.rest} rest
                          </div>
                          <div className="text-gray-600">{ex.intensity}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-12 text-center">
          <Dumbbell size={48} className="text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Complete your profile to generate a workout plan</p>
        </div>
      )}

      <CaloriePredictor user={user} />

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
        <h2 className="text-[var(--text-primary)] font-semibold mb-4 flex items-center gap-2">
          <Activity size={18} className="text-green-400" /> Log Workout
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
          {[
            { key: 'exercise_name', label: 'Exercise', placeholder: 'e.g. Push-Ups' },
            { key: 'duration_minutes', label: 'Duration (min)', placeholder: '30', type: 'number' },
            { key: 'sets', label: 'Sets', placeholder: '3', type: 'number' },
            { key: 'reps', label: 'Reps', placeholder: '12', type: 'number' },
            { key: 'heart_rate', label: 'Heart Rate (BPM)', placeholder: '140', type: 'number' },
            { key: 'calories_burned', label: 'Calories Burned', placeholder: '200', type: 'number' },
          ].map(f => (
            <div key={f.key}>
              <label className="block text-xs text-gray-400 mb-1">{f.label}</label>
              <input
                type={f.type || 'text'}
                value={logForm[f.key]}
                onChange={(e) => setLogForm({ ...logForm, [f.key]: e.target.value })}
                className="w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-3 py-2 text-[var(--text-primary)] text-sm focus:outline-none focus:border-green-500"
                placeholder={f.placeholder}
              />
            </div>
          ))}
        </div>
        <button
          onClick={logWorkout}
          className="px-6 py-2 bg-green-500/20 border border-green-500/30 text-green-400 rounded-xl text-sm font-medium hover:bg-green-500/30 transition-colors"
        >
          Log Workout
        </button>

        {logs.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="text-gray-400 text-xs font-medium mb-2">Recent Workouts</div>
            {logs.slice(0, 5).map(log => (
              <div key={log.id} className="flex items-center justify-between bg-[var(--bg-nested)] rounded-xl px-4 py-3 text-sm">
                <div>
                  <span className="text-[var(--text-primary)] font-medium">{log.exercise_name}</span>
                  <span className="text-gray-500 ml-2">{log.duration_minutes} min</span>
                  {log.sets && log.reps && (
                    <span className="text-gray-500 ml-2 text-xs">{log.sets}×{log.reps}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    {log.calories_burned && <span className="text-orange-400 text-xs">{log.calories_burned} kcal</span>}
                    <div className="text-gray-600 text-xs">{new Date(log.logged_at).toLocaleDateString()}</div>
                  </div>
                  <button
                    onClick={() => deleteLog(log.id)}
                    aria-label="Delete workout log"
                    className="text-gray-600 hover:text-red-400 transition-colors p-1"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
