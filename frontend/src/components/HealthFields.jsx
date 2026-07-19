import { CONDITION_OPTIONS, ALLERGY_OPTIONS, hasItem, toggleItem } from '../utils/health';

// Reusable allergy + disease inputs. `diseases` / `allergies` are comma-separated
// strings; onChange(key, newValue) is called with the updated string.
export default function HealthFields({ diseases, allergies, onChange }) {
  const Chip = ({ field, value, option }) => {
    const active = hasItem(value, option.value);
    return (
      <button
        type="button"
        onClick={() => onChange(field, toggleItem(value, option.value))}
        className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
          active
            ? 'border-orange-500 bg-orange-500/15 text-orange-300'
            : 'border-[var(--border-input)] bg-[var(--bg-nested)] text-gray-400 hover:border-gray-400'
        }`}
      >
        {active ? '✓ ' : ''}{option.label}
      </button>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm text-gray-400 mb-1">
          Health conditions or injuries
        </label>
        <p className="text-xs text-gray-500 mb-3">
          We adapt your workout plan and nutrition targets around these. Select any that apply.
        </p>
        <div className="flex flex-wrap gap-2">
          {CONDITION_OPTIONS.map((o) => (
            <Chip key={o.value} field="diseases" value={diseases} option={o} />
          ))}
        </div>
        <input
          type="text"
          value={diseases || ''}
          onChange={(e) => onChange('diseases', e.target.value)}
          className="w-full mt-3 bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500"
          placeholder="Or type your own, comma-separated"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Food allergies</label>
        <p className="text-xs text-gray-500 mb-3">
          Foods matching these are flagged when you search, and noted in your nutrition plan.
        </p>
        <div className="flex flex-wrap gap-2">
          {ALLERGY_OPTIONS.map((o) => (
            <Chip key={o.value} field="allergies" value={allergies} option={o} />
          ))}
        </div>
        <input
          type="text"
          value={allergies || ''}
          onChange={(e) => onChange('allergies', e.target.value)}
          className="w-full mt-3 bg-[var(--bg-nested)] border border-[var(--border-input)] rounded-xl px-4 py-2.5 text-[var(--text-primary)] text-sm focus:outline-none focus:border-orange-500"
          placeholder="Or type your own, comma-separated"
        />
      </div>
    </div>
  );
}
