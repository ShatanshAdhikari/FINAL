# GetFit — System Documentation

> Personalized Fitness & Nutrition Web Application  
> Stack: React (Vite) · FastAPI · SQLite · Scikit-learn  
> Branch: `feat/improvements` — last updated 2026-06-21

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture Diagram](#2-system-architecture-diagram)
3. [Frontend Structure](#3-frontend-structure)
4. [Backend Structure](#4-backend-structure)
5. [Database Schema](#5-database-schema)
6. [API Reference](#6-api-reference)
7. [ML & Algorithm Layer](#7-ml--algorithm-layer)
8. [Authentication Flow](#8-authentication-flow)
9. [Data Flow Diagrams](#9-data-flow-diagrams)
10. [How to Run](#10-how-to-run)
11. [Bug Fixes & Change Log](#11-bug-fixes--change-log)
12. [Troubleshooting](#12-troubleshooting)
13. [Technology Stack](#13-technology-stack)
14. [Role System & Permissions](#14-role-system--permissions)
15. [API Request & Response Examples](#15-api-request--response-examples)
16. [Testing](#16-testing)

---

## 1. Project Overview

GetFit is a full-stack fitness and nutrition application that provides:

| Feature | Description |
|---------|-------------|
| 🔐 Auth | JWT-based registration & login with rate limiting |
| 🏋️ Workout Plans | Rule-based personalized weekly workout generator |
| 🔥 Calorie Predictor | ML model (Lasso Regression) — predicts calories burned with confidence range |
| 🥗 Nutrition Tracker | Food logging with macro tracking + USDA FoodData Central API |
| 👟 Step Tracker | Daily step logging with live accelerometer counter |
| 📊 Dashboard | Summary of today's activity, nutrition totals, and progress charts |
| 🛡️ Admin Panel | Admin-only user management panel |
| 🌗 Dark / Light Mode | Toggle persisted in localStorage, applied to all pages |

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER'S BROWSER                             │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                  REACT FRONTEND  (Port 5173)                 │  │
│   │                                                              │  │
│   │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │  │
│   │  │  Login / │  │Dashboard │  │  Workout  │  │ Calorie   │  │  │
│   │  │ Register │  │          │  │   Plan    │  │ Tracker   │  │  │
│   │  └──────────┘  └──────────┘  └───────────┘  └───────────┘  │  │
│   │                                                              │  │
│   │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │  │
│   │  │   Step   │  │ Profile  │  │  Admin    │  │Onboarding │  │  │
│   │  │ Tracker  │  │          │  │  Panel    │  │           │  │  │
│   │  └──────────┘  └──────────┘  └───────────┘  └───────────┘  │  │
│   │                                                              │  │
│   │  ┌──────────────────────┐   ┌──────────────────────────┐   │  │
│   │  │   AuthContext (JWT)  │   │   axios.js (HTTP Client) │   │  │
│   │  └──────────────────────┘   └──────────────────────────┘   │  │
│   └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  HTTP/REST (JSON)
                                │  Bearer Token (JWT)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND  (Port 8000)                      │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                        API ROUTES                            │  │
│   │  /auth    /profile    /workout    /nutrition  /steps  /admin │  │
│   └────────────────────────────┬─────────────────────────────────┘  │
│                                │                                    │
│         ┌──────────────────────┼────────────────────┐              │
│         ▼                      ▼                    ▼              │
│  ┌─────────────┐     ┌──────────────────┐   ┌─────────────────┐   │
│  │  Services   │     │   ML Module      │   │  Core / Auth    │   │
│  │─────────────│     │──────────────────│   │─────────────────│   │
│  │ Workout     │     │ Calorie          │   │ JWT Security    │   │
│  │ Recommender │     │ Predictor        │   │ bcrypt hashing  │   │
│  │ (rule-based)│     │ (Lasso Regress.) │   │ Settings/Config │   │
│  │             │     │                  │   │                 │   │
│  │ Nutrition   │     │ calorie_model.pkl│   │ Database conn.  │   │
│  │ Calculator  │     │ (trained on boot)│   │ (SQLAlchemy)    │   │
│  │ (Mifflin)   │     └──────────────────┘   └─────────────────┘   │
│  └─────────────┘                                                   │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                      DATA MODELS                             │  │
│   │    User       CalorieLog      WorkoutLog       StepLog       │  │
│   └────────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────┘
                                 │  SQLAlchemy ORM
                                 ▼
                    ┌────────────────────────┐
                    │   SQLite Database      │
                    │   (getfit.db)          │
                    │                        │
                    │  users                 │
                    │  calorie_logs          │
                    │  workout_logs          │
                    │  step_logs             │
                    └────────────────────────┘

                                              ┌────────────────────────┐
                    (Optional external API) ──►│  Nutritionix API       │
                                              │  /v2/natural/nutrients  │
                                              └────────────────────────┘
```

---

## 3. Frontend Structure

```
frontend/
├── src/
│   ├── main.jsx              # React entry point; applies saved theme class before render
│   ├── App.jsx               # Router + route guards + ErrorBoundary wrappers
│   ├── index.css             # Tailwind import + CSS custom properties for theming
│   ├── api/
│   │   └── axios.js          # Axios instance (base URL, auth headers, 401 handler)
│   ├── context/
│   │   ├── AuthContext.jsx   # Global auth state (user, token, login, logout)
│   │   └── ThemeContext.jsx  # Dark/light theme state + toggle (localStorage-backed)
│   ├── components/
│   │   ├── Layout.jsx        # Sidebar nav + Outlet wrapper + Sun/Moon toggle button
│   │   ├── ErrorBoundary.jsx # Class component — catches render errors, shows fallback UI
│   │   └── Skeleton.jsx      # Animated placeholder components (Skeleton, CardSkeleton, etc.)
│   └── pages/
│       ├── Login.jsx         # Login form
│       ├── Register.jsx      # Registration form
│       ├── Onboarding.jsx    # First-time profile setup (3-step wizard)
│       ├── Dashboard.jsx     # Activity summary + charts + weight logging
│       ├── WorkoutPlan.jsx   # Weekly workout plan + calorie predictor + log history
│       ├── CalorieTracker.jsx# Food search + gram input + macro logging
│       ├── StepTracker.jsx   # Daily step input + live accelerometer + history
│       ├── Profile.jsx       # Edit profile & view nutrition plan
│       └── AdminPanel.jsx    # Admin-only user table
```

### Theming

All background, border, and primary text colours are driven by CSS custom properties defined in `index.css`. Adding `dark` or `light` to `<html>` switches the full theme:

| CSS Variable | Dark | Light |
|---|---|---|
| `--bg-base` | `#0f0f0f` | `#f3f4f6` |
| `--bg-surface` | `#111118` | `#ffffff` |
| `--bg-nested` | `#1a1a24` | `#f1f5f9` |
| `--bg-muted` | `#222222` | `#e5e7eb` |
| `--border` | `#222222` | `#e5e7eb` |
| `--border-input` | `#333333` | `#d1d5db` |
| `--text-primary` | `#ffffff` | `#111827` |

`ThemeContext` reads the preference from `localStorage` on mount. `main.jsx` applies the class to `<html>` before React renders to prevent a flash of the wrong theme.

### Route Guards

```
/login, /register      → PublicRoute   (redirects to /dashboard if logged in)
/dashboard, /workout,
/calories, /steps,
/profile               → ProtectedRoute (redirects to /login if not logged in)
/admin                 → AdminRoute    (requires is_admin=true)
/onboarding            → ProtectedRoute
```

### Vite Dev Proxy

The frontend `axios.js` uses `baseURL: '/api'`. Vite's dev server proxies every `/api/*` request to `http://localhost:8000`, stripping the `/api` prefix, so no CORS issue exists during development:

```
Frontend call:  GET  /api/workout/plan
  ── Vite proxy ──►  GET  http://localhost:8000/workout/plan
```

Configured in `vite.config.js`:

```js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

In a production build, Nginx (or equivalent) must replicate this proxy rule.

---

### Axios 401 Interceptor

`axios.js` auto-logs the user out and redirects to `/login` on any **401 Unauthorized** response from the API — **except** on `/auth/*` endpoints (login/register), where a 401 means wrong credentials and should show an error message instead.

```js
// src/api/axios.js
const isAuthEndpoint = error.config?.url?.startsWith('/auth/');
if (error.response?.status === 401 && !isAuthEndpoint) {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

---

## 4. Backend Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app, CORS, rate-limiter setup, route registration
│   ├── core/
│   │   ├── config.py         # Settings (JWT secret, DB URL, USDA/Nutritionix keys)
│   │   ├── database.py       # SQLAlchemy engine, session, Base
│   │   └── security.py       # bcrypt hashing (direct), JWT create/decode
│   ├── models/
│   │   ├── user.py           # User model (profile + auth fields, roles)
│   │   └── logs.py           # CalorieLog, WorkoutLog, StepLog, WeightLog + indexes
│   ├── routes/
│   │   ├── auth.py           # /auth/register, /auth/login (rate-limited), /auth/me
│   │   ├── profile.py        # PUT /profile, GET /profile/nutrition-plan, weight logging
│   │   ├── workout.py        # /workout/plan, /workout/log, /workout/logs, predict-calories
│   │   ├── nutrition.py      # /nutrition/search (USDA), /nutrition/log, logs, delete
│   │   ├── steps.py          # /steps/log, /steps/today, /steps/history
│   │   └── admin.py          # Admin & super-admin endpoints + ML retrain
│   ├── services/
│   │   ├── workout_recommender.py  # Rule-based workout plan generator
│   │   └── nutrition_calculator.py # BMR/TDEE/macro calculator (Mifflin-St Jeor)
│   └── ml/
│       ├── calorie_predictor.py    # Lasso Regression pipeline; returns confidence range
│       └── calorie_model.pkl       # Saved model (auto-generated on first run)
├── tests/                    # pytest test suite (50 tests)
│   ├── conftest.py           # In-memory SQLite (StaticPool) + TestClient fixture
│   ├── test_auth.py          # Registration, login, /auth/me
│   ├── test_nutrition_calculator.py # BMR, TDEE, macros, step calories
│   ├── test_calorie_predictor.py    # Model inference, confidence range
│   └── test_workout_recommender.py  # Plan generation, splits, determinism
├── seed_users.py             # One-shot database seeder (1 super-admin, 2 admins, 5 users)
├── create_admin.py           # CLI to create or promote admin accounts
├── requirements.txt          # Includes slowapi, pytest, httpx
└── .env.example              # Template — copy to .env and fill in values (never commit .env)
```

### Password Hashing — `security.py`

Passwords are hashed using **bcrypt directly** (not via passlib), making the app compatible with any bcrypt version (4.x, 5.x):

```python
import bcrypt

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

> ⚠️ **Do not revert to `passlib`** — passlib 1.7.x is incompatible with bcrypt ≥ 4.0 and causes 500 errors on all login/register requests.

---

## 5. Database Schema

```
┌─────────────────────────────────────────┐
│                  users                  │
├──────────────────┬──────────────────────┤
│ id               │ INTEGER (PK)         │
│ email            │ STRING (unique)      │
│ username         │ STRING (unique)      │
│ hashed_password  │ STRING               │
│ is_admin         │ BOOLEAN (default: F) │
│ is_super_admin   │ BOOLEAN (default: F) │
│ is_active        │ BOOLEAN (default: T) │
│ created_at       │ DATETIME             │
│ age              │ INTEGER              │
│ gender           │ STRING (male/female) │
│ weight           │ FLOAT (kg)           │
│ height           │ FLOAT (cm)           │
│ fitness_level    │ STRING               │
│ goal             │ STRING               │
│ activity_level   │ STRING               │
│ workout_frequency│ INTEGER (days/week)  │
│ equipment        │ STRING (comma-sep.)  │
└──────────────────┴──────────────────────┘
          │ 1
          │
          ├────────────────────────────────────────────┐
          │                                            │
          ▼ many                                       ▼ many
┌──────────────────────────┐          ┌───────────────────────────┐
│       calorie_logs       │          │       workout_logs         │
├──────────────┬───────────┤          ├──────────────┬────────────┤
│ id           │ INT (PK)  │          │ id           │ INT (PK)   │
│ user_id      │ FK→users  │          │ user_id      │ FK→users   │
│ food_name    │ STRING    │          │ exercise_name│ STRING     │
│ calories     │ FLOAT     │          │ duration_min │ FLOAT      │
│ protein      │ FLOAT     │          │ heart_rate   │ FLOAT      │
│ carbs        │ FLOAT     │          │ calories_burn│ FLOAT      │
│ fat          │ FLOAT     │          │ notes        │ TEXT       │
│ meal_type    │ STRING    │          │ logged_at    │ DATETIME   │
│ logged_at    │ DATETIME  │          └───────────────────────────┘
└──────────────────────────┘

          │ 1 (users)
          ├───────────────────────────────────────────┐
          ▼ many                                      ▼ many
┌──────────────────────────┐          ┌───────────────────────────┐
│        step_logs         │          │       weight_logs          │
├──────────────┬───────────┤          ├──────────────┬────────────┤
│ id           │ INT (PK)  │          │ id           │ INT (PK)   │
│ user_id      │ FK→users  │          │ user_id      │ FK→users   │
│ steps        │ INTEGER   │          │ weight       │ FLOAT (kg) │
│ calories_from│ FLOAT     │          │ date         │ STRING     │
│ date         │ STRING    │          │ logged_at    │ DATETIME   │
│              │ (YYYY-MM) │          └───────────────────────────┘
└──────────────────────────┘
```

> **Indexes:** All log tables have `Index` definitions on `user_id` and `logged_at`/`date` to keep queries fast as data grows.

---

## 6. API Reference

Base URL: `http://localhost:8000`  
Interactive Docs: `http://localhost:8000/docs`

### Authentication — `/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Register new user, returns JWT token. **Rate limited: 10/min per IP.** |
| POST | `/auth/login` | ❌ | Login (email or username + password), returns JWT token. **Rate limited: 10/min per IP.** |
| GET | `/auth/me` | ✅ | Get current user details |

### Profile — `/profile`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| PUT | `/profile` | ✅ | Update profile (weight, height, goal, etc.) |
| GET | `/profile/nutrition-plan` | ✅ | Calculate BMR/TDEE/macros from saved profile |

### Profile — additional endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/profile/weight` | ✅ | Log today's weight (upserts by date) |
| GET | `/profile/weight-history?days=90` | ✅ | Weight log history |

### Workout — `/workout`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/workout/plan` | ✅ | Generate personalised weekly workout plan |
| POST | `/workout/predict-calories` | ✅ | Predict calories burned — returns point + confidence range |
| POST | `/workout/log` | ✅ | Log a completed workout session |
| GET | `/workout/logs?skip=0&limit=20` | ✅ | Paginated workout log history (max 100 per request) |
| DELETE | `/workout/log/{id}` | ✅ | Delete a specific workout log entry |

### Nutrition — `/nutrition`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/nutrition/search` | ❌ | Search food nutrition (Nutritionix or mock) |
| POST | `/nutrition/log` | ✅ | Log a food entry |
| GET | `/nutrition/logs/today` | ✅ | Today's food log + macro totals |
| GET | `/nutrition/logs/history?days=7` | ✅ | Past N days of calorie history |
| DELETE | `/nutrition/log/{id}` | ✅ | Delete a food log entry |

### Steps — `/steps`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/steps/log` | ✅ | Log daily steps (upserts by date) |
| GET | `/steps/today` | ✅ | Today's steps + estimated calories + BMR |
| GET | `/steps/history?days=7` | ✅ | Past N days step history |

### Admin — `/admin`

> All admin endpoints require `is_admin = true`. Endpoints marked **Super-Admin** additionally require `is_super_admin = true`.

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| GET | `/admin/users` | Admin | List all users |
| GET | `/admin/users/{id}` | Admin | Get a single user's details |
| DELETE | `/admin/users/{id}` | Admin | Delete a user |
| PATCH | `/admin/users/{id}/toggle-active` | Admin | Activate / deactivate a user |
| GET | `/admin/stats` | Admin | Platform-wide statistics |
| PATCH | `/admin/users/{id}/promote-admin` | Super-Admin | Promote user → admin |
| PATCH | `/admin/users/{id}/demote-admin` | Super-Admin | Demote admin → user |
| PATCH | `/admin/users/{id}/promote-super-admin` | Super-Admin | Promote user → super-admin |
| PATCH | `/admin/users/{id}/demote-super-admin` | Super-Admin | Demote super-admin → admin |

---

## 7. ML & Algorithm Layer

### 7.1 Calorie Burn Predictor (ML)

**File:** `backend/app/ml/calorie_predictor.py`

**Model:** Lasso Regression with Polynomial Features (degree 3)

**Pipeline:**
```
Input Features → StandardScaler → PolynomialFeatures(degree=3) → Lasso(alpha=0.01)
```

**Input features:**
| Feature | Type | Description |
|---------|------|-------------|
| gender | 0/1 | 0 = female, 1 = male |
| age | int | User age in years |
| height | float | Height in cm |
| weight | float | Weight in kg |
| duration | float | Workout duration in minutes |
| heart_rate | float | Heart rate in BPM |
| body_temp | float | Body temperature in °C (default 37.5) |

**Output:** The predictor returns a point estimate plus a ±2σ confidence interval derived from the model's RMSE (0.30 cal):
```json
{ "calories": 334.17, "confidence_low": 333.57, "confidence_high": 334.77 }
```

**Performance (EDA notebook):** R² = 0.9999, MAE = 0.26 cal, RMSE = 0.30 cal on the 15,000-sample Kaggle dataset.

**Lifecycle:** Model is trained on first startup and saved to `calorie_model.pkl`. Falls back to synthetic data with a warning if the real dataset is not present in `backend/app/ml/data/`.

---

### 7.2 Workout Recommender (Rule-Based)

**File:** `backend/app/services/workout_recommender.py`

**Logic based on workout frequency:**

```
≤ 3 days/week  →  Full Body  (Push + Pull + Legs + Core, 2 exercises each)
4 days/week    →  Upper / Lower Split
                   Mon/Wed: Upper (Push + Pull + Core)
                   Tue/Thu: Lower (Legs + Core)
5-7 days/week  →  Push / Pull / Legs Split
                   + Core & Cardio day if 7 days
```

**Sets/Reps are adjusted per goal:**

| Goal | Reps | Rest | Intensity |
|------|------|------|-----------|
| Fat Loss | 12–20 | 20–45s | Moderate–High |
| Muscle Gain | 6–12 | 60–90s | Moderate–High |
| Strength | 1–8 | 2–5 min | Max |
| Endurance | 15–25 | 15–30s | Low–Moderate |

---

### 7.3 Nutrition Calculator

**File:** `backend/app/services/nutrition_calculator.py`

**Formulas used:**

```
BMR (Mifflin-St Jeor):
  Male:   10×weight + 6.25×height − 5×age + 5
  Female: 10×weight + 6.25×height − 5×age − 161

TDEE = BMR × activity_multiplier
  sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9

Calorie Goal:
  fat_loss    = TDEE − 500
  muscle_gain = TDEE + 300
  endurance   = TDEE + 150
  strength    = TDEE

Calories from steps = steps × 0.05 × (weight / 70)
```

**Protein targets (g per kg of body weight):**

| Fitness Level | Fat Loss | Muscle Gain | Strength | Endurance |
|---|---|---|---|---|
| Beginner | 1.6 g/kg | 1.8 g/kg | 1.8 g/kg | 1.4 g/kg |
| Intermediate | 1.8 g/kg | 2.0 g/kg | 2.0 g/kg | 1.6 g/kg |
| Advanced | 2.0 g/kg | 2.2 g/kg | 2.4 g/kg | 1.8 g/kg |

**Fat & carb split of remaining calories after protein:**

| Goal | Fat % | Carb % |
|---|---|---|
| Fat Loss | 35% | 65% |
| Muscle Gain | 25% | 75% |
| Strength | 30% | 70% |
| Endurance | 20% | 80% |

---

## 8. Authentication Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Browser │         │   Frontend   │         │   Backend    │
└────┬─────┘         └──────┬───────┘         └──────┬───────┘
     │                      │                        │
     │  Enter credentials   │                        │
     │─────────────────────►│                        │
     │                      │  POST /auth/login       │
     │                      │───────────────────────►│
     │                      │                        │ bcrypt.checkpw()
     │                      │                        │ verify password
     │                      │                        │ check is_active
     │                      │  { access_token, user }│
     │                      │◄───────────────────────│
     │                      │                        │
     │                      │ localStorage:           │
     │                      │  token = access_token   │
     │                      │  user  = user object    │
     │                      │ AuthContext.setUser()   │
     │                      │                        │
     │  (subsequent calls)  │                        │
     │                      │  GET /workout/plan      │
     │                      │  Authorization: Bearer  │
     │                      │  <token>               │
     │                      │───────────────────────►│
     │                      │                        │ jwt.decode(token)
     │                      │                        │ sub → user_id (int)
     │                      │                        │ DB lookup by id
     │                      │  { weekly_plan }       │
     │                      │◄───────────────────────│
     │  Render page         │                        │
     │◄─────────────────────│                        │
```

**Token details:**

| Property | Value |
|----------|-------|
| Algorithm | `HS256` |
| Expiry | `24 hours` (1440 minutes) |
| `sub` claim | `str(user.id)` — stored as **string** per JWT RFC 7519 |
| Decode | `int(payload["sub"])` — converted back to int for DB query |

> ⚠️ The `sub` claim **must be a string**. `python-jose 3.5+` raises `JWTError: Subject must be a string` when decoding a token whose `sub` is an integer — causing all authenticated endpoints to return 401.

**Login error handling:**  
If login returns 401 (wrong credentials), the error toast (`"Invalid credentials"`) is shown in-place. The global 401 interceptor is **bypassed** for `/auth/*` routes so it does not trigger a page reload before the toast renders.

---

## 9. Data Flow Diagrams

### Workout Plan Generation

```
User clicks "Get My Plan"
        │
        ▼
GET /workout/plan  (with JWT)
        │
        ▼
Backend checks user profile fields:
  fitness_level ✓  goal ✓  workout_frequency ✓
        │
        ▼
workout_recommender.generate_workout_plan()
        │
        ├── determine split type (full body / upper-lower / PPL)
        ├── select exercises from EXERCISE_DATABASE
        └── apply sets/reps/rest from goal config
        │
        ▼
Return { goal, fitness_level, days_per_week, weekly_plan }
        │
        ▼
Frontend renders day-by-day exercise cards
```

### Calorie Logging Flow

```
User types food name
        │
        ▼
POST /nutrition/search { query: "chicken rice" }
        │
        ├── If NUTRITIONIX_APP_ID set → call Nutritionix API
        └── Else → return mock data (200 cal, 10g protein...)
        │
        ▼
User selects food, confirms macros
        │
        ▼
POST /nutrition/log { food_name, calories, protein, carbs, fat, meal_type }
        │
        ▼
CalorieLog saved to SQLite
        │
        ▼
GET /nutrition/logs/today → recalculate totals
        │
        ▼
Dashboard updates macro rings
```

---

## 10. How to Run

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

### First-Time Setup

```bash
# 1. Create the virtual environment
cd backend
python -m venv venv

# 2. Install Python dependencies
venv\Scripts\pip install -r requirements.txt

# 3. Seed the database (creates all test accounts)
venv\Scripts\python seed_users.py
```

```bash
# 4. Install frontend dependencies
cd frontend
npm install
```

### Starting the App

#### Option A — One command (recommended)

```
double-click  start-all.bat
```

Opens the backend and frontend **each in their own terminal window**.

#### Option B — Separately

| Script | What it does |
|--------|-------------|
| `start-backend.bat` | Starts FastAPI on `:8000` using the venv Python |
| `start-frontend.bat` | Starts Vite dev server on `:5173` (auto-runs `npm install` if needed) |

#### Option C — Manual (terminal)

**Backend:**
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> ⚠️ Always use `venv\Scripts\python.exe`, **not** the bare `python` command. Running with the system Python will cause package conflicts (see §12).

**Frontend:**
```bash
cd frontend
npm run dev
```

### URLs

| Service | URL |
|---------|-----|
| Frontend App | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Swagger Docs | http://localhost:8000/docs |
| API ReDoc | http://localhost:8000/redoc |

### Seeded Test Accounts

Run `venv\Scripts\python seed_users.py` to populate these accounts:

| Role | Username | Email | Password |
|------|----------|-------|----------|
| Super-Admin | `superadmin` | superadmin@getfit.com | `SuperAdmin@123` |
| Admin | `admin_alex` | admin1@getfit.com | `Admin@1234` |
| Admin | `admin_sara` | admin2@getfit.com | `Admin@1234` |
| User | `john_doe` | john.doe@example.com | `User@1234` |
| User | `jane_smith` | jane.smith@example.com | `User@1234` |
| User | `mike_chen` | mike.chen@example.com | `User@1234` |
| User | `priya_patel` | priya.patel@example.com | `User@1234` |
| User | `carlos_garcia` | carlos.garcia@example.com | `User@1234` |

### Environment Variables

`backend/.env` is **not committed to git** — copy `backend/.env.example` and fill in your values:

```bash
cp backend/.env.example backend/.env
```

```env
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key-here

DATABASE_URL=sqlite:///./getfit.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# USDA FoodData Central (free, no signup for DEMO_KEY)
# Get a personal key at https://fdc.nal.usda.gov/api-guide.html for higher rate limits
USDA_API_KEY=DEMO_KEY

# Optional: Nutritionix (premium, richer NLP search). Leave blank to use USDA.
NUTRITIONIX_APP_ID=
NUTRITIONIX_API_KEY=

FRONTEND_URL=http://localhost:5173
```

| Variable | Default | Required | Description |
|---|---|:---:|---|
| `SECRET_KEY` | *(none — must be set)* | **Yes** | JWT signing secret. App refuses to start if missing. Generate with `secrets.token_hex(32)`. |
| `ALGORITHM` | `HS256` | No | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 h) | No | Token lifetime in minutes |
| `DATABASE_URL` | `sqlite:///./getfit.db` | No | SQLAlchemy database URL |
| `USDA_API_KEY` | `DEMO_KEY` | No | USDA FoodData Central key — `DEMO_KEY` allows 30 req/hour |
| `NUTRITIONIX_APP_ID` | *(empty)* | No | If set alongside `NUTRITIONIX_API_KEY`, Nutritionix is used instead of USDA |
| `NUTRITIONIX_API_KEY` | *(empty)* | No | Nutritionix API key |
| `FRONTEND_URL` | `http://localhost:5173` | No | Allowed CORS origin |

> ⚠️ **Never commit `.env`** — it is listed in `.gitignore`. Use `.env.example` as a safe template for other contributors.

---

## 11. Bug Fixes & Change Log

### v1.2.0 — 2026-06-21

#### Security — Credential Exposure in Git History

**Problem:** `backend/.env` (containing real `SECRET_KEY` and `USDA_API_KEY` values) was tracked by git and committed to the repository. Anyone with repo read access could use these values to forge JWT tokens or exhaust the USDA API quota.

**Fix:**
- Added root `.gitignore` that excludes `.env`, `__pycache__/`, `*.pkl`, `*.db`, `*.log`, `venv/`, and `node_modules/`
- Removed `backend/.env` from git tracking via `git rm --cached`
- Generated a new `SECRET_KEY` via `secrets.token_hex(32)`
- Restored `backend/.env.example` with placeholder values and generation instructions

**Files:** `.gitignore`, `backend/.env.example`

---

#### Security — Rate Limiting on Auth Endpoints

**Problem:** `/auth/login` and `/auth/register` had no brute-force protection — an attacker could make unlimited login attempts.

**Fix:** Added `slowapi` middleware. Both endpoints are capped at **10 requests/minute per IP**. Exceeding the limit returns `429 Too Many Requests`.

**Files:** `backend/app/main.py`, `backend/app/routes/auth.py`, `backend/requirements.txt`

---

#### Feature — DELETE /workout/log/{id}

**Problem:** The README listed `DELETE /workout/log/{id}` but the endpoint was never implemented. Users could log workouts but had no way to remove them.

**Fix:** Added the handler to `workout.py` (same ownership check as `DELETE /nutrition/log/{id}`). Wired up a trash icon button in `WorkoutPlan.jsx`.

**Files:** `backend/app/routes/workout.py`, `frontend/src/pages/WorkoutPlan.jsx`

---

#### Feature — Pydantic Input Validation with Bounds

**Problem:** Routes accepted physically impossible values — negative ages, zero weights, heart rates of 999 BPM.

**Fix:** Added `Field(ge=..., le=...)` constraints to all numeric fields and a `pattern=` regex for date strings:

| Field | Range |
|---|---|
| age | 10 – 120 |
| weight | 20 – 500 kg |
| height | 50 – 300 cm |
| heart_rate | 30 – 250 BPM |
| duration_minutes | 1 – 600 min |
| steps | 0 – 100,000 |
| date | `YYYY-MM-DD` regex |

Invalid requests now return `422 Unprocessable Entity` with a clear field-level error message.

**Files:** `backend/app/routes/profile.py`, `backend/app/routes/workout.py`, `backend/app/routes/steps.py`

---

#### Feature — Paginated Workout Logs

**Problem:** `GET /workout/logs` was hardcoded to `.limit(50)` with no way to fetch older entries.

**Fix:** Added `?skip=0&limit=20` query parameters. `limit` is capped server-side at 100 to prevent abuse.

**Files:** `backend/app/routes/workout.py`

---

#### Feature — Calorie Predictor Confidence Range

**Problem:** The calorie predictor returned a bare float with no indication of how accurate the estimate was.

**Fix:** The endpoint now returns `{ "predicted_calories_burned": float, "confidence_low": float, "confidence_high": float }`. The range is ±2σ around the point estimate, derived from the model's RMSE of 0.30 cal. The frontend displays this as e.g. `"47 kcal (46–48 kcal range)"`.

**Files:** `backend/app/ml/calorie_predictor.py`, `backend/app/routes/workout.py`, `frontend/src/pages/WorkoutPlan.jsx`

---

#### Feature — Database Indexes

**Problem:** No indexes existed on frequently queried columns — queries would table-scan as data grew.

**Fix:** Added `Index` definitions on `user_id` and `logged_at`/`date` for `CalorieLog`, `WorkoutLog`, `StepLog`, and `WeightLog`.

**Files:** `backend/app/models/logs.py`

---

#### Feature — Dark / Light Mode Toggle

**Problem:** The app was forced dark with no way for users to switch to a light theme.

**Fix:**
- Added `ThemeContext.jsx` — stores preference in `localStorage`, applies `dark` or `light` class to `<html>`
- `main.jsx` applies the class synchronously before React renders to avoid a flash
- Sun/Moon toggle button added to desktop sidebar footer and mobile bottom nav
- All hardcoded hex colour classes (`bg-[#111118]`, `border-[#222]`, `text-white`, etc.) replaced with CSS custom property references (`bg-[var(--bg-surface)]`, etc.) across all 9 page files, Layout, and shared components
- Recharts tooltip inline styles and SVG stroke colours are also theme-aware

**Files:** `frontend/src/context/ThemeContext.jsx` (new), `frontend/src/index.css`, `frontend/src/main.jsx`, `frontend/src/components/Layout.jsx`, all page files

---

#### Feature — Error Boundaries

**Problem:** Any unhandled JavaScript render error crashed the entire app with a blank screen.

**Fix:** New `ErrorBoundary` class component wraps every protected route. On error, it shows a friendly card with a "Try again" button that resets the error state.

**Files:** `frontend/src/components/ErrorBoundary.jsx` (new), `frontend/src/App.jsx`

---

#### Feature — Loading Skeletons

**Problem:** Pages displayed a plain `"Loading..."` text string while data was fetching.

**Fix:** New `Skeleton`, `CardSkeleton`, `StatSkeleton`, and `ListSkeleton` components render animated grey placeholder bars in the shape of the real content.

**Files:** `frontend/src/components/Skeleton.jsx` (new), `frontend/src/pages/Dashboard.jsx`, `frontend/src/pages/WorkoutPlan.jsx`

---

### v1.1.0 — 2026-05-26

#### Security Fix 1 — Hardcoded JWT Secret Key

**Root cause:** `SECRET_KEY` had a public default value (`"getfit-super-secret-key-change-in-production"`) baked into `config.py`. Anyone reading the source code could forge valid JWT tokens for any user account.

**Fix:**
- Removed the default value from `config.py` — the app now **refuses to start** if `SECRET_KEY` is not present in `.env`
- Generated a fresh 64-character hex key via `secrets.token_hex(32)` and stored it in `.env`
- Updated `.env.example` to show a placeholder with generation instructions

**File:** `backend/app/core/config.py`, `backend/.env`, `backend/.env.example`

---

#### Security Fix 2 — Deactivated Users Could Still Call the API

**Root cause:** `get_current_user()` — the shared dependency used by every protected route — verified that the JWT was valid and the user existed, but never checked `is_active`. An admin could deactivate an account in the Admin Panel, yet that user's existing token continued to work on all endpoints indefinitely.

**Fix:** Added a single `is_active` check inside `get_current_user()`:
```python
if not user.is_active:
    raise HTTPException(status_code=403, detail="Account is deactivated")
```
Because this function is a shared dependency injected by every route, one line fixes all protected endpoints.

**File:** `backend/app/routes/auth.py`

---

#### Security Fix 3 — No Email Format Validation at Registration

**Root cause:** `EmailStr` was imported from Pydantic in `auth.py` but `UserRegister.email` was declared as plain `str`. Any string (`"notanemail"`, `"@"`, `"hello"`) was accepted as a valid email address at registration.

**Fix:**
- Changed `email: str` → `email: EmailStr` in `UserRegister`
- Added `email-validator` to `requirements.txt` (Pydantic's required dependency for `EmailStr`)
- Installed `email-validator==2.3.0` + `dnspython==2.8.0` into the backend venv

**File:** `backend/app/routes/auth.py`, `backend/requirements.txt`

---

#### Bug Fix 1 — `JSON.parse` Could Crash the Entire App on Load

**Root cause:** `AuthProvider` initialised the user state with `JSON.parse(localStorage.getItem('user'))` and no error handling. If the stored value was corrupted (browser crash, manual edit, partial write), the `SyntaxError` propagated uncaught — resulting in a blank white screen.

**Fix:** Wrapped in try-catch; on failure, clears both `user` and `token` from localStorage and returns `null` (treated as a logged-out state):
```js
try {
  return JSON.parse(stored);
} catch {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  return null;
}
```

**File:** `frontend/src/context/AuthContext.jsx`

---

#### Bug Fix 2 — Calorie Burn Predictor Returning 400 with No Useful Message

**Root cause:** The `/workout/predict-calories` endpoint checks for `gender`, `age`, `weight`, and `height` — different fields from those required for the workout plan (`fitness_level`, `goal`, `workout_frequency`). A user could have a workout plan but still fail the predictor check. The backend returned a generic `"Please complete your profile first"` and the frontend always showed `"Prediction failed. Check your profile is complete."` — neither revealed which fields were actually missing.

**Fix (backend):** The error message now lists the specific missing fields:
```python
missing = [f for f, v in {"gender": ..., "age": ..., "weight": ..., "height": ...}.items() if not v]
raise HTTPException(400, detail=f"Profile incomplete — please set: {', '.join(missing)}")
```

**Fix (frontend):**
- Added `useAuth` import and computed `missingFields` (gender, age, weight, height) before rendering
- If any are absent: a yellow warning banner lists exactly which fields are missing with a direct link to the Profile page; the inputs and Predict button are disabled
- Error handler now uses `e.response?.data?.detail` instead of a hardcoded string
- Prediction result is rounded to a whole number with `Math.round()`

**File:** `backend/app/routes/workout.py`, `frontend/src/pages/WorkoutPlan.jsx`

---

#### Bug Fix 3 — Food Log Had No Weight Input

**Root cause:** Clicking "+" on a search result logged the food at a fixed default serving with no way to specify the actual amount eaten. There was no gram input, no scaled macros, and no feedback on what portion was being logged.

**Fix:** Redesigned the search results section in `CalorieTracker.jsx`:
- Each result shows an inline gram input pre-filled with `serving_weight_grams` from Nutritionix (or 100g as fallback)
- All nutrients (calories, protein, carbs, fat) update **live** as the weight changes, scaled proportionally by `grams / serving_weight_grams`
- A per-100g calorie reference is shown below each result for a quick sanity check
- Logged food name includes the weight: `"Chicken Breast (150g)"`
- Added `getScaled(food, grams)` helper and `quantities` state (`{ [resultIndex]: grams }`) to track each result's input independently

**File:** `frontend/src/pages/CalorieTracker.jsx`

---

#### Feature — PWA Support

Added Progressive Web App capability so the app can be installed directly from a mobile browser.

**Changes:**
- Installed `vite-plugin-pwa` as a dev dependency
- Added `VitePWA()` to `vite.config.js` with:
  - Web app manifest (name, short name, description, theme colour `#111118`, background `#0f0f0f`, standalone display, portrait orientation)
  - Workbox service worker in `generateSW` mode — precaches all JS/CSS/HTML/SVG assets
  - `NetworkFirst` runtime cache for API responses (10-minute TTL, 50 entries max)
- App is now installable: Chrome Android → browser menu → "Add to Home Screen"; Safari iOS → Share → "Add to Home Screen"

**File:** `frontend/vite.config.js`, `frontend/package.json`

---

#### Feature — Responsive Mobile Layout

The app was desktop-only with a fixed 256px sidebar and hardcoded multi-column grids. All pages have been made fully responsive.

**Layout changes (`Layout.jsx`):**
- Desktop (`md` and above): sidebar remains as-is
- Mobile (below `md`): sidebar is hidden; a fixed **bottom navigation bar** is shown instead (icons + labels for all nav items, logout button)
- Main content area: `ml-0 md:ml-64` margin, `pb-24 md:pb-8` padding to clear the bottom nav bar

**Grid changes (all page files):**

| Page | Change |
|------|--------|
| `Dashboard.jsx` | Stats: `grid-cols-4` → `grid-cols-2 md:grid-cols-4`; charts: `grid-cols-3` → `grid-cols-1 md:grid-cols-3`; nutrition plan: `grid-cols-4` → `grid-cols-2 md:grid-cols-4` |
| `WorkoutPlan.jsx` | Summary: kept `grid-cols-3`; predictor: `grid-cols-3` → `grid-cols-1 md:grid-cols-3`; log form: `grid-cols-4` → `grid-cols-2 md:grid-cols-4` |
| `Profile.jsx` | Personal info: `grid-cols-2` → `grid-cols-1 md:grid-cols-2`; fitness settings: same; nutrition summary: `grid-cols-4` → `grid-cols-2 md:grid-cols-4` |
| `CalorieTracker.jsx` | Macro bars: `grid-cols-3` → `grid-cols-1 sm:grid-cols-3` |
| `AdminPanel.jsx` | Stats: `grid-cols-5` → `grid-cols-2 md:grid-cols-5` |

**File:** `frontend/src/components/Layout.jsx` and all page files

---

#### Feature — Live Accelerometer Step Counter

The Step Tracker previously had only a manual number input. A live step counter using the device's motion sensor has been added.

**How it works:**
- A `useStepCounter` hook listens to `DeviceMotionEvent`
- On each event, the acceleration magnitude is computed: `√(x² + y² + z²)`
- A step is registered when the magnitude exceeds `STEP_THRESHOLD` (13 m/s²) and at least `MIN_STEP_INTERVAL` (280ms) has elapsed since the last step — preventing double-counting a single footfall
- iOS 13+: `DeviceMotionEvent.requestPermission()` is called on user gesture; if denied, a toast is shown
- Desktops and unsupported browsers: the counter UI is hidden automatically (`'DeviceMotionEvent' in window` check)

**UI:**
- "Start" button begins the session and shows a pulsing live counter
- "Stop" button ends the session and pre-fills the manual save input with the counted steps
- User taps "Update Steps" to save to the database — allowing review/edit before committing
- Manual entry remains available as a fallback at all times

**File:** `frontend/src/pages/StepTracker.jsx`

---

### v1.0.1 — 2026-05-24

#### Fix 1 — `security.py`: passlib incompatible with bcrypt ≥ 4.0 → 500 on login/register

**Root cause:** `passlib 1.7.4` internally calls `bcrypt.hashpw()` with a >72-byte test password during backend initialisation (`detect_wrap_bug`). bcrypt 4.0+ rejects passwords over 72 bytes with a hard `ValueError`, crashing every call to `get_password_hash()` and `verify_password()`.

**Symptom:** Every `POST /auth/login` and `POST /auth/register` returned **500 Internal Server Error**.

**Fix:** Replaced passlib with **direct `bcrypt` calls**. The hash format (`$2b$...`) is identical so existing stored passwords remain valid.

```python
# Before (broken with bcrypt ≥ 4.0)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# After
import bcrypt as _bcrypt
def verify_password(plain, hashed):
    return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
def get_password_hash(password):
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
```

**File:** `backend/app/core/security.py`

---

#### Fix 2 — `auth.py`: JWT `sub` claim stored as integer → all authenticated endpoints 401

**Root cause:** `python-jose 3.5` enforces RFC 7519 — the `sub` (subject) claim must be a **string**. The code was passing `user.id` (Python `int`) directly. The token encoded without error, but every `jwt.decode()` call threw `JWTError: Subject must be a string`, causing `decode_token()` to return `None` and every protected endpoint to return **401 Invalid token**.

**Symptom:** Login returned 200, but all subsequent dashboard/profile/steps calls returned **401 Invalid token** — user appeared to log in but was immediately bounced back.

**Fix:** Cast `sub` to string on creation; cast back to `int` on decode.

```python
# Before
token = create_access_token({"sub": user.id})           # int → broken decode
user  = db.query(User).filter(User.id == payload["sub"]) # string comparison

# After
token = create_access_token({"sub": str(user.id)})       # string ✓
user  = db.query(User).filter(User.id == int(payload["sub"])) # int comparison ✓
```

**File:** `backend/app/routes/auth.py`

---

#### Fix 3 — `axios.js`: 401 interceptor fired on failed login → silent page reload

**Root cause:** The global axios response interceptor called `window.location.href = '/login'` on every 401, including the login request itself. When a user typed wrong credentials, the backend returned 401, the interceptor triggered a full page reload before `toast.error()` could render, and the user saw no error message.

**Symptom:** Entering wrong credentials caused a silent page refresh with no feedback.

**Fix:** Skip the interceptor for `/auth/*` endpoints.

```js
// Before
if (error.response?.status === 401) { ... }

// After
const isAuthEndpoint = error.config?.url?.startsWith('/auth/');
if (error.response?.status === 401 && !isAuthEndpoint) { ... }
```

**File:** `frontend/src/api/axios.js`

---

#### Fix 4 — `start-backend.bat`: server launched with system Python instead of venv

**Root cause:** The bat file used the bare `python` command, which resolved to the system Python. The system Python had `bcrypt 5.0.0` (incompatible with passlib) and different package versions than the project venv.

**Fix:** Always invoke the venv Python explicitly.

```bat
# Before
python -m uvicorn app.main:app --reload ...

# After
venv\Scripts\python.exe -m uvicorn app.main:app --reload ...
```

---

#### Enhancement — Bat file improvements

| File | Change |
|------|--------|
| `start-backend.bat` | Added venv existence guard with setup instructions; shows API URLs on start |
| `start-frontend.bat` | Added Node.js check; auto-runs `npm install` if `node_modules` is missing |
| `start-all.bat` | **New** — launches backend + frontend each in a separate terminal window with a 2-second stagger |

---

## 12. Troubleshooting

### Login returns 500 Internal Server Error

**Cause:** The server is running with the system Python instead of the venv Python, causing a passlib/bcrypt version conflict.

**Fix:** Stop the server and restart using the bat file or with the explicit venv path:
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Never use the bare `python` command to start the server.

---

### All authenticated endpoints return 401 after a successful login

**Cause:** The running server has old code where `create_access_token` stores `user.id` as an integer in the JWT `sub` claim. `python-jose 3.5` rejects this on decode.

**Fix:** Ensure `backend/app/routes/auth.py` uses `str(user.id)` and `int(payload["sub"])` (already patched in v1.0.1), then restart the server so the new code is loaded.

---

### "Invalid credentials" error shows as a silent page refresh

**Cause:** Old axios interceptor triggered `window.location.href = '/login'` on any 401, including the login call itself.

**Fix:** Ensure `frontend/src/api/axios.js` skips the interceptor for `/auth/*` endpoints (already patched in v1.0.1).

---

### `node_modules` not found / frontend won't start

`start-frontend.bat` now auto-runs `npm install` when `node_modules` is missing. Alternatively run manually:
```bash
cd frontend
npm install
npm run dev
```

---

### Port 8000 already in use

Find and kill the process occupying the port:
```powershell
# PowerShell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
Then restart `start-backend.bat`.

---

---

## 13. Technology Stack

### Frontend

| Technology | Version | Role |
|---|---|---|
| React | 19.2.6 | UI component framework |
| Vite | 8.0.12 | Dev server, HMR, bundler |
| TailwindCSS | 4.3.0 | Utility-first CSS with CSS custom property theming |
| React Router DOM | 7.15.1 | Client-side SPA routing |
| Axios | 1.16.1 | HTTP client with interceptors |
| Recharts | 3.8.1 | Area, Bar, Pie, and Line charts |
| Lucide React | 1.16.0 | SVG icon library |
| React Hot Toast | 2.6.0 | Toast notifications |
| React Context API | built-in | Auth + Theme state management (no Redux) |

### Backend

| Technology | Version | Role |
|---|---|---|
| Python | 3.10+ | Runtime |
| FastAPI | latest | REST API framework, auto OpenAPI docs |
| Uvicorn | latest | ASGI server (with `--reload`) |
| SQLAlchemy | latest | ORM — models, sessions, indexes |
| SQLite | built-in | File-based relational database (`getfit.db`) |
| python-jose | latest | JWT encode/decode (HS256) |
| bcrypt | 4.0.1 | Password hashing (pinned — see §11 Fix 1) |
| pydantic-settings | latest | `.env` configuration with type validation |
| slowapi | latest | Rate limiting middleware for FastAPI |
| requests | latest | Outbound HTTP (USDA / Nutritionix API) |
| pytest | latest | Test runner |
| httpx | latest | Async HTTP client used by FastAPI TestClient |

### Machine Learning

| Technology | Version | Role |
|---|---|---|
| scikit-learn | latest | Lasso Regression pipeline (StandardScaler → PolynomialFeatures → Lasso) |
| NumPy | latest | Array operations for model inference |
| pandas | latest | Data loading and preprocessing |
| joblib | latest | Model serialization (`.pkl`) |
| scipy | latest | Statistical utilities in EDA notebook |

---

## 14. Role System & Permissions

GetFit uses three roles. `is_super_admin = true` always implies `is_admin = true`.

```
              Super-Admin
             /           \
          Admin          Admin
           │               │
          User            User
```

| Permission | User | Admin | Super-Admin |
|---|:---:|:---:|:---:|
| Register / Login | ✓ | ✓ | ✓ |
| View & edit own profile | ✓ | ✓ | ✓ |
| Log workouts / nutrition / steps | ✓ | ✓ | ✓ |
| Get personalised workout plan | ✓ | ✓ | ✓ |
| Get personalised nutrition plan | ✓ | ✓ | ✓ |
| Predict calories burned (ML) | ✓ | ✓ | ✓ |
| View all users list | ✗ | ✓ | ✓ |
| View any user's details | ✗ | ✓ | ✓ |
| Toggle user active / inactive | ✗ | ✓ | ✓ |
| Delete regular users | ✗ | ✓ | ✓ |
| View platform statistics | ✗ | ✓ | ✓ |
| Delete admin accounts | ✗ | ✗ | ✓ |
| Promote user → admin | ✗ | ✗ | ✓ |
| Demote admin → user | ✗ | ✗ | ✓ |
| Promote user → super-admin | ✗ | ✗ | ✓ |
| Demote super-admin → admin | ✗ | ✗ | ✓ |

**Server-side guard rules:**
- A super-admin **cannot** be deactivated or deleted by anyone.
- An admin **cannot** delete another admin — only a super-admin can.
- A super-admin **cannot** demote themselves.

**Client-side guard rules:**
- `/admin` route is wrapped in `<AdminRoute>` — non-admins are redirected to `/dashboard`.
- The Admin Panel nav link is hidden unless `user.is_admin === true`.
- Action buttons in the user table are hidden for the currently logged-in admin's own row.

---

## 15. API Request & Response Examples

### `POST /auth/register`

**Request:**
```json
{
  "email": "jane@example.com",
  "username": "jane_smith",
  "password": "Secret@123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 3,
    "email": "jane@example.com",
    "username": "jane_smith",
    "is_admin": false,
    "is_super_admin": false
  }
}
```

---

### `POST /auth/login`

**Request** (`application/x-www-form-urlencoded`):
```
username=jane_smith&password=Secret@123
```
> `username` field also accepts an email address.

**Response `200`:** same shape as `/auth/register`.

**Error `401`:** `{ "detail": "Invalid credentials" }`  
**Error `403`:** `{ "detail": "Account is deactivated" }`

---

### `GET /auth/me`

**Response `200`:**
```json
{
  "id": 3,
  "email": "jane@example.com",
  "username": "jane_smith",
  "is_admin": false,
  "is_super_admin": false,
  "age": 27,
  "gender": "female",
  "weight": 62.0,
  "height": 165.0,
  "fitness_level": "intermediate",
  "goal": "fat_loss",
  "activity_level": "moderate",
  "workout_frequency": 4,
  "equipment": "dumbbells"
}
```

---

### `PUT /profile/`

**Request** (all fields optional — send only what changed):
```json
{
  "age": 27,
  "gender": "female",
  "weight": 62.0,
  "height": 165.0,
  "fitness_level": "intermediate",
  "goal": "fat_loss",
  "activity_level": "moderate",
  "workout_frequency": 4,
  "equipment": "dumbbells"
}
```

**Response `200`:**
```json
{
  "message": "Profile updated",
  "user": { "id": 3, "username": "jane_smith", "age": 27, "weight": 62.0, "..." : "..." }
}
```

---

### `GET /profile/nutrition-plan`

**Response `200`:**
```json
{
  "bmr": 1454.0,
  "tdee": 2254.0,
  "calorie_goal": 1754.0,
  "goal": "fat_loss",
  "activity_level": "moderate",
  "macros": {
    "calories": 1754.0,
    "protein_g": 111.6,
    "fat_g": 50.9,
    "carbs_g": 200.2,
    "protein_pct": 25.5,
    "fat_pct": 26.1,
    "carbs_pct": 45.7
  }
}
```

**Error `400`:** `{ "detail": "Please complete your profile first" }`

---

### `POST /workout/predict-calories`

**Request:**
```json
{
  "duration_minutes": 45.0,
  "heart_rate": 148.0,
  "body_temp": 37.5
}
```

**Validation bounds:** `duration_minutes` 1–600, `heart_rate` 30–250, `body_temp` 35.0–43.0.

**Response `200`:**
```json
{
  "predicted_calories_burned": 334.17,
  "confidence_low": 333.57,
  "confidence_high": 334.77
}
```

The `confidence_low` / `confidence_high` fields represent a ±2σ interval around the point estimate, based on the model's RMSE of 0.30 cal.

---

### `POST /workout/log`

**Request:**
```json
{
  "exercise_name": "Running",
  "duration_minutes": 30.0,
  "heart_rate": 155.0,
  "calories_burned": 290.0,
  "notes": "5K in 28 min"
}
```

**Response `200`:** `{ "message": "Workout logged", "id": 12 }`

---

### `POST /nutrition/log`

**Request:**
```json
{
  "food_name": "Grilled chicken breast",
  "calories": 165.0,
  "protein": 31.0,
  "carbs": 0.0,
  "fat": 3.6,
  "meal_type": "lunch"
}
```

**Response `200`:** `{ "message": "Food logged", "id": 7 }`

---

### `GET /nutrition/logs/today`

**Response `200`:**
```json
{
  "logs": [
    {
      "id": 7,
      "food_name": "Grilled chicken breast",
      "calories": 165.0,
      "protein": 31.0,
      "carbs": 0.0,
      "fat": 3.6,
      "meal_type": "lunch",
      "logged_at": "2026-05-25T12:34:00"
    }
  ],
  "totals": {
    "calories": 165.0,
    "protein": 31.0,
    "carbs": 0.0,
    "fat": 3.6
  }
}
```

---

### `POST /steps/log`

**Request:**
```json
{
  "steps": 9200,
  "date": "2026-05-25"
}
```

**Response `200`:**
```json
{
  "message": "Steps logged",
  "calories_from_steps": 265.6
}
```

---

### `DELETE /workout/log/{id}`

**Response `200`:** `{ "message": "Workout log deleted" }`  
**Error `404`:** `{ "detail": "Workout log not found" }` (also returned if the log belongs to a different user)

---

### `GET /workout/logs?skip=0&limit=20`

**Response `200`:** Array of workout log objects, ordered most-recent first.

```json
[
  {
    "id": 12,
    "exercise_name": "Running",
    "duration_minutes": 30.0,
    "sets": null,
    "reps": null,
    "heart_rate": 155.0,
    "calories_burned": 290.0,
    "notes": "5K in 28 min",
    "logged_at": "2026-06-21T09:15:00"
  }
]
```

---

### `GET /admin/stats`

**Response `200`:**
```json
{
  "total_users": 8,
  "active_users": 8,
  "admin_users": 3,
  "super_admin_users": 1,
  "total_calorie_logs": 42,
  "total_workout_logs": 17,
  "total_step_logs": 24
}
```

---

---

## 16. Testing

### Running the Test Suite

```bash
cd backend
venv\Scripts\python.exe -m pytest tests/ -v
```

All 50 tests run against an in-memory SQLite database — no backend server needed.

### Test Architecture

`tests/conftest.py` sets up the test environment:

1. Sets `DATABASE_URL=sqlite://` and `SECRET_KEY` via `os.environ` before any app import
2. Replaces `app.core.database.engine` with a `StaticPool` engine — all connections share one in-memory SQLite database, so tables created by `main.py` on import are visible to test sessions
3. Provides a `client` fixture that overrides FastAPI's `get_db` dependency and wraps the app in `TestClient`

### Test Files

| File | Tests | What's covered |
|---|---|---|
| `test_auth.py` | 9 | Register success, duplicate email/username, login by email and username, wrong password, `/auth/me` with and without token |
| `test_nutrition_calculator.py` | 16 | BMR formula (male/female), TDEE multipliers, calorie goal adjustments, macro splits, step calorie formula, full plan structure |
| `test_calorie_predictor.py` | 8 | Model loads, returns positive float, confidence range shape, monotonicity (longer duration → more calories, higher HR → more calories), gender case-insensitivity, minimum clamp at 1.0 |
| `test_workout_recommender.py` | 10 | Correct day count, non-empty exercises, required keys (name/sets/reps), all fitness levels, all goals, determinism per user/week, full-body split for ≤3 days, upper/lower split for 4 days |

### Adding New Tests

Follow the existing pattern — import the function under test directly; use the `client` fixture for HTTP endpoint tests:

```python
# Unit test (no HTTP)
from app.services.nutrition_calculator import calculate_bmr

def test_male_bmr():
    assert abs(calculate_bmr("male", 70, 175, 30) - 1648.75) < 0.01

# Endpoint test
def test_register_success(client):
    res = client.post("/auth/register", json={
        "email": "test@example.com", "username": "testuser", "password": "pass"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
```

---

*Documentation last updated: 2026-06-21 — GetFit v1.2.0*
