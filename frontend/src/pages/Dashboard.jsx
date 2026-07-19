import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';
import { Flame, Footprints, Dumbbell, Target, TrendingUp, Apple, Scale, Download, Calendar } from 'lucide-react';
import { CardSkeleton, StatSkeleton } from '../components/Skeleton';
import { generateProgressPdf } from '../utils/progressPdf';

export default function Dashboard() {
  const { user } = useAuth();
  const isoDaysAgo = (n) => new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);

  const [nutritionPlan, setNutritionPlan] = useState(null);
  const [todayCalories, setTodayCalories] = useState(null);
  const [stepData, setStepData] = useState(null);
  const [calorieHistory, setCalorieHistory] = useState([]);
  const [weightHistory, setWeightHistory] = useState([]);
  const [weightInput, setWeightInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // On-page chart date range (defaults: last 30 days)
  const [chartFrom, setChartFrom] = useState(isoDaysAgo(29));
  const [chartTo, setChartTo] = useState(isoDaysAgo(0));
  const [chartsLoading, setChartsLoading] = useState(false);

  const applyChartPreset = (days) => {
    setChartFrom(days === 'all' ? isoDaysAgo(730) : isoDaysAgo(days - 1));
    setChartTo(isoDaysAgo(0));
  };

  // Core dashboard data (range-independent)
  useEffect(() => {
    const fetchCore = async () => {
      try {
        const [plan, today, steps] = await Promise.allSettled([
          api.get('/profile/nutrition-plan'),
          api.get('/nutrition/logs/today'),
          api.get('/steps/today'),
        ]);
        if (plan.status === 'fulfilled') setNutritionPlan(plan.value.data);
        if (today.status === 'fulfilled') setTodayCalories(today.value.data);
        if (steps.status === 'fulfilled') setStepData(steps.value.data);
        if (![plan, today, steps].some(r => r.status === 'fulfilled')) setError(true);
      } catch {
        setError(true);
      }
      setLoading(false);
    };
    void fetchCore();
  }, []);

  // Chart history — refetches whenever the on-page range changes
  useEffect(() => {
    if (chartFrom > chartTo) return;
    let cancelled = false;
    const load = async () => {
      setChartsLoading(true);
      const fromMs = new Date(`${chartFrom}T00:00:00Z`).getTime();
      const days = Math.min(1000, Math.max(1, Math.round((Date.now() - fromMs) / 86400000) + 2));
      const [hist, weights] = await Promise.allSettled([
        api.get(`/nutrition/logs/history?days=${days}`),
        api.get(`/profile/weight-history?days=${days}`),
      ]);
      if (cancelled) return;
      const inRange = (d) => d.date >= chartFrom && d.date <= chartTo;
      if (hist.status === 'fulfilled') setCalorieHistory(hist.value.data.filter(inRange));
      if (weights.status === 'fulfilled') setWeightHistory(weights.value.data.filter(inRange));
      setChartsLoading(false);
    };
    void load();
    return () => { cancelled = true; };
  }, [chartFrom, chartTo]);

  const [downloading, setDownloading] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [rangeFrom, setRangeFrom] = useState(isoDaysAgo(29));
  const [rangeTo, setRangeTo] = useState(isoDaysAgo(0));

  const applyPreset = (days) => {
    // days === 'all' spans up to ~2 years back; presets always end today.
    setRangeFrom(days === 'all' ? isoDaysAgo(730) : isoDaysAgo(days - 1));
    setRangeTo(isoDaysAgo(0));
  };

  const downloadReport = async (from, to) => {
    if (from > to) {
      toast.error('Start date must be on or before the end date');
      return;
    }
    setDownloading(true);
    try {
      // Fetch a window wide enough to cover the chosen start, then filter to [from, to].
      const fromMs = new Date(`${from}T00:00:00Z`).getTime();
      const days = Math.min(1000, Math.max(1, Math.round((Date.now() - fromMs) / 86400000) + 2));
      const [hist, weights] = await Promise.allSettled([
        api.get(`/nutrition/logs/history?days=${days}`),
        api.get(`/profile/weight-history?days=${days}`),
      ]);
      const inRange = (d) => d.date >= from && d.date <= to;
      const cal = (hist.status === 'fulfilled' ? hist.value.data : calorieHistory).filter(inRange);
      const wt = (weights.status === 'fulfilled' ? weights.value.data : weightHistory).filter(inRange);

      generateProgressPdf({
        user, nutritionPlan, todayCalories, stepData,
        calorieHistory: cal, weightHistory: wt,
        range: { from, to },
      });
      toast.success('Progress report downloaded 📄');
      setShowReport(false);
    } catch (e) {
      console.error(e);
      toast.error('Could not generate the report');
    } finally {
      setDownloading(false);
    }
  };

  const logWeight = async () => {
    const w = parseFloat(weightInput);
    if (!w || w <= 0) return toast.error('Enter a valid weight');
    try {
      await api.post('/profile/weight', { weight: w });
      toast.success('Weight logged!');
      setWeightInput('');
      // Refetch within the active chart range so a new entry shows immediately.
      const fromMs = new Date(`${chartFrom}T00:00:00Z`).getTime();
      const days = Math.min(1000, Math.max(1, Math.round((Date.now() - fromMs) / 86400000) + 2));
      const res = await api.get(`/profile/weight-history?days=${days}`);
      setWeightHistory(res.data.filter(d => d.date >= chartFrom && d.date <= chartTo));
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
        <div className="flex items-center gap-2">
          {!isProfileComplete && (
            <Link
              to="/onboarding"
              className="bg-orange-500/20 border border-orange-500/30 text-orange-400 px-4 py-2 rounded-xl text-sm font-medium hover:bg-orange-500/30 transition-colors"
            >
              Complete Profile →
            </Link>
          )}
          <div className="relative">
            <button
              onClick={() => setShowReport(v => !v)}
              disabled={downloading}
              className="flex items-center gap-2 bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-primary)] px-4 py-2 rounded-xl text-sm font-medium hover:border-orange-500/50 transition-colors disabled:opacity-50"
            >
              <Download size={16} className="text-orange-400" />
              {downloading ? 'Preparing…' : 'Download Progress'}
            </button>

            {showReport && (
              <>
                {/* click-away backdrop */}
                <div className="fixed inset-0 z-10" onClick={() => setShowReport(false)} />
                <div className="absolute right-0 mt-2 w-72 z-20 bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl shadow-xl p-4 space-y-3">
                  <div className="flex items-center gap-2 text-[var(--text-primary)] font-semibold text-sm">
                    <Calendar size={16} className="text-orange-400" /> Report period
                  </div>

                  <div className="flex flex-wrap gap-1.5">
                    {[
                      { label: '7d', days: 7 },
                      { label: '30d', days: 30 },
                      { label: '90d', days: 90 },
                      { label: 'All', days: 'all' },
                    ].map(p => (
                      <button
                        key={p.label}
                        onClick={() => applyPreset(p.days)}
                        className="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--bg-nested)] border border-[var(--border-input)] text-[var(--text-primary)] hover:border-orange-500/50 transition-colors"
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-2">
                    <label className="block text-xs text-gray-400">
                      From
                      <input
                        type="date"
                        value={rangeFrom}
                        max={rangeTo}
                        onChange={e => setRangeFrom(e.target.value)}
                        className="mt-1 w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-lg px-3 py-1.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500"
                      />
                    </label>
                    <label className="block text-xs text-gray-400">
                      To
                      <input
                        type="date"
                        value={rangeTo}
                        min={rangeFrom}
                        max={isoDaysAgo(0)}
                        onChange={e => setRangeTo(e.target.value)}
                        className="mt-1 w-full bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-lg px-3 py-1.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500"
                      />
                    </label>
                  </div>

                  <button
                    onClick={() => downloadReport(rangeFrom, rangeTo)}
                    disabled={downloading}
                    className="w-full flex items-center justify-center gap-2 bg-orange-500 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-orange-600 transition-colors disabled:opacity-50"
                  >
                    <Download size={15} />
                    {downloading ? 'Preparing…' : 'Download PDF'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
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

      <div className="flex flex-wrap items-center gap-2 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] px-4 py-3">
        <span className="flex items-center gap-1.5 text-sm text-[var(--text-primary)] font-medium mr-1">
          <Calendar size={15} className="text-orange-400" /> Chart range
        </span>
        {[
          { label: '7d', days: 7 },
          { label: '30d', days: 30 },
          { label: '90d', days: 90 },
          { label: 'All', days: 'all' },
        ].map(p => (
          <button
            key={p.label}
            onClick={() => applyChartPreset(p.days)}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--bg-nested)] border border-[var(--border-input)] text-[var(--text-primary)] hover:border-orange-500/50 transition-colors"
          >
            {p.label}
          </button>
        ))}
        <input
          type="date"
          value={chartFrom}
          max={chartTo}
          onChange={e => setChartFrom(e.target.value)}
          className="bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-orange-500"
        />
        <span className="text-gray-500 text-xs">→</span>
        <input
          type="date"
          value={chartTo}
          min={chartFrom}
          max={isoDaysAgo(0)}
          onChange={e => setChartTo(e.target.value)}
          className="bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-orange-500"
        />
        {chartsLoading && <span className="text-xs text-gray-400 ml-auto">updating…</span>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={18} className="text-orange-400" />
            <h2 className="text-[var(--text-primary)] font-semibold">Calorie Intake</h2>
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
