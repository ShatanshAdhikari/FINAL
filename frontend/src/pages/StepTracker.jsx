import { useEffect, useRef, useState } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Footprints, Flame, Heart, Play, Square } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const STEP_GOAL = 10000;

// ─── Accelerometer Step Counter Hook ──────────────────────────────────────────
// Peak-detection on acceleration magnitude (|a| = √(x²+y²+z²)).
// A step is registered when the magnitude crosses STEP_THRESHOLD after a
// minimum interval — simple but effective for walking detection.
const STEP_THRESHOLD = 13;      // m/s² — tune up if too sensitive, down if missing steps
const MIN_STEP_INTERVAL = 280;  // ms  — prevents double-counting a single footfall

function useStepCounter() {
  const [liveSteps, setLiveSteps] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const lastStepTime = useRef(0);
  const stepsRef = useRef(0);

  useEffect(() => {
    setIsSupported('DeviceMotionEvent' in window);
  }, []);

  useEffect(() => {
    if (!isRunning) return;

    const handleMotion = (e) => {
      const a = e.accelerationIncludingGravity;
      if (!a) return;
      const magnitude = Math.sqrt((a.x || 0) ** 2 + (a.y || 0) ** 2 + (a.z || 0) ** 2);
      const now = Date.now();
      if (magnitude > STEP_THRESHOLD && now - lastStepTime.current > MIN_STEP_INTERVAL) {
        lastStepTime.current = now;
        stepsRef.current += 1;
        setLiveSteps(stepsRef.current);
      }
    };

    window.addEventListener('devicemotion', handleMotion);
    return () => window.removeEventListener('devicemotion', handleMotion);
  }, [isRunning]);

  const start = async () => {
    // iOS 13+ requires an explicit user-gesture permission request
    if (typeof DeviceMotionEvent?.requestPermission === 'function') {
      try {
        const permission = await DeviceMotionEvent.requestPermission();
        if (permission !== 'granted') {
          toast.error('Motion sensor permission denied');
          return false;
        }
      } catch {
        toast.error('Could not request motion permission');
        return false;
      }
    }
    stepsRef.current = 0;
    setLiveSteps(0);
    lastStepTime.current = 0;
    setIsRunning(true);
    return true;
  };

  const stop = () => {
    setIsRunning(false);
    return stepsRef.current;
  };

  return { liveSteps, isRunning, isSupported, start, stop };
}

// ─── Component ─────────────────────────────────────────────────────────────────
export default function StepTracker() {
  const [today, setToday] = useState(null);
  const [history, setHistory] = useState([]);
  const [stepInput, setStepInput] = useState('');
  const [loading, setLoading] = useState(false);

  const { liveSteps, isRunning, isSupported, start, stop } = useStepCounter();

  useEffect(() => {
    fetchToday();
    fetchHistory();
  }, []);

  const fetchToday = async () => {
    try {
      const res = await api.get('/steps/today');
      setToday(res.data);
    } catch (e) {
      console.error('Failed to fetch today steps', e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await api.get('/steps/history?days=7');
      setHistory(res.data);
    } catch (e) {
      console.error('Failed to fetch step history', e);
    }
  };

  const logSteps = async (overrideSteps) => {
    const value = overrideSteps ?? stepInput;
    const count = parseInt(value);
    if (!value || isNaN(count) || count < 0) {
      toast.error('Enter a valid step count');
      return;
    }
    setLoading(true);
    try {
      await api.post('/steps/log', {
        steps: count,
        date: new Date().toISOString().split('T')[0],
      });
      toast.success('Steps logged! 👣');
      setStepInput('');
      fetchToday();
      fetchHistory();
    } catch (e) {
      toast.error('Failed to log steps');
    } finally {
      setLoading(false);
    }
  };

  const handleStartCounter = async () => {
    const ok = await start();
    if (ok) toast.success('Counting steps — keep your phone in your pocket or hand!');
  };

  const handleStopCounter = () => {
    const counted = stop();
    if (counted > 0) {
      setStepInput(String(counted));
      toast.success(`Counted ${counted} steps — tap "Update Steps" to save!`);
    } else {
      toast.error('No steps detected. Make sure to carry your phone while walking.');
    }
  };

  const progress = today ? Math.min((today.steps / STEP_GOAL) * 100, 100) : 0;
  const circumference = 2 * Math.PI * 70;
  const dashOffset = circumference - (progress / 100) * circumference;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Step Tracker</h1>
        <p className="text-gray-400 text-sm mt-1">Track your daily steps and activity</p>
      </div>

      {/* Step Ring + Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#111118] rounded-2xl border border-[#222] p-8 flex flex-col items-center justify-center">
          <div className="relative">
            <svg width="160" height="160" className="-rotate-90">
              <circle cx="80" cy="80" r="70" fill="none" stroke="#1a1a24" strokeWidth="10" />
              <circle
                cx="80" cy="80" r="70" fill="none"
                stroke="#f97316" strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 0.5s ease' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="text-3xl font-bold text-white">{today?.steps?.toLocaleString() || 0}</div>
              <div className="text-gray-400 text-xs">/ {STEP_GOAL.toLocaleString()}</div>
            </div>
          </div>
          <div className="text-orange-400 font-semibold mt-4">{Math.round(progress)}% of daily goal</div>
        </div>

        <div className="space-y-4">
          <div className="bg-[#111118] rounded-2xl border border-[#222] p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
              <Flame size={24} className="text-orange-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {Math.round(today?.calories_from_steps || 0)} kcal
              </div>
              <div className="text-gray-400 text-sm">Calories from steps</div>
            </div>
          </div>
          <div className="bg-[#111118] rounded-2xl border border-[#222] p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center">
              <Heart size={24} className="text-red-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {today?.bmr ? `${today.bmr} kcal` : '—'}
              </div>
              <div className="text-gray-400 text-sm">Basal Metabolic Rate</div>
            </div>
          </div>
          <div className="bg-[#111118] rounded-2xl border border-[#222] p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
              <Footprints size={24} className="text-blue-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {today?.steps ? `~${((today.steps * 0.762) / 1000).toFixed(1)} km` : '0 km'}
              </div>
              <div className="text-gray-400 text-sm">Distance (est.)</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Accelerometer Counter ── */}
      {isSupported && (
        <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-white font-semibold">Live Step Counter</h2>
            <span className="text-xs text-gray-500 bg-[#1a1a24] px-2 py-1 rounded-lg">
              Uses phone motion sensor
            </span>
          </div>
          <p className="text-gray-500 text-xs mb-5">
            Carry your phone naturally while walking. Tap Stop when done — the count will fill in below automatically.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-4">
            {/* Live count display */}
            <div className="flex-1 w-full bg-[#1a1a24] rounded-2xl p-6 text-center">
              <div className={`text-5xl font-bold tabular-nums transition-all ${isRunning ? 'text-orange-400' : 'text-white'}`}>
                {liveSteps.toLocaleString()}
              </div>
              <div className="text-gray-500 text-sm mt-2">
                {isRunning ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
                    Counting…
                  </span>
                ) : 'steps detected'}
              </div>
            </div>

            {/* Start / Stop button */}
            {!isRunning ? (
              <button
                onClick={handleStartCounter}
                className="flex items-center gap-2 px-6 py-4 bg-orange-500/20 border border-orange-500/30 text-orange-400 rounded-2xl font-semibold hover:bg-orange-500/30 transition-colors"
              >
                <Play size={20} />
                Start
              </button>
            ) : (
              <button
                onClick={handleStopCounter}
                className="flex items-center gap-2 px-6 py-4 bg-red-500/20 border border-red-500/30 text-red-400 rounded-2xl font-semibold hover:bg-red-500/30 transition-colors"
              >
                <Square size={20} />
                Stop
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Manual Log ── */}
      <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
        <h2 className="text-white font-semibold mb-1">Update Today's Steps</h2>
        <p className="text-gray-500 text-xs mb-4">
          {isSupported
            ? 'Or type a count directly — e.g. from a fitness band or watch.'
            : 'Motion sensor not available in this browser. Enter your step count manually.'}
        </p>
        <div className="flex gap-3">
          <input
            type="number"
            value={stepInput}
            onChange={(e) => setStepInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && logSteps()}
            className="flex-1 bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-orange-500"
            placeholder="Enter step count (e.g. 8500)"
            min="0"
          />
          <button
            onClick={() => logSteps()}
            disabled={loading}
            className="px-6 py-3 bg-orange-500/20 border border-orange-500/30 text-orange-400 rounded-xl text-sm font-medium hover:bg-orange-500/30 transition-colors disabled:opacity-50"
          >
            {loading ? 'Saving…' : 'Update Steps'}
          </button>
        </div>
      </div>

      {/* ── 7-day history ── */}
      <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
        <h2 className="text-white font-semibold mb-4">7-Day Step History</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={history}>
            <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
            <YAxis tick={{ fill: '#666', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1a1a24', border: '1px solid #333', borderRadius: '8px' }}
              formatter={(v) => [v.toLocaleString(), 'Steps']}
            />
            <Bar dataKey="steps" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
