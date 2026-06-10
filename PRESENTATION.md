# GetFit — PowerPoint Presentation (10 Slides)

---

## Slide 1 — Introduction

**Title:** GetFit — Your Personal Fitness & Nutrition Companion

**Content:**

Getting fit is hard. Most people don't know how many calories they should eat, what workouts suit their body, or how to track their progress without guessing.

GetFit is a web application that takes the guesswork out of fitness. You enter your age, weight, height, and goal — and the app builds a personalised meal plan, workout schedule, and tracks your daily activity all in one place.

Whether you want to lose fat, gain muscle, build strength, or improve endurance — GetFit gives you a plan designed specifically for you.

> **Image reference:** Place a hero screenshot of the GetFit dashboard or a before/after fitness progress graphic here. Alternatively, use the `frontend/src/assets/hero.png` file already in the project.

---

## Slide 2 — The Problem We're Solving

**Title:** Why Does This App Exist?

**Content:**

Most fitness apps are either too generic ("do 30 push-ups a day") or too complicated for everyday users. People are left bouncing between a calorie calculator on one website, a workout video on another, and a step counter on their phone — none of which talk to each other.

GetFit brings all of this into one place:

- **Eat right** — track meals and get a personalised daily calorie & macro target
- **Train smart** — get a weekly workout plan matched to your fitness level and goals
- **Move more** — log daily steps and see how many calories you burned just by walking
- **Stay informed** — see everything on one dashboard

> **Image reference:** A simple split-screen graphic — left side showing a confused person juggling multiple apps, right side showing a clean single dashboard. Or use an icon grid representing food, workouts, steps, and analytics.

---

## Slide 3 — Project Scope & Limitations

**Title:** What GetFit Does (and Doesn't Do)

**Content:**

**In scope — what the app covers:**
- User registration, login, and profile setup
- Personalised calorie and macro targets based on your body and goal
- Meal logging with a real food database (Nutritionix)
- Auto-generated weekly workout plans (adjusted by fitness level and available equipment)
- Step tracking with calorie burn estimation
- A personal history log and dashboard
- Admin tools for managing users

**Out of scope — what we deliberately left out:**
- No mobile app (web-only for now)
- No social features (no friends, sharing, or leaderboards)
- No real-time wearable sync (no Fitbit/Apple Watch integration)
- The calorie burn ML model uses synthetic training data, not a real clinical dataset
- No payment system or premium tiers

> **Image reference:** A two-column table graphic — green checkmarks on the left for "in scope", red crosses on the right for "out of scope". Clean and visual.

---

## Slide 4 — Methodology

**Title:** How We Calculate Everything

**Content:**

We used three different methods depending on what we needed to calculate:

**1. Mifflin-St Jeor Equation (for meal plans)**
This is a well-established scientific formula used by dietitians worldwide to calculate how many calories your body needs per day. We feed it your age, weight, height, and activity level to produce your personal calorie target and protein/carb/fat breakdown.

**2. Rule-Based Workout Recommender (for workout plans)**
We built an exercise database of 50+ exercises across push, pull, legs, core, and cardio categories. The system picks the right exercises and training volume (sets/reps/rest) based on your fitness level and goal — no random guessing, just structured logic that mirrors how real coaches program training.

**3. Lasso Regression with Polynomial Features (for calorie burn)**
When you log a workout, we estimate how many calories you burned using a machine learning model trained on workout data (heart rate, duration, weight, age). We chose Lasso regression because it's accurate for this kind of physical data and avoids overfitting by automatically simplifying the model.

> **Image reference:** A flow diagram with three boxes, one for each method, with a short label and a relevant icon (calculator, checklist, brain/chart). Or a simple "Input → Method → Output" graphic for each of the three.

---

## Slide 5 — Tech Stack

**Title:** What We Built It With

**Content:**

| Layer | Technology | Why we chose it |
|---|---|---|
| **Frontend** | React + Vite | Fast, modern, and widely used for building interactive UIs |
| **Backend** | Python FastAPI | Simple to write, fast to run, automatic API documentation |
| **Database** | SQLAlchemy ORM | Clean database access without writing raw SQL |
| **ML Library** | scikit-learn | Industry-standard Python library for machine learning |
| **Food Data** | Nutritionix API | Real-world food database with calorie and macro info |
| **State Management** | Redux Toolkit | Manages logged-in user state cleanly across pages |
| **Styling** | CSS + Recharts | Custom styles and interactive data charts |

The frontend and backend are completely separate — the browser talks to the backend using a REST API. This makes the app easy to scale and maintain.

> **Image reference:** A tech stack diagram with logos/icons for React, Python, FastAPI, SQLite/PostgreSQL, scikit-learn, and Nutritionix arranged in layers (Frontend → Backend → Database → External).

---

## Slide 6 — Gantt Chart

**Title:** Project Timeline

**Content:**

*(The Gantt chart itself should be the main visual here. Below is a reference for what it should show.)*

| Phase | Task | Duration |
|---|---|---|
| Week 1–2 | Planning, requirements gathering, ER diagram, system design | 2 weeks |
| Week 3–4 | Backend setup — database models, auth, user profiles | 2 weeks |
| Week 5–6 | Core features — meal tracking, step tracker, workout logger | 2 weeks |
| Week 7 | ML model — calorie burn predictor, nutrition calculator | 1 week |
| Week 8 | Frontend — all pages, dashboard, charts | 1 week |
| Week 9 | Admin panel, role management | 1 week |
| Week 10 | Testing, bug fixes, documentation | 1 week |

> **Image reference:** Insert an actual Gantt chart bar graph here. Use PowerPoint's built-in chart tool or a tool like TeamGantt/Excel. Rows = tasks listed above, columns = weeks. Use colour coding to show completed vs in-progress phases.

---

## Slide 7 — Use Case Description

**Title:** Who Uses GetFit and What Can They Do?

**Content:**

GetFit has four types of users, each with different levels of access:

**Guest** — can only sign up or log in. Nothing else is visible until they create an account.

**Registered User** — the main user. They can log meals, workouts, and steps. They get their personalised meal and workout plans. They can view their dashboard and edit their profile.

**Admin** — can do everything a regular user can, plus view all users on the platform and manage their accounts.

**Super Admin** — has full control, including the ability to promote or demote users to admin roles.

When a user logs a meal, the app reaches out to the **Nutritionix food database** in real time to fetch the calorie and nutrition data for that food.

> **Image reference:** Insert the Use Case Diagram from `DIAGRAMS.md` (Section 1). Export or screenshot the Mermaid flowchart rendered as a visual diagram. Alternatively, create a simple actor-feature grid graphic showing the four user types and their permissions.

---

## Slide 8 — ER Diagram

**Title:** How the Data is Stored

**Content:**

The app stores four main types of data:

- **Users** — your profile information: name, email, age, weight, height, fitness goal, activity level, and role (admin or not)
- **Food Logs** — every meal you record: the food name, calories, protein, carbs, fat, meal type (breakfast/lunch/dinner/snack), and timestamp
- **Workout Logs** — every workout session: exercise name, duration, heart rate, calories burned, and any notes
- **Step Logs** — daily step count entries: total steps and the estimated calories burned from walking

One user can have many food logs, many workout logs, and many step log entries. If a user account is deleted, all their data is removed automatically.

> **Image reference:** Insert the ER Diagram from `DIAGRAMS.md` (Section 3). Render the Mermaid diagram visually — show the four tables (USER, FOOD LOG, WORKOUT LOG, STEP LOG) connected by relationship diamonds. Tools like mermaid.live can export this as an image.

---

## Slide 9 — System Design

**Title:** How the App Works Behind the Scenes

**Content:**

GetFit is built in three layers that work together:

**1. What You See (Frontend)**
The screens you use in your browser — login, dashboard, meal tracker, step tracker, workout plan, profile, and admin panel. Built with React.

**2. The App's Brain (Backend)**
When you take an action (log a meal, get a workout plan), the frontend sends a request to the backend. The backend processes it — runs calculations, applies business rules, calls the ML model if needed — and sends back the result. Built with FastAPI.

**3. The Database**
Stores everything permanently — your profile, all your logs, and your history. Managed with SQLAlchemy.

**External service:** When you search for food, the backend contacts the Nutritionix API to fetch real food data, so we don't have to maintain our own food database.

> **Image reference:** Insert the System Design Diagram from `DIAGRAMS.md` (Section 2). Render the Mermaid flowchart — it shows the browser, frontend pages, backend modules, database, and Nutritionix as connected blocks with arrows showing the flow of requests.

---

## Slide 10 — Summary & What's Next

**Title:** What We Built and Where It Could Go

**Content:**

**What we built:**
GetFit is a fully working personalised fitness web app. A user can sign up, set their goals, get a meal plan and workout schedule in seconds, log their daily food and activity, and watch their progress over time — all from one app.

**Key achievements:**
- 3 personalised recommendation systems (meal plan, workout plan, calorie burn)
- Real food data via Nutritionix integration
- Role-based access with admin tools
- Machine learning calorie predictor using Lasso regression

**What could come next:**
- Mobile app version
- Wearable device sync (Fitbit, Apple Watch)
- Real clinical dataset for the ML model
- Progress photos and body measurement tracking
- Social features — friends, challenges, and leaderboards

> **Image reference:** A "roadmap" style graphic showing what was built (ticked items) and future features (upcoming milestones). Or a final screenshot of the app's dashboard as a closing visual.

---

## Quick Image Sourcing Guide

- **Diagrams from `DIAGRAMS.md`** — render at mermaid.live and export as PNG
- **App screenshots** — run the app locally and take screenshots of the main pages
- **Tech logos** — use the official logos for React, Python, FastAPI, scikit-learn (all freely available)
- **Gantt chart** — build directly in PowerPoint or Google Slides using the built-in chart tool

---

## Use Cases & Impact

### Use Cases — GetFit

Based on Slide 7, GetFit serves **four types of users** with distinct roles:

#### Actor-Based Use Cases

| Actor | What They Can Do |
|---|---|
| **Guest** | Sign up, Log in |
| **Registered User** | Set fitness goals, Get personalised meal plan, Get weekly workout plan, Log meals (with real-time Nutritionix data), Log workouts, Log daily steps, View dashboard & progress history, Edit profile |
| **Admin** | All of the above + View all platform users, Manage user accounts |
| **Super Admin** | All of the above + Promote/demote users to Admin roles |

#### Functional Use Cases (by Feature)

1. **Meal Planning** — User inputs age, weight, height, and goal → app calculates daily calorie & macro targets using the Mifflin-St Jeor equation → user logs meals against that target.
2. **Workout Planning** — User selects fitness level and available equipment → app auto-generates a structured weekly plan from a 50+ exercise database.
3. **Step Tracking** — User logs daily step count → app estimates calories burned from walking.
4. **Progress Monitoring** — User views their food, workout, and step history all in one dashboard with interactive charts.
5. **Admin Management** — Admin reviews all registered users and manages accounts; Super Admin controls role assignments.

---

### Impact of GetFit

#### Problem Solved
Most people bounce between multiple disconnected apps — a calorie calculator, a workout video, a step counter — that share no data. GetFit **consolidates everything into one personalised platform**, removing that fragmentation.

#### Direct User Impact
- **Removes guesswork** — Scientifically-grounded calorie targets (Mifflin-St Jeor) replace generic "eat 2000 calories" advice.
- **Personalisation at scale** — Each user gets a workout plan and meal target tailored to their specific body metrics and goals (fat loss, muscle gain, strength, endurance).
- **Behaviour tracking** — Logging meals, workouts, and steps in one place makes it easier for users to identify patterns and stay consistent.

#### Technical Impact
- Demonstrates a **full-stack ML-integrated application** — React frontend, FastAPI backend, SQLAlchemy ORM, and a Lasso Regression calorie-burn predictor working end-to-end.
- Integrates a **live external API** (Nutritionix) so food data is real and up-to-date, not static.
- Implements **role-based access control** (Guest → User → Admin → Super Admin), a real-world security pattern.

#### Future Potential
As noted in Slide 10, the foundation built here could extend to:
- Mobile app version
- Wearable sync (Fitbit, Apple Watch)
- Social features (challenges, leaderboards)
- Clinical-grade ML training data for more accurate calorie predictions

> **Summary:** GetFit's impact is replacing a fragmented multi-app fitness experience with a single, science-backed, personalised tool — while also serving as a strong demonstration of applied ML, REST APIs, and full-stack web development.
