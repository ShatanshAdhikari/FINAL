import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';
import { Flame, Footprints, Dumbbell, Target, TrendingUp, Apple, Scale } from 'lucide-react';
import { CardSkeleton, StatSkeleton } from '../components/Skeleton';

export default function Dashboard() {
  const { user } = useAuth();
  const [nutritionPlan, setNutritionPlan] = useState(null);
  const [todayCalories, setTodayCalories] = useState(null);
  const [stepData, setStepData] = useState(null);
  const [calorieHistory, setCalorieHistory] = useState([]);
  const [weightHistory, setWeightHistory] = useState([]);
  const [weightInput, setWeightInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [plan, today, steps, history, weights] = await Promise.allSettled([
          api.get('/profile/nutrition-plan'),
          api.get('/nutrition/logs/today'),
          api.get('/steps/today'),
          api.get('/nutrition/logs/history?days=7'),
          api.get('/profile/weight-history?days=90'),
        ]);
        if (plan.status === 'fulfilled') setNutritionPlan(plan.value.data);
        if (today.status === 'fulfilled') setTodayCalories(today.value.data);
        if (steps.status === 'fulfilled') setStepData(steps.value.data);
        if (history.status === 'fulfilled') setCalorieHistory(history.value.data);
        if (weights.status === 'fulfilled') setWeightHistory(weights.value.data);

        const anySuccess = [plan, today, steps, history, weights].some(r => r.status === 'fulfilled');
        if (!anySuccess) setError(true);
      } catch {
        setError(true);
      }
      setLoading(false);
    };
    void fetchData();
  }, []);

  const logWeight = async () => {
    const w = parseFloat(weightInput);
    if (!w || w <= 0) return toast.error('Enter a valid weight');
    try {
      await api.post('/profile/weight', { weight: w });
      toast.success('Weight logged!');
      setWeightInput('');
      const res = await api.get('/profile/weight-history?days=90');
      setWeightHistory(res.data);
    } catch {
      toast.error('Failed to log weight');
    }
  };

  if (loading) return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => <StatSkeleton key={i} />)}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CardSkeleton />
        <CardSkeleton />
      </div>
      <CardSkeleton />
    </div>
  );

  if (error) return (
    <div className="text-center py-20">
      <p className="text-red-400 font-medium">Could not reach the server.</p>
      <p className="text-gray-500 text-sm mt-1">Make sure the backend is running, then refresh.</p>
    </div>
  );

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Evening';

  const isProfileComplete = user?.goal && user?.fitness_level && user?.weight;

  const macroColors = ['#f97316', '#3b82f6', '#22c55e'];
  const macros = nutritionPlan ? [
    { name: 'Protein', value: nutritionPlan.macros.protein_pct },
    { name: 'Carbs', value: nutritionPlan.macros.carbs_pct },
    { name: 'Fat', value: nutritionPlan.macros.fat_pct },
  ] : [];

  const calorieGoal = nutritionPlan?.calorie_goal || 2000;
  const consumed = todayCalories?.totals?.calories || 0;
  const progress = Math.min((consumed / calorieGoal) * 100, 100);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Good {greeting}, {user?.username}! 💪
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        {!isProfileComplete && (
          <Link
            to="/onboarding"
            className="bg-orange-500/20 border border-orange-500/30 text-orange-400 px-4 py-2 rounded-xl text-sm font-medium hover:bg-orange-500/30 transition-colors"
          >
            Complete Profile →
          </Link>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Flame size={20} className="text-orange-400" />}
          label="Calories Today"
          value={`${Math.round(consumed)} kcal`}
          sub={`/ ${calorieGoal} goal`}
          color="orange"
        />
        <StatCard
          icon={<Footprints size={20} className="text-blue-400" />}
          label="Steps Today"
          value={stepData?.steps?.toLocaleString() || '0'}
          sub={`${Math.round(stepData?.calories_from_steps || 0)} kcal burned`}
          color="blue"
        />
        <StatCard
          icon={<Target size={20} className="text-green-400" />}
          label="Daily Goal"
          value={`${Math.round(progress)}%`}
          sub="calories consumed"
          color="green"
        />
        <StatCard
          icon={<Dumbbell size={20} className="text-purple-400" />}
          label="Workout Days"
          value={user?.workout_frequency || '—'}
          sub="days per week"
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={18} className="text-orange-400" />
            <h2 className="text-[var(--text-primary)] font-semibold">7-Day Calorie Intake</h2>
          </div>
          {calorieHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={calorieHistory}>
                <defs>
                  <linearGradient id="calGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fill: '#666', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-nested)', border: '1px solid var(--border-input)', borderRadius: '8px' }}
                  labelStyle={{ color: '#999' }}
                  itemStyle={{ color: '#f97316' }}
                />
                <Area type="monotone" dataKey="calories" stroke="#f97316" fill="url(#calGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex flex-col items-center justify-center text-gray-500">
              <Apple size={32} className="mb-2 opacity-30" />
              <p className="text-sm">No calorie data yet. Start logging meals!</p>
              <Link to="/calories" className="text-orange-400 text-sm mt-2 hover:underline">Log food →</Link>
            </div>
          )}
        </div>

        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <h2 className="text-[var(--text-primary)] font-semibold mb-4">Macro Distribution</h2>
          {nutritionPlan ? (
            <>
              <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                  <Pie data={macros} cx="50%" cy="50%" innerRadius={40} outerRadius={65} dataKey="value">
                    {macros.map((_, i) => <Cell key={i} fill={macroColors[i]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => `${v.toFixed(1)}%`}
                    contentStyle={{ background: 'var(--bg-nested)', border: '1px solid var(--border-input)', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-3">
                {[
                  { name: 'Protein', g: nutritionPlan.macros.protein_g, pct: nutritionPlan.macros.protein_pct, color: 'text-orange-400' },
                  { name: 'Carbs', g: nutritionPlan.macros.carbs_g, pct: nutritionPlan.macros.carbs_pct, color: 'text-blue-400' },
                  { name: 'Fat', g: nutritionPlan.macros.fat_g, pct: nutritionPlan.macros.fat_pct, color: 'text-green-400' },
                ].map(m => (
                  <div key={m.name} className="flex justify-between text-sm">
                    <span className={m.color}>{m.name}</span>
                    <span className="text-[var(--text-primary)]">{m.g}g <span className="text-gray-500">({m.pct}%)</span></span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-40 flex items-center justify-center text-gray-500 text-sm">
              Complete your profile to see macros
            </div>
          )}
        </div>
      </div>

      <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-[var(--text-primary)] font-semibold flex items-center gap-2">
            <Scale size={18} className="text-purple-400" /> Weight Progress
          </h2>
          {weightHistory.length > 0 && (
            <span className="text-gray-400 text-sm">
              Current: <span className="text-[var(--text-primary)] font-medium">{weightHistory[weightHistory.length - 1].weight} kg</span>
            </span>
          )}
        </div>

        <div className="flex gap-2 mb-4">
          <input
            type="number"
            value={weightInput}
            onChange={e => setWeightInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && logWeight()}
            placeholder="Enter weight (kg)"
            className="flex-1 bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2 text-[var(--text-primary)] text-sm focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={logWeight}
            className="px-4 py-2 bg-purple-500/20 border border-purple-500/30 text-purple-400 rounded-xl text-sm font-medium hover:bg-purple-500/30 transition-colors"
          >
            Log
          </button>
        </div>

        {weightHistory.length > 1 ? (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={weightHistory}>
              <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis
                tick={{ fill: '#666', fontSize: 11 }}
                domain={['auto', 'auto']}
                tickFormatter={v => `${v}kg`}
              />
              <Tooltip
                contentStyle={{ background: 'var(--bg-nested)', border: '1px solid var(--border-input)', borderRadius: '8px' }}
                formatter={v => [`${v} kg`, 'Weight']}
              />
              <Line type="monotone" dataKey="weight" stroke="#a855f7" strokeWidth={2} dot={{ fill: '#a855f7', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-24 flex items-center justify-center text-gray-500 text-sm">
            {weightHistory.length === 1
              ? 'Log a second entry to see your trend'
              : 'Log your weight daily to track progress'}
          </div>
        )}
      </div>

      {nutritionPlan && (
        <div className="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <h2 className="text-[var(--text-primary)] font-semibold mb-4">Your Daily Nutrition Plan</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'BMR', value: `${nutritionPlan.bmr} kcal`, desc: 'Resting metabolic rate' },
              { label: 'TDEE', value: `${nutritionPlan.tdee} kcal`, desc: 'Total daily expenditure' },
              { label: 'Calorie Goal', value: `${nutritionPlan.calorie_goal} kcal`, desc: `For ${nutritionPlan.goal.replace(/_/g, ' ')}` },
              { label: 'Protein Target', value: `${nutritionPlan.macros.protein_g}g`, desc: 'Daily protein intake' },
            ].map(item => (
              <div key={item.label} className="bg-[var(--bg-nested)] rounded-xl p-4">
                <div className="text-gray-400 text-xs mb-1">{item.label}</div>
                <div className="text-[var(--text-primary)] font-bold text-lg">{item.value}</div>
                <div className="text-gray-500 text-xs mt-1">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value, sub, color }) {
  const colors = {
    orange: 'border-orange-500/20 bg-orange-500/5',
    blue: 'border-blue-500/20 bg-blue-500/5',
    green: 'border-green-500/20 bg-green-500/5',
    purple: 'border-purple-500/20 bg-purple-500/5',
  };
  return (
    <div className={`bg-[var(--bg-surface)] rounded-2xl border ${colors[color]} p-5`}>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <span className="text-gray-400 text-xs">{label}</span>
      </div>
      <div className="text-2xl font-bold text-[var(--text-primary)]">{value}</div>
      <div className="text-gray-500 text-xs mt-1">{sub}</div>
    </div>
  );
}
