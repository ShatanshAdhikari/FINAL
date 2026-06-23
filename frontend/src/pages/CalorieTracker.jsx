import { useCallback, useEffect, useState } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Search, Plus, Trash2, Apple } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];

function getScaled(food, grams) {
  const base = food.serving_weight_grams || 100;
  const ratio = (parseFloat(grams) || 0) / base;
  return {
    calories: Math.round((food.nf_calories || 0) * ratio),
    protein:  Math.round((food.nf_protein               || 0) * ratio * 10) / 10,
    carbs:    Math.round((food.nf_total_carbohydrate     || 0) * ratio * 10) / 10,
    fat:      Math.round((food.nf_total_fat              || 0) * ratio * 10) / 10,
  };
}

export default function CalorieTracker() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [quantities, setQuantities] = useState({});
  const [searching, setSearching] = useState(false);
  const [todayLogs, setTodayLogs] = useState({ logs: [], totals: {} });
  const [history, setHistory] = useState([]);
  const [selectedMeal, setSelectedMeal] = useState('snack');
  const [nutritionPlan, setNutritionPlan] = useState(null);

  const fetchToday = useCallback(async () => {
    try {
      const res = await api.get('/nutrition/logs/today');
      setTodayLogs(res.data);
    } catch {}
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await api.get('/nutrition/logs/history?days=7');
      setHistory(res.data);
    } catch {}
  }, []);

  useEffect(() => {
    void fetchToday();
    void fetchHistory();
    void api.get('/profile/nutrition-plan').then(r => setNutritionPlan(r.data)).catch(() => {});
  }, [fetchToday, fetchHistory]);

  const searchFood = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.post('/nutrition/search', { query: searchQuery });
      const foods = res.data.foods || [];
      setSearchResults(foods);
      const initial = {};
      foods.forEach((f, i) => { initial[i] = f.serving_weight_grams || 100; });
      setQuantities(initial);
    } catch {
      toast.error('Food search failed');
    } finally {
      setSearching(false);
    }
  };

  const logFood = async (food, index) => {
    const grams = parseFloat(quantities[index]) || food.serving_weight_grams || 100;
    if (grams <= 0) {
      toast.error('Enter a valid weight');
      return;
    }
    const scaled = getScaled(food, grams);
    try {
      await api.post('/nutrition/log', {
        food_name: `${food.food_name} (${grams}g)`,
        calories: scaled.calories,
        protein:  scaled.protein,
        carbs:    scaled.carbs,
        fat:      scaled.fat,
        meal_type: selectedMeal,
      });
      toast.success(`${food.food_name} (${grams}g) logged! 🥗`);
      void fetchToday();
      void fetchHistory();
      setSearchResults([]);
      setSearchQuery('');
      setQuantities({});
    } catch {
      toast.error('Failed to log food');
    }
  };

  const deleteLog = async (id) => {
    try {
      await api.delete(`/nutrition/log/${id}`);
      toast.success('Removed');
      void fetchToday();
      void fetchHistory();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const setQty = (index, value) =>
    setQuantities(q => ({ ...q, [index]: value }));

  const calorieGoal = nutritionPlan?.calorie_goal || 2000;
  const consumed    = todayLogs.totals?.calories || 0;
  const remaining   = calorieGoal - consumed;
  const progress    = Math.min((consumed / calorieGoal) * 100, 100);

  const mealGroups = mealTypes.map(m => {
    const items = todayLogs.logs.filter(l => l.meal_type === m);
    return { type: m, items, total: items.reduce((s, l) => s + l.calories, 0) };
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Calorie Tracker</h1>
        <p className="text-gray-400 text-sm mt-1">Log meals and track daily intake</p>
      </div>

      <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold">Today's Progress</h2>
          <span className="text-gray-400 text-sm">{new Date().toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-6 mb-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{Math.round(consumed)}</div>
            <div className="text-gray-400 text-xs">consumed</div>
          </div>
          <div className="flex-1">
            <div className="w-full bg-[#222] rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${progress > 100 ? 'bg-red-500' : 'bg-gradient-to-r from-orange-500 to-red-500'}`}
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{Math.round(progress)}% of goal</span>
              <span>{calorieGoal} kcal goal</span>
            </div>
          </div>
          <div className="text-center">
            <div className={`text-3xl font-bold ${remaining < 0 ? 'text-red-400' : 'text-green-400'}`}>
              {Math.abs(Math.round(remaining))}
            </div>
            <div className="text-gray-400 text-xs">{remaining < 0 ? 'over goal' : 'remaining'}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { name: 'Protein', consumed: todayLogs.totals?.protein || 0, goal: nutritionPlan?.macros?.protein_g || 0, color: 'bg-orange-500' },
            { name: 'Carbs',   consumed: todayLogs.totals?.carbs   || 0, goal: nutritionPlan?.macros?.carbs_g   || 0, color: 'bg-blue-500'   },
            { name: 'Fat',     consumed: todayLogs.totals?.fat     || 0, goal: nutritionPlan?.macros?.fat_g     || 0, color: 'bg-green-500'  },
          ].map(m => (
            <div key={m.name} className="bg-[#1a1a24] rounded-xl p-3">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-gray-400">{m.name}</span>
                <span className="text-gray-300">{Math.round(m.consumed)}g / {Math.round(m.goal)}g</span>
              </div>
              <div className="w-full bg-[#222] rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${m.color}`}
                  style={{ width: `${Math.min((m.consumed / (m.goal || 1)) * 100, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
        <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Search size={18} className="text-orange-400" /> Search & Log Food
        </h2>

        <div className="flex gap-2 mb-4">
          <select
            value={selectedMeal}
            onChange={(e) => setSelectedMeal(e.target.value)}
            className="bg-[#1a1a24] border border-[#333] rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-orange-500"
          >
            {mealTypes.map(m => (
              <option key={m} value={m}>{m.charAt(0).toUpperCase() + m.slice(1)}</option>
            ))}
          </select>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchFood()}
            className="flex-1 bg-[#1a1a24] border border-[#333] rounded-xl px-4 py-2 text-white text-sm focus:outline-none focus:border-orange-500"
            placeholder="Search food (e.g. chicken breast, rice, apple)…"
          />
          <button
            onClick={searchFood}
            disabled={searching}
            className="px-4 py-2 bg-orange-500/20 border border-orange-500/30 text-orange-400 rounded-xl text-sm hover:bg-orange-500/30 transition-colors disabled:opacity-50"
          >
            {searching ? '…' : 'Search'}
          </button>
        </div>

        {searchResults.length > 0 && (
          <div className="space-y-3">
            {searchResults.map((food, i) => {
              const grams  = quantities[i] ?? (food.serving_weight_grams || 100);
              const scaled = getScaled(food, grams);
              const per100 = Math.round((food.nf_calories || 0) / (food.serving_weight_grams || 100) * 100);

              return (
                <div key={i} className="bg-[#1a1a24] rounded-xl p-4 border border-[#2a2a2a]">
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-white text-sm font-medium capitalize">{food.food_name}</div>
                    <div className="text-orange-400 font-bold text-lg leading-none">{scaled.calories} kcal</div>
                  </div>
                  <div className="text-gray-500 text-xs mb-3">
                    {scaled.protein}g protein &middot; {scaled.carbs}g carbs &middot; {scaled.fat}g fat
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center flex-1 bg-[#111118] border border-[#333] rounded-xl overflow-hidden focus-within:border-orange-500 transition-colors">
                      <input
                        type="number"
                        min="1"
                        max="5000"
                        value={grams}
                        onChange={(e) => setQty(i, e.target.value)}
                        className="flex-1 bg-transparent px-3 py-2 text-white text-sm focus:outline-none min-w-0"
                        placeholder="100"
                      />
                      <span className="text-gray-500 text-sm px-3 border-l border-[#333]">g</span>
                    </div>
                    <button
                      onClick={() => logFood(food, i)}
                      className="flex items-center gap-1.5 px-4 py-2 bg-orange-500/20 border border-orange-500/30 text-orange-400 rounded-xl text-sm font-medium hover:bg-orange-500/30 transition-colors whitespace-nowrap"
                    >
                      <Plus size={15} />
                      Add
                    </button>
                  </div>
                  <div className="text-gray-600 text-xs mt-2">
                    Per 100 g: {per100} kcal
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
        <h2 className="text-white font-semibold mb-4">Today's Meals</h2>
        <div className="space-y-4">
          {mealGroups.map(group => (
            group.items.length > 0 && (
              <div key={group.type}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm capitalize font-medium">{group.type}</span>
                  <span className="text-orange-400 text-sm">{Math.round(group.total)} kcal</span>
                </div>
                <div className="space-y-2">
                  {group.items.map(log => (
                    <div key={log.id} className="flex items-center justify-between bg-[#1a1a24] rounded-xl px-4 py-3 text-sm">
                      <div>
                        <span className="text-white font-medium capitalize">{log.food_name}</span>
                        <span className="text-gray-500 ml-2 text-xs">
                          {Math.round(log.protein || 0)}g P &middot; {Math.round(log.carbs || 0)}g C &middot; {Math.round(log.fat || 0)}g F
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-orange-400">{Math.round(log.calories)} kcal</span>
                        <button
                          onClick={() => deleteLog(log.id)}
                          className="text-gray-600 hover:text-red-400 transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          ))}
          {todayLogs.logs.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Apple size={32} className="mx-auto mb-2 opacity-30" />
              <p className="text-sm">No meals logged today. Search for food above!</p>
            </div>
          )}
        </div>
      </div>

      {history.length > 0 && (
        <div className="bg-[#111118] rounded-2xl border border-[#222] p-6">
          <h2 className="text-white font-semibold mb-4">7-Day Calorie History</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={history}>
              <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fill: '#666', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a24', border: '1px solid #333', borderRadius: '8px' }}
                formatter={(v, n) => [Math.round(v), n.charAt(0).toUpperCase() + n.slice(1)]}
              />
              <Bar dataKey="calories" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
