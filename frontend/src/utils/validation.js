// Shared, real-time form validation. Bounds mirror the backend Pydantic
// Field(ge/le) constraints so the client and server agree (defense in depth).

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(value) {
  if (!value) return 'Email is required';
  if (!EMAIL_RE.test(value.trim())) return 'Enter a valid email address';
  return '';
}

export function validateUsername(value) {
  if (!value) return 'Username is required';
  if (value.trim().length < 3) return 'Username must be at least 3 characters';
  if (value.trim().length > 30) return 'Username must be 30 characters or fewer';
  return '';
}

// Matches backend validate_password_strength: ≥8 chars, a letter and a number.
export function validatePassword(value) {
  if (!value) return 'Password is required';
  if (value.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Za-z]/.test(value)) return 'Include at least one letter';
  if (!/[0-9]/.test(value)) return 'Include at least one number';
  return '';
}

// Numeric field bounds, keyed by field name. [min, max, label].
export const NUMERIC_BOUNDS = {
  age: [10, 115, 'Age'],
  weight: [20, 500, 'Weight'],
  height: [50, 300, 'Height'],
  workout_frequency: [1, 7, 'Workout days'],
  heart_rate: [30, 250, 'Heart rate'],
};

export function validateNumber(field, value) {
  const bound = NUMERIC_BOUNDS[field];
  if (!bound) return '';
  const [min, max, label] = bound;
  if (value === '' || value === null || value === undefined) return `${label} is required`;
  const n = Number(value);
  if (Number.isNaN(n)) return `${label} must be a number`;
  if (n < min || n > max) return `${label} must be between ${min} and ${max}`;
  return '';
}

// True only when every provided error string is empty.
export function isClean(errors) {
  return Object.values(errors).every((e) => !e);
}
