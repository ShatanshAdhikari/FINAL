# GetFit — Judge's Evaluation & Demo Briefing

> A complete, code-verified evaluation of the GetFit fitness & nutrition platform.
> Every claim below was checked against the actual source, not just the docs.
> Stack: React (Vite) · FastAPI · SQLite · scikit-learn · Docker

**Contents**
1. [One-line verdict](#1-one-line-verdict)
2. [What GetFit is](#2-what-getfit-is-the-demo-elevator-pitch)
3. [System architecture](#3-system-architecture)
4. [End-to-end request lifecycle](#4-the-end-to-end-request-lifecycle)
5. [Backend deep dive](#5-backend-deep-dive)
6. [Frontend deep dive](#6-frontend-deep-dive)
7. [ML & notebooks deep dive](#7-ml--notebooks-deep-dive)
8. [Testing & DevOps](#8-testing--devops)
9. [Discrepancies a sharp judge will catch](#9-discrepancies-a-sharp-judge-will-catch)
10. [Live demo script](#10-suggested-live-demo-script)
11. [Grading rubric](#11-grading-rubric)
12. [Judge Q&A prep](#12-judge-qa-prep)

---

## 1. One-line verdict

> A genuinely full-stack, ML-integrated fitness app with real role-based access control, real security hardening, a real 15,000-row ML pipeline, tests, and Docker. It is well above a typical student CRUD project. Its weak points are **documentation inconsistencies** (three different food-API names, a "synthetic data" claim that's no longer true, a "Redux" claim that's false) and a handful of **known-but-unfixed code-quality items** the team has honestly logged themselves.

**Grade: A− / ≈88%.** The engineering is strong; the polish gap is almost entirely in the docs contradicting the (better) reality of the code.

---

## 2. What GetFit is (the demo elevator pitch)

GetFit replaces the "juggle a calorie site + a workout video + a phone step counter" problem with **one personalised platform**. A user enters age/weight/height/goal, and the app produces three personalised outputs from three *different* techniques:

| # | Output | Technique | Type |
|---|--------|-----------|------|
| 1 | Daily calorie + macro target | **Mifflin-St Jeor** equation | Scientific formula |
| 2 | Weekly workout plan | **Rule-based recommender** (50+ exercise DB) | Expert-system logic |
| 3 | Calories burned per session | **Lasso Regression** (poly degree 3) | Machine learning |

That "three distinct methods for three problems" is the strongest single talking point — it shows the team picked the *right tool per problem* rather than forcing ML everywhere.

---

## 3. System architecture

```
┌─────────────────────── BROWSER ───────────────────────┐
│  React SPA (Vite, :5173)                               │
│  Pages: Login/Register · Onboarding · Dashboard ·      │
│         WorkoutPlan · CalorieTracker · StepTracker ·   │
│         Profile · AdminPanel                           │
│  Cross-cutting: AuthContext (JWT) · ThemeContext ·     │
│                 axios (interceptors) · ErrorBoundary   │
└───────────────┬────────────────────────────────────────┘
                │  /api/*  → Vite proxy strips /api
                │  REST + JSON · Authorization: Bearer <JWT>
                ▼
┌─────────────────── FASTAPI BACKEND (:8000) ───────────┐
│  Routes: /auth /profile /workout /nutrition /steps /admin
│                                                        │
│  Services (business logic)      ML                Core │
│  • nutrition_calculator         • calorie_        • JWT (HS256)
│    (Mifflin-St Jeor)              predictor.py    • bcrypt
│  • workout_recommender          • calorie_        • config/settings
│    (rule-based)                   model.pkl       • rate limiter
│                                                        │
│  Models (SQLAlchemy): User · CalorieLog ·              │
│                       WorkoutLog · StepLog · WeightLog │
└───────────────┬───────────────────────────┬───────────┘
                │ SQLAlchemy ORM             │ outbound HTTP
                ▼                            ▼
        ┌──────────────┐          ┌────────────────────────┐
        │ SQLite        │          │ USDA FoodData Central  │
        │ getfit.db     │          │ (or Nutritionix if     │
        └──────────────┘          │  keys are set)         │
                                   └────────────────────────┘
```

**Decoupling note:** frontend and backend are fully separate; the browser talks REST. In dev, Vite proxies `/api/*` → `http://localhost:8000` (with `/api` stripped), which sidesteps CORS entirely. This is a clean, production-shaped separation.

---

## 4. The end-to-end request lifecycle

```
1. Login: POST /auth/login (form-encoded username|email + password)
   → backend bcrypt.checkpw() → checks is_active → returns JWT + user
2. Frontend stores token+user in localStorage, sets AuthContext
3. Every later call: axios attaches  Authorization: Bearer <JWT>
4. Backend get_current_user() dependency:
      jwt.decode() → sub (string) → int(sub) → DB lookup
      → if not is_active: 403
5. On ANY 401 (except /auth/*): axios interceptor wipes storage → /login
```

Three subtle-but-important design decisions live in this flow, and each was a *bug that got fixed* (great story material):

| Decision | Why it matters | What broke without it |
|---|---|---|
| JWT `sub` is `str(user.id)`, decoded back to `int` | RFC 7519 / python-jose 3.5 requires string subject | Every authenticated call returned 401 after a "successful" login |
| bcrypt called **directly**, not via passlib | passlib 1.7.x crashes on bcrypt ≥4.0 | 500 error on *every* login/register |
| 401 interceptor **skips** `/auth/*` | Wrong password shouldn't trigger a full-page reload | Silent page refresh with no error toast |

If asked "tell me about a hard bug," the JWT-subject one is the best answer: subtle, RFC-driven, symptom (login works then instantly bounces) didn't obviously point at the cause.

---

## 5. Backend deep dive

### 5.1 The three "brains"

**(A) Nutrition Calculator** — `services/nutrition_calculator.py`
```
BMR (Mifflin-St Jeor):
  Male:   10·wt + 6.25·ht − 5·age + 5
  Female: 10·wt + 6.25·ht − 5·age − 161
TDEE = BMR × {sedentary 1.2 … very_active 1.9}
Goal: fat_loss −500 · muscle_gain +300 · endurance +150 · strength ±0
Steps→cal = steps × 0.05 × (weight/70)
```
Protein target scales by *both* fitness level and goal (1.4–2.4 g/kg); remaining calories split fat/carb by goal. Dietitian-grade logic, not a made-up number.

**(B) Workout Recommender** — `services/workout_recommender.py`
```
≤3 days → Full Body     4 days → Upper/Lower     5–7 days → Push/Pull/Legs (+Core/Cardio at 7)
Sets/reps/rest tuned per goal (fat loss 12–20 reps/short rest … strength 1–8 reps/long rest)
```
> ⚠️ **Honest flag (self-logged as CODE-07):** `random.seed(42)` means every user with the same frequency gets an identical plan. Deterministic *by design* for demos, but removes variety. If asked "does everyone get the same plan?" — yes, currently, and the team already knows.

**(C) ML Calorie Predictor** — `ml/calorie_predictor.py` — **the crown jewel, and it's real.** See §7.

### 5.2 Security posture — genuinely strong

| Control | Status | Evidence |
|---|---|---|
| No hardcoded secret | ✅ | `config.py` refuses to boot on empty `SECRET_KEY` (validator raises) |
| Passwords hashed | ✅ | bcrypt direct, `$2b$` format |
| Deactivated users locked out | ✅ | `is_active` check in shared `get_current_user()` — one line covers all routes |
| Brute-force protection | ✅ | slowapi, 10/min per IP on login+register → 429 |
| Email validation | ✅ | `EmailStr` on registration |
| Input bounds | ✅ | Pydantic `Field(ge/le)` — age 10–120, HR 30–250, etc. → 422 |
| Enum validation | ✅ | `Literal[...]` on goal/gender/etc. (BUG-04 fix) |
| `.env` out of git | ✅ | removed from tracking, key rotated (SEC-01) |

A real security narrative: **3 security fixes + rate limiting + input hardening**, all documented with root cause.

### 5.3 Data model

`User (1) ──< CalorieLog / WorkoutLog / StepLog / WeightLog`. All log tables are indexed on `user_id` + timestamp. Ownership is enforced on every read/delete (`filter(user_id == current_user.id)`), so users can't touch each other's logs. There's even a **live startup migration** in `main.py` (`PRAGMA table_info` → `ALTER TABLE ADD COLUMN`) that adds `sets`/`reps` to existing DBs without data loss — production-minded.

### 5.4 Role system (RBAC — a real-world pattern)

Three roles, enforced **server-side** (not just hidden in UI):
- **User** → own data only
- **Admin** → list/view/delete users, toggle active, stats
- **Super-Admin** → everything + promote/demote roles

Guard rules worth quoting: a super-admin **cannot** be deleted/deactivated by anyone, an admin **cannot** delete another admin, and a super-admin **cannot** demote themselves. Thoughtful privilege-escalation defense.

---

## 6. Frontend deep dive

### 6.1 Routing & guards
```
PublicRoute   → /login /register     (bounces to /dashboard if logged in)
ProtectedRoute→ /dashboard /workout /calories /steps /profile /onboarding
AdminRoute    → /admin               (requires is_admin)
```

### 6.2 Resilience features (these separate it from a toy app)
| Feature | File | Why it matters |
|---|---|---|
| **ErrorBoundary** wraps every protected route | `ErrorBoundary.jsx` | A render crash shows a "Try again" card, not a white screen |
| **Loading skeletons** | `Skeleton.jsx` | Shaped placeholders instead of "Loading…" text |
| **Safe JSON.parse** of localStorage | `AuthContext.jsx` | Corrupted storage no longer white-screens the app (BUG-01) |
| **Smart 401 handling** | `axios.js` | Auto-logout on expiry, but not on wrong-password |
| **Dark/Light theme** | `ThemeContext.jsx` + CSS vars | Applied to `<html>` *before* React renders → no flash |
| **PWA + responsive + accelerometer** | vite config, Layout, StepTracker | Installable; mobile bottom-nav; live step counting via `DeviceMotionEvent` (√(x²+y²+z²) peak detection, 13 m/s² threshold, 280 ms debounce) |

The **live accelerometer step counter** is the best *frontend* demo moment — open on a phone, tap Start, walk, watch it count.

### 6.3 State management
**React Context API only** (AuthContext + ThemeContext) — no Redux. Appropriate for this scope. ⚠️ *(See discrepancy D-1 — one doc wrongly says Redux.)*

---

## 7. ML & notebooks deep dive

### 7.1 The dataset (what it *actually* is)

| Property | Value | Source of truth |
|---|---|---|
| File used for training | `backend/app/ml/data/calories.csv` | verified header |
| Rows | **15,000** (15,001 incl. header) | `wc -l` |
| Columns | `User_ID, Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp, Calories` | verified header |
| Origin | Kaggle — "Calories Burnt Prediction" (~15k-row exercise dataset) | notebook + FINDINGS |
| `exercise_dataset.csv` (249 rows) | **NOT used** — unrelated "activity → cal/hour by bodyweight" lookup table | `calorie_model_eda.md` |

**Critical detail most people miss:** `calories.csv` is **already a fully-merged file** — all 7 features *plus* the target in one file. So although `calorie_predictor.py` advertises a two-file merge (`exercise.csv` + `calories.csv` on `User_ID`), that path never runs. The loader's `_is_merged()` check detects `calories.csv` has every required column and loads it directly. **The model trains on the real 15,000 rows.** The synthetic 1,000-row generator is a *fallback only*, triggered when no CSV is present.

**The gender-encoding + column-alias system** is genuinely robust: `_COL_ALIASES` maps `Sex`/`sex`/`Gender` → `Gender`, `Heart Rate`/`HeartRate` → `Heart_Rate`, etc., so the same code ingests almost any upload variant. The notebook mirrors these exact aliases — notebook and production stay in sync.

### 7.2 Model architecture — and *why* each piece

```
raw 7 features
   │
   ▼
StandardScaler          ── zero-mean/unit-variance; required for L1 fairness
   │
   ▼
PolynomialFeatures      ── degree=3, include_bias=False
(7 → 119 terms)            expands to squares, cubes & interactions
   │                       (Duration×Heart_Rate, Gender×Weight×Duration, …)
   ▼
Lasso(alpha=0.01,        ── L1 penalty drives weak terms to exactly 0
      max_iter=10000)       → automatic feature selection
   │
   ▼
Calories (continuous)
```

| Choice | Why it's the *right* choice |
|---|---|
| **Polynomial degree 3** | Calorie burn is non-linear & interactive — long AND high-HR workouts compound. Degree 3 captures 3-way interactions like `Gender×Weight×Duration`. |
| **Lasso (L1)** | Degree-3 expansion → 119 features → huge overfitting risk. Lasso zeros **64% of them** (only 43 survive), giving a sparse, interpretable model. |
| **StandardScaler first** | Lasso's penalty is scale-sensitive; scaling makes the penalty fair across Height (~175) vs Gender (0/1). |
| **alpha=0.01** | Small penalty — enough to prune noise without underfitting a near-deterministic target. |

### 7.3 Training & serving lifecycle

```
FIRST REQUEST ─► get_model() ─► load_model()
                                   │
                     model.pkl exists? ──yes──► joblib.load()  (fast)
                                   │no
                                   ▼
                              train_model()
                                   │
                     real_data_available()? ──yes──► _load_real_data() (15k rows)
                                   │no
                                   ▼
                        _generate_synthetic_data() + UserWarning
                                   │
                            fit → joblib.dump(model.pkl)

SERVING: POST /workout/predict-calories
   → predict_calories(gender,age,height,weight,duration,hr,body_temp)
   → point = max(raw, 1.0)          (clamp — never return ≤0 cal)
   → band  = point ± 2·RMSE  (RMSE=0.30 → ±0.60 cal)
   → route maps: calories→predicted_calories_burned, low→confidence_low, high→confidence_high
```

Engineering touches worth crediting:
- **Lazy singleton** (`_model` global) — model loads once per process, not per request.
- **Min-clamp at 1.0 cal** — guards against tiny/negative predictions at extreme inputs (dedicated test exists).
- **MLOps admin endpoints** (not in the summary docs!):
  - `POST /admin/ml/retrain` — admin-only, forces a full retrain after uploading new CSV data.
  - `GET /admin/ml/status` — reports `using_real_data: true/false`, so an admin can *verify at runtime* whether the deployed model is on real or synthetic data.

### 7.4 The EDA notebook — section by section

`calorie_model_eda.ipynb` is a proper 5-part analysis:

| § | Title | Techniques used | Key result |
|---|---|---|---|
| **A** | Data loading & overview | alias-rename, gender encode, `.describe()`, missing/dupe check | 15k rows, **0 missing, 0 duplicate User_IDs** |
| **B** | EDA | histograms+KDE, boxplots, countplots, **correlation heatmap**, scatter (gender-colored), **IQR outlier detection** | Duration r=**0.955**, HR r=**0.898**, Body_Temp r=**0.825** dominate; Weight/Gender/Height ≈ 0 |
| **C** | Regression eval | stratified `train_test_split`, `r2/MAE/RMSE`, **5-fold `cross_val_score`**, predicted-vs-actual, residual plot, **Shapiro-Wilk + Q-Q plot** | R²=**0.99998**, MAE=**0.26**, RMSE=**0.30**; CV R²=0.99998 ± 1e-6 |
| **D** | Classification-style metrics | bin calories into Low/Med/High, `classification_report`, **confusion matrix**, false-positive counting | F1 **0.99–1.00**; only **17/3000 misclassifications**, all adjacent-class, **0 High false positives** |
| **E** | Feature importance | `PolynomialFeatures.get_feature_names_out()` × `Lasso.coef_`, rank by abs value | **43/119** non-zero; Duration (41.6) ≫ Heart_Rate (18.9) > Duration×HR (10.2); **Height fully eliminated** |

The clever bit in **§D**: Lasso is a *regression* model, but the team **binned** the continuous output into Low/Medium/High to also report F1/precision/recall/confusion-matrix — the classification vocabulary a rubric often expects.

### 7.5 Honest critical analysis (be ready — a knowledgeable judge WILL probe this)

**(a) The R²≈0.99998 is "too perfect" — and there's a real reason.**
A near-perfect fit almost always means the target is *near-deterministic* from the features. Two independent signals confirm the data is the cause, not a mistake:
- **Body_Temp mean = 40.03 °C** (min 37.1, max 41.5) — a *feverish* range no clinical population sustains → a strong tell that this Kaggle dataset was **synthetically generated from a physiological formula**, not measured on real people.
- The **5-fold CV** (which cleanly re-fits per fold) *also* returns 0.99998 — the perfection generalizes; it's not overfitting.

**Framing to say out loud:** *"The model faithfully learned the relationship, and cross-validation proves it generalizes. But the dataset's calorie target is near-deterministic — likely synthetically generated — so this demonstrates a correct, well-regularized ML pipeline rather than conquering a genuinely noisy prediction problem."* This reconciles the "synthetic data" claim in the slides (D-2): the *file we train on is real/downloaded*, but the *dataset's origin is synthetic*. Both are true — say both.

**(b) A subtle methodology bug in Section C (hold-out cell).**
`train_model()` fits on **100%** of the 15k rows and saves the `.pkl`. The notebook's §C then does a `train_test_split` and evaluates the **already-fully-trained** model on `X_test` — but those rows were *part of* training. That's **train/test leakage** in the hold-out metric specifically. It doesn't change the headline (the clean 5-fold CV agrees), but if asked "is your test set truly held out?", the honest answer is: *"The 5-fold CV is the trustworthy number; the hold-out cell reuses training rows and should be re-run on a model trained only on the train split."* Owning this shows real ML literacy.

**(c) The ±0.60 cal confidence band is technically trivial.**
RMSE 0.30 → ±2σ band is ±0.60 cal, so "334 kcal (333–335)" looks almost pointless. It's the *right idea* (communicating uncertainty), just applied to a dataset so clean the uncertainty is negligible. Frame it as "the mechanism is correct and would show meaningful width on noisier real-world data."

**(d) The `calorie_model_eda.md` results table is a stub.** Its "Evaluation Results" section still has `—` placeholders even though `FINDINGS.md` has the real numbers. Fix: copy `FINDINGS.md`'s numbers into it.

### 7.6 ML test suite

`tests/test_calorie_predictor.py` covers: model loads, returns positive float, confidence-range shape (`low ≤ calories ≤ high`), **monotonicity** (longer duration → more calories; higher HR → more calories), gender case-insensitivity, and the minimum-clamp at 1.0. Monotonicity tests are a strong signal — they assert the model behaves *physically correctly*, not just that it returns a number.

---

## 8. Testing & DevOps

- **Tests:** pytest suite over auth, nutrition calculator, calorie predictor (incl. monotonicity), and workout recommender. Runs against in-memory SQLite via `StaticPool` — no server needed. *(Doc count drifts between "50 tests" and per-file totals summing to ~43 — verify with `pytest -v` before quoting a number.)*
- **Docker:** one-command `docker compose up --build`; backend seeds demo users on first boot, healthcheck gates the frontend, named volume persists SQLite. Real infra, not a token Dockerfile.

---

## 9. Discrepancies a sharp judge will catch

The **code is correct**; the **docs contradict it** in spots. Best fix: reconcile the docs. At minimum, know the truth.

| ID | Claim in docs | Reality in code | Where |
|---|---|---|---|
| **D-1** | "State Management: **Redux Toolkit**" | It's **React Context** (no Redux anywhere) | `PRESENTATION.md` Slide 5 |
| **D-2** | "ML model uses **synthetic training data**" | Trains on **real 15,000-row** dataset (origin may be synthetic — see §7.5) | `PRESENTATION.md` Slide 3 |
| **D-3** | Food source = **Nutritionix** / **USDA** / **OpenFoodFacts** (all three appear!) | Code = **Nutritionix if keys set, else USDA**. OpenFoodFacts is *not* in the code | DIAGRAMS/PRESENTATION vs DOCUMENTATION vs FIXES |
| **D-4** | `/nutrition/search` Auth = ❌ (public) | Code **requires** a JWT (BUG-05 fixed it) | `DOCUMENTATION.md` §6 table |
| **D-5** | Predictor returns `predicted_calories_burned` / `calories` | Internal fn returns `calories/low/high`; route maps to `predicted_calories_burned/confidence_low/confidence_high` (API boundary is consistent) | §7.1 vs §15 vs code |
| **D-6** | Token expiry default = 60 min | Actual default = **1440 min** (config) | `backend/README.md` |
| **D-7** | CORS uses `FRONTEND_URL` config | `main.py` **hardcodes** localhost origins | self-logged CODE-04 |
| **M-1** | `calorie_model_eda.md` evaluation table = empty placeholders | Real values in `FINDINGS.md` (R²=0.99998, MAE=0.26, RMSE=0.30) | `calorie_model_eda.md` |
| **M-2** | `.md` says Kaggle source "aadhavvignesh"; `data/README.md` says "ruchikakumbhar" | Two different attributions — pick one | notebooks vs data/README |
| **M-3** | `.md` mentions `POST /api/admin/retrain-model` "if wired up" | It **is** wired up as `POST /admin/ml/retrain` | `calorie_model_eda.md` |
| **M-4** | Target range "≈3–200" (notebook) vs "1–314" (FINDINGS) | FINDINGS' min 1 / max 314 is the actual `.describe()` output | notebooks |

**Team's own honestly-logged open items** (`FIXES.md`): unused `loading` state, no onboarding step-validation, lenient `isProfileComplete`, silent `catch{}` blocks, deprecated `datetime.utcnow`/`declarative_base`, **no password-strength check** (empty passwords accepted at register), and seeded-fixed workout plans. Having these written down is a *plus* (self-awareness); expect a judge to ask about the password one.

---

## 10. Suggested live demo script

8–10 minutes, maximum impact:

```
1.  Log in as super-admin (shatansh / SuperAdmin@123)              → show role
2.  Log in as a fresh/regular user → Onboarding wizard            → personalisation
3.  Dashboard: summary cards + charts + theme toggle (dark/light) → polish
4.  Profile → nutrition plan: show BMR/TDEE/macros compute live   → Mifflin-St Jeor
5.  Workout Plan: generate plan → Predict Calories (ML) w/ range  → the ML crown jewel
6.  Calorie Tracker: search food (USDA), gram input, live macros  → external API
7.  Step Tracker (on a phone!): Start → walk → live counter       → accelerometer wow
8.  Log out → log in as admin → Admin Panel: toggle/deactivate,   → RBAC enforced
    show super-admin-only promote/demote buttons                    server-side
9.  Bonus: hit http://localhost:8000/docs → live Swagger          → API quality
```

**Pre-demo checklist:** run `seed_users.py`; start via **venv Python** (not system Python — that's the passlib/bcrypt 500 trap); confirm `.env` has `SECRET_KEY`; if using Docker, consider dropping `jupyter` from `requirements.txt` for a faster build.

**Seeded accounts:**

| Role | Username | Password |
|---|---|---|
| Super-Admin | `shatansh` | `SuperAdmin@123` |
| Admin | `prerana` | `Admin@1234` |
| Users | `maria` `neha` `animesh` `biplov` `binav` | `User@1234` |

---

## 11. Grading rubric

| Dimension | Score | Rationale |
|---|:---:|---|
| Architecture & separation | 9/10 | Clean FE/BE split, proxy, layered backend |
| Backend engineering | 9/10 | Shared-dependency auth, migrations, ownership checks |
| Security | 9/10 | Real RBAC + 3 sec fixes + rate limiting; only gap: password strength |
| ML integration | 8.5/10 | Real data, real EDA, confidence range, `ml/status` self-check; R² almost *too* perfect + one leakage cell |
| Frontend UX & resilience | 9/10 | ErrorBoundary, skeletons, theming, PWA, accelerometer |
| Testing | 7.5/10 | Good coverage of logic (incl. monotonicity); light on endpoint/integration breadth |
| DevOps | 8.5/10 | One-command Docker, healthcheck, volume, seeding |
| Documentation *accuracy* | 6.5/10 | Voluminous and well-formatted, but **11 internal contradictions** |
| **Overall** | **≈88% (A−)** | Strong, demo-ready, honest about its own gaps |

**Highest-value pre-demo action:** spend ~20 minutes reconciling the discrepancies in §9 so the docs match the (superior) code. The biggest risk isn't the software — it's a judge reading "synthetic data" or "Redux" in a slide and catching a contradiction you didn't intend.

---

## 12. Judge Q&A prep

**"Tell me about a hard bug."**
The JWT `sub` claim. python-jose 3.5 enforces RFC 7519 — the subject must be a string. We passed `user.id` as an int; the token *encoded* fine but every decode threw `JWTError`, so login returned 200 then every authenticated call 401'd — the user appeared to log in then instantly bounced. Fix: `str(user.id)` on create, `int(sub)` on decode.

**"Why Lasso and not Linear/Ridge/a neural net?"**
Degree-3 poly expansion makes 119 correlated features — we needed automatic feature selection. Lasso's L1 zeros 64% of them, giving a sparse, interpretable model. A neural net is overkill for 15k rows / 7 features and would sacrifice interpretability for no accuracy gain (already R²≈1).

**"Which feature matters most?"**
Duration, by far (coefficient 41.6), then Heart_Rate (18.9), then their interaction (10.2). Height was *completely eliminated* by Lasso — no independent predictive value once weight is present.

**"Is R²=0.9999 realistic?"**
On this dataset, yes — cross-validation confirms it — because the target is near-deterministic in the features (the dataset appears synthetically generated; note the 40 °C mean body temperature). On noisy real-world data I'd expect lower R² and a wider confidence band.

**"How do you know it's not overfitting?"**
Three ways: L1 regularization prunes 64% of terms; 5-fold CV variance is ±0.000001 (identical across folds); residuals are near-zero-mean (−0.004) and tight (σ=0.30).

**"Is your test set truly held out?"**
The 5-fold CV is the trustworthy number. The notebook's hold-out cell reuses training rows (the `.pkl` was trained on the full set), so that specific metric has leakage and should be re-run on a model trained only on the train split.

**"Can you update the model?"**
Yes — drop a new CSV in `data/`, call `POST /admin/ml/retrain` (admin-only), and check `GET /admin/ml/status` to confirm it's using real data.

**"How is role security enforced?"**
Server-side, via FastAPI dependencies (`require_admin` / `require_super_admin`), not just hidden UI. A super-admin can't be deleted/deactivated by anyone, an admin can't delete another admin, and a super-admin can't demote themselves.

---

*Evaluation compiled 2026-07-07. All claims verified against source, not documentation alone.*
