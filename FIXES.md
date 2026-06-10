# GetFit — Issue Tracker & Fix Log

All bugs, security issues, and improvements identified during development.
Each entry records what the problem was, what file(s) changed, and the fix applied.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fixed and deployed |
| 🔲 | Identified, not yet fixed |
| 🔴 | Critical / Security |
| 🟠 | Medium — functional impact |
| 🟡 | Low — code quality / UX |

---

## Security Issues

### SEC-01 — Hardcoded JWT Secret Key `🔴 ✅`
**File:** `backend/app/core/config.py`, `backend/.env`, `backend/.env.example`

**Problem:** `SECRET_KEY` had a public default value (`"getfit-super-secret-key-change-in-production"`) committed directly in code. Any attacker who reads the source can forge valid JWT tokens for any user.

**Fix:**
- Removed the default value from `config.py` — app now refuses to start if `SECRET_KEY` is not set in `.env`
- Generated a fresh 64-character hex key and set it in `.env`
- Updated `.env.example` to show a placeholder with generation instructions
- Added `email-validator` to requirements (related cleanup)

---

### SEC-02 — Deactivated Users Could Still Call the API `🔴 ✅`
**File:** `backend/app/routes/auth.py`

**Problem:** `get_current_user()` — the shared dependency used by every protected route — only verified that the JWT was valid and the user existed. It never checked `is_active`. An admin could deactivate an account, but that user's existing token continued to work indefinitely on all routes.

**Fix:** Added `is_active` check immediately after the user lookup:
```python
if not user.is_active:
    raise HTTPException(status_code=403, detail="Account is deactivated")
```
This single line covers every protected route since they all share this dependency.

---

### SEC-03 — No Email Format Validation at Registration `🔴 ✅`
**File:** `backend/app/routes/auth.py`, `backend/requirements.txt`

**Problem:** `EmailStr` was imported from Pydantic but `UserRegister.email` was typed as plain `str`. Any string (`"notanemail"`, `"@"`, `"hello"`) was accepted as a valid email at registration.

**Fix:**
- Changed `email: str` → `email: EmailStr` in `UserRegister`
- Added `email-validator` to `requirements.txt` (Pydantic's required dependency for `EmailStr`)
- Installed `email-validator==2.3.0` into the backend venv

---

## Functional Bugs

### BUG-01 — `JSON.parse` Crash on Corrupted localStorage `🟠 ✅`
**File:** `frontend/src/context/AuthContext.jsx`

**Problem:** The `AuthProvider` initialised user state by calling `JSON.parse(localStorage.getItem('user'))` with no error handling. If the stored value was corrupted (truncated by a browser crash, manually edited, or partially written), the `SyntaxError` propagated uncaught — causing a blank white screen on app load.

**Fix:** Wrapped in try-catch; on failure, clears both `user` and `token` from localStorage and returns `null` (treated as logged-out):
```js
try {
  return JSON.parse(stored);
} catch {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  return null;
}
```

---

### BUG-02 — Calorie Burn Predictor Returning 400 with No Useful Message `🟠 ✅`
**File:** `backend/app/routes/workout.py`, `frontend/src/pages/WorkoutPlan.jsx`

**Problem:** The `/workout/predict-calories` endpoint requires `gender`, `age`, `weight`, and `height` — different fields from those required for the workout plan (`fitness_level`, `goal`, `workout_frequency`). A user could have a workout plan but still fail the predictor check. On failure:
- Backend returned a generic `"Please complete your profile first"` with no detail on which fields were missing
- Frontend caught the error and always showed `"Prediction failed. Check your profile is complete."` regardless of the actual server message

**Fix (backend):** Error message now lists the specific missing fields:
```python
missing = [f for f, v in {"gender": ..., "age": ..., ...}.items() if not v]
raise HTTPException(400, detail=f"Profile incomplete — please set: {', '.join(missing)}")
```

**Fix (frontend):**
- Imported `useAuth` to read profile fields client-side
- Computed `missingFields` before rendering the predictor
- If any required fields are absent: shows a yellow warning banner listing exactly which fields are missing + a direct link to the Profile page; disables the inputs and Predict button
- Error handler now shows `e.response?.data?.detail` instead of a hardcoded string
- Prediction result rounded to whole number (`Math.round`)

---

### BUG-03 — Food Log Had No Weight Input — Fixed Serving Only `🟠 ✅`
**File:** `frontend/src/pages/CalorieTracker.jsx`

**Problem:** Clicking "+" on a search result logged the food at its default serving size with no way to adjust the amount. There was no gram input, no scaled macros, no feedback on what portion was being logged.

**Fix:** Redesigned the search results section:
- Each result now shows an inline gram input pre-filled with `serving_weight_grams` from Nutritionix (or 100g as fallback)
- Calories, protein, carbs, and fat update live as the user types a weight (proportional scaling via `serving_weight_grams` base)
- Per-100g calorie reference shown below each result
- Food is logged as `"Chicken Breast (150g)"` so the log entry includes the weight
- `logFood` now scales all nutrients by `grams / base_serving_weight` before posting

---

## UX / Code Quality

### UX-01 — `loading` State in AuthContext Was Unused `🟡 🔲`
**File:** `frontend/src/context/AuthContext.jsx`

**Problem:** A `loading` state is declared and exported but is always `false` — it is never set to `true`. Route guards (`ProtectedRoute`, `PublicRoute`, `AdminRoute`) in `App.jsx` do not check `loading`, meaning there is no loading screen during auth-state resolution.

**Status:** Identified. Low priority for a pet project (user is initialised synchronously from localStorage so there is no async gap on first render).

---

### UX-02 — Onboarding Has No Step Validation `🟡 🔲`
**File:** `frontend/src/pages/Onboarding.jsx`

**Problem:** The "Continue" button on each onboarding step does not validate whether required fields were filled. A user can advance through all steps with empty inputs. On submit, `parseInt('')` → `NaN` → serialised as `null` in JSON → stored as `NULL` in the database. This is the root cause of BUG-02 for users who skip onboarding fields.

**Status:** Identified. Fix: add field validation before allowing step advancement.

---

### UX-03 — `isProfileComplete` Check Is Too Lenient `🟡 🔲`
**File:** `frontend/src/pages/Dashboard.jsx`

**Problem:** The "Complete Profile →" banner checks only `goal`, `fitness_level`, and `weight`. It misses `age`, `height`, `gender`, and `activity_level` — all of which are required for the nutrition plan endpoint. The banner can disappear while the profile is still incomplete.

**Status:** Identified. Fix: check all seven required fields.

---

### UX-04 — Silent `catch (e) {}` Blocks Hide Errors `🟡 🔲`
**Files:** `Dashboard.jsx`, `CalorieTracker.jsx`, `StepTracker.jsx`, `WorkoutPlan.jsx`

**Problem:** Multiple empty catch blocks swallow errors silently — no console log, no user feedback. Failures in background fetches are invisible.

**Status:** Partially fixed (CalorieTracker and StepTracker now log to `console.error`). Remaining: Dashboard, WorkoutPlan background fetches.

---

### UX-05 — Step Input Accepts Non-Numeric Text `🟡 🔲`
**File:** `frontend/src/pages/StepTracker.jsx`

**Problem:** Validation was `parseInt(stepInput) < 0` — `parseInt("abc")` returns `NaN`, and `NaN < 0` is `false`, so text passes the guard.

**Status:** Identified. The `logSteps` function was rewritten in the PWA update to use `isNaN(count)` — **partially fixed** as part of the accelerometer refactor (the new code uses `parseInt(value)` with an `isNaN` check).

---

### CODE-01 — `datetime.utcnow` Deprecated in Python 3.12+ `🟡 🔲`
**Files:** `backend/app/models/logs.py`, `backend/app/models/user.py`, `backend/app/core/security.py`, `backend/app/routes/nutrition.py`, `backend/app/routes/steps.py`

**Problem:** `datetime.utcnow()` is deprecated since Python 3.12. Should be `datetime.now(timezone.utc)`.

**Status:** Identified. Low risk until Python 3.12+ is used.

---

### CODE-02 — `declarative_base` Import Deprecated `🟡 🔲`
**File:** `backend/app/core/database.py`

**Problem:** `from sqlalchemy.ext.declarative import declarative_base` is deprecated in SQLAlchemy 2.x. Should be `from sqlalchemy.orm import declarative_base`.

**Status:** Identified.

---

### CODE-03 — User Model Defines Enums but Columns Use `String` `🟡 🔲`
**File:** `backend/app/models/user.py`

**Problem:** `GenderEnum`, `GoalEnum`, `FitnessLevelEnum`, `ActivityLevelEnum` are defined but the actual columns use plain `String`. Invalid values (e.g. `goal = "banana"`) can be stored without any DB-level rejection.

**Status:** Identified.

---

### CODE-04 — CORS Hardcodes `localhost` Instead of Using Config `🟡 🔲`
**File:** `backend/app/main.py`

**Problem:** `FRONTEND_URL` is defined in `Settings` but the CORS middleware hardcodes `["http://localhost:5173", "http://localhost:3000"]` and ignores the config value.

**Status:** Identified.

---

### CODE-05 — Synchronous `requests` in FastAPI Routes `🟡 🔲`
**File:** `backend/app/routes/nutrition.py`

**Problem:** The Nutritionix food search uses the synchronous `requests` library with no timeout, blocking the thread for the full duration of the external call. FastAPI is async-native; `httpx` with `async/await` is the correct choice.

**Status:** Identified.

---

### CODE-06 — Unused Imports `🟡 🔲`
**Files:** `backend/app/routes/nutrition.py` (`List`, `date`), `backend/app/routes/steps.py` (`date`), `backend/app/routes/workout.py` (`datetime`)

**Status:** Identified.

---

### CODE-07 — `random.seed(42)` Makes All Workout Plans Identical `🟡 🔲`
**File:** `backend/app/services/workout_recommender.py`

**Problem:** A fixed seed means every user with the same profile parameters receives the exact same workout. The comment says "consistent recommendations" but this removes all variety across users.

**Status:** Identified. Intentional for now but worth revisiting.

---

### CODE-08 — No Password Strength Validation `🟡 🔲`
**File:** `backend/app/routes/auth.py`

**Problem:** Registration accepts any password including empty strings.

**Status:** Identified.

---

## Feature Additions

### FEAT-01 — PWA Support `✅`
**Files:** `frontend/vite.config.js`, `frontend/package.json`

Added `vite-plugin-pwa` with:
- Web app manifest (name, theme colour, standalone display, icon)
- Workbox service worker (precaches all assets, NetworkFirst for API responses)
- App is installable from Chrome (Android) and Safari (iOS) via "Add to Home Screen"

---

### FEAT-02 — Responsive Mobile Layout `✅`
**Files:** `frontend/src/components/Layout.jsx`, all page files

- Desktop: fixed 256px sidebar (unchanged)
- Mobile (`< md` breakpoint): sidebar hidden, replaced with a fixed bottom navigation bar (icons + labels)
- Main content: `ml-0 md:ml-64`, `pb-24 md:pb-8` to clear the bottom nav
- All grid layouts converted to responsive Tailwind variants:
  - `grid-cols-4` → `grid-cols-2 md:grid-cols-4`
  - `grid-cols-3` → `grid-cols-1 md:grid-cols-3`
  - `grid-cols-5` (Admin) → `grid-cols-2 md:grid-cols-5`

---

### FEAT-03 — Live Accelerometer Step Counter `✅`
**File:** `frontend/src/pages/StepTracker.jsx`

Added `useStepCounter` hook:
- Listens to `DeviceMotionEvent` (available in modern mobile browsers)
- Peak-detection on acceleration magnitude (`√(x²+y²+z²)`) with configurable threshold (13 m/s²) and minimum interval (280ms) between steps
- iOS 13+: requests `DeviceMotionEvent.requestPermission()` on user gesture
- Start/Stop UI with live pulsing counter
- On Stop: counted steps pre-fill the manual save input
- Falls back gracefully (hidden) on desktop or unsupported browsers
