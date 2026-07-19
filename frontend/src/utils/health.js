// Quick-pick options for the health step. Disease `value`s use the exact tokens
// the backend matches on (substring, case-insensitive) so a chip selection always
// drives the workout exclusions / nutrition adjustments — free text can still be
// typed, but chips guarantee a hit.

export const CONDITION_OPTIONS = [
  { value: 'knee', label: 'Knee injury' },
  { value: 'back', label: 'Back pain' },
  { value: 'shoulder', label: 'Shoulder injury' },
  { value: 'hip', label: 'Hip pain' },
  { value: 'ankle', label: 'Ankle injury' },
  { value: 'wrist', label: 'Wrist pain' },
  { value: 'neck', label: 'Neck pain' },
  { value: 'elbow', label: 'Elbow pain' },
  { value: 'sciatica', label: 'Sciatica' },
  { value: 'herniated disc', label: 'Herniated disc' },
  { value: 'arthritis', label: 'Arthritis' },
  { value: 'osteoporosis', label: 'Osteoporosis' },
  { value: 'heart', label: 'Heart condition' },
  { value: 'hypertension', label: 'High blood pressure' },
  { value: 'asthma', label: 'Asthma' },
  { value: 'copd', label: 'COPD' },
  { value: 'diabetes', label: 'Diabetes' },
  { value: 'obesity', label: 'Obesity' },
  { value: 'hernia', label: 'Hernia' },
  { value: 'vertigo', label: 'Vertigo' },
  { value: 'epilepsy', label: 'Epilepsy' },
  { value: 'pcos', label: 'PCOS' },
  { value: 'thyroid', label: 'Thyroid condition' },
  { value: 'kidney', label: 'Kidney condition' },
  { value: 'celiac', label: 'Celiac / gluten' },
  { value: 'gerd', label: 'GERD / reflux' },
  { value: 'ibs', label: 'IBS / digestive' },
  { value: 'anemia', label: 'Anemia' },
  { value: 'gout', label: 'Gout' },
  { value: 'cholesterol', label: 'High cholesterol' },
];

export const ALLERGY_OPTIONS = [
  { value: 'peanuts', label: 'Peanuts' },
  { value: 'tree nuts', label: 'Tree nuts' },
  { value: 'dairy', label: 'Dairy' },
  { value: 'eggs', label: 'Eggs' },
  { value: 'gluten', label: 'Gluten' },
  { value: 'shellfish', label: 'Shellfish' },
  { value: 'fish', label: 'Fish' },
  { value: 'soy', label: 'Soy' },
  { value: 'sesame', label: 'Sesame' },
];

// Parse/serialize a comma-separated field into a trimmed list.
export function parseList(value) {
  return (value || '').split(',').map((s) => s.trim()).filter(Boolean);
}

export function hasItem(value, item) {
  return parseList(value).some((i) => i.toLowerCase() === item.toLowerCase());
}

export function toggleItem(value, item) {
  const items = parseList(value);
  const next = hasItem(value, item)
    ? items.filter((i) => i.toLowerCase() !== item.toLowerCase())
    : [...items, item];
  return next.join(', ');
}
