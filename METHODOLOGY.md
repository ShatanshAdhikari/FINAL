# GetFit — Development Methodology

## What methodology do we use? → Scrum

Scrum is a type of **Agile** methodology.

The idea is simple:
> Instead of planning everything at once, you build the app **piece by piece** in short cycles called **Sprints**.

Each Sprint is **2 weeks** long. At the end of every Sprint, you have something that **actually works**.

---

## Why Scrum for GetFit?

GetFit has features that are **independent from each other**. You can build and test one feature without needing another to be done.

For example:
- You can build **Login** without needing the Workout Tracker to exist
- You can build the **Calorie Tracker** without the Admin Panel

This makes Scrum a perfect fit.

---

## Why not the others?

| Method | Problem |
|---|---|
| **Waterfall** | You plan everything first, then build. If something changes, you're stuck. Too rigid for an app. |
| **Kanban** | Better for fixing bugs and small tasks. Not great for building a full app from scratch. |
| **XP (Extreme Programming)** | Too strict. Requires pair programming and heavy testing from day one. |

---

## How Scrum Works — Simply

```
Step 1 → Write down all features you want to build  (Backlog)
Step 2 → Pick a few features to build this week     (Sprint Planning)
Step 3 → Build them over 2 weeks                    (Sprint)
Step 4 → Show what you built                        (Sprint Review)
Step 5 → Think about what went well / what didn't   (Retrospective)
Step 6 → Repeat with the next set of features       (Next Sprint)
```

---

## GetFit — Sprint Plan

### 🔴 Sprint 1 — Weeks 1 & 2: Foundation
> Goal: Users can create accounts and set up their profile

- [ ] User Registration
- [ ] User Login (JWT tokens)
- [ ] Onboarding flow (age, weight, height, goal, fitness level)
- [ ] Update Profile page

---

### 🔴 Sprint 2 — Weeks 3 & 4: Nutrition Tracker
> Goal: Users can search and log what they eat

- [ ] Search food using Nutritionix API
- [ ] Log a meal (breakfast / lunch / dinner / snack)
- [ ] View today's calorie and macro summary
- [ ] View nutrition history (last 7 days)
- [ ] Delete a food log

---

### 🔴 Sprint 3 — Weeks 5 & 6: Workout Features
> Goal: Users can get a workout plan and track their sessions

- [ ] Generate personalised workout plan (based on goal + fitness level)
- [ ] Log a workout session (exercise, duration, heart rate)
- [ ] Predict calories burned using ML model
- [ ] View workout history

---

### 🟡 Sprint 4 — Weeks 7 & 8: Step Tracker + Dashboard
> Goal: Users can track daily steps and see everything in one place

- [ ] Log daily steps
- [ ] Calculate calories burned from steps
- [ ] View step history (last 7 days)
- [ ] Dashboard with summary cards and charts

---

### 🟢 Sprint 5 — Weeks 9 & 10: Admin Panel + Final Polish
> Goal: Admins can manage the platform, app is ready to ship

- [ ] Admin: view all users
- [ ] Admin: activate / deactivate users
- [ ] Admin: delete users
- [ ] Super Admin: promote / demote roles
- [ ] Platform stats (total users, logs)
- [ ] Bug fixes and UI polish

---

## Feature Priority Guide

| Symbol | Meaning |
|---|---|
| 🔴 Must Have | App doesn't work without this |
| 🟡 Should Have | Important, but app can launch without it |
| 🟢 Nice to Have | Adds value, but not urgent |

---

## Daily Standup (3 Questions)

Every day, answer these 3 questions:

1. **What did I do yesterday?**
2. **What will I do today?**
3. **Is anything blocking me?**

Keep it short — under 5 minutes.

---

## Scrum Roles

| Role | Who | Job |
|---|---|---|
| **Product Owner** | You / Client | Decides what to build and in what order |
| **Scrum Master** | Team Lead | Makes sure the process runs smoothly, removes blockers |
| **Dev Team** | Developers | Designs, builds, and tests the features |

---

## Quick Summary

| Topic | Decision |
|---|---|
| Methodology | Scrum (Agile) |
| Sprint Length | 2 weeks |
| Total Sprints | 5 |
| Total Duration | ~10 weeks |
| Works for team size | 1 to 5 people |
| Main benefit | Always have a working version of the app |
