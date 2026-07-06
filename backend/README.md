# GetFit — Backend API

FastAPI + SQLite backend for the GetFit fitness tracking application.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Seeded Accounts](#seeded-accounts)
- [Role Permissions](#role-permissions)
- [API Endpoints](#api-endpoints)
- [User Management Scripts](#user-management-scripts)
- [Environment Variables](#environment-variables)

---

## Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database (creates all accounts below)
python seed_users.py

# 4. Start the server
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

---

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings / env vars
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   └── security.py        # JWT & password hashing
│   ├── models/
│   │   ├── user.py            # User model (roles, profile)
│   │   └── logs.py            # Calorie / Workout / Step logs
│   ├── routes/
│   │   ├── auth.py            # Register, login, /me
│   │   ├── admin.py           # Admin & super-admin management
│   │   ├── profile.py         # Profile CRUD
│   │   ├── workout.py         # Workout logging
│   │   ├── nutrition.py       # Nutrition / calorie logging
│   │   └── steps.py           # Step tracking
│   ├── services/              # Business logic helpers
│   ├── ml/                    # Calorie prediction model
│   └── main.py                # FastAPI app entry point
├── create_admin.py            # CLI to create / promote admins
├── seed_users.py              # One-shot database seeder
├── requirements.txt
└── .env                       # Local environment variables
```

---

## Seeded Accounts

Run `python seed_users.py` to populate the database with these accounts.

### Super-Admin

| Role        | Username     | Email                    | Password        |
|-------------|--------------|--------------------------|-----------------|
| Super-Admin | `shatansh`   | shatansh@gmail.com       | `SuperAdmin@123` |

### Admins

| Role  | Username    | Email               | Password     |
|-------|-------------|---------------------|--------------|
| Admin | `prerana`   | prerana@gmail.com   | `Admin@1234` |

### Regular Users

| Role | Username    | Email                | Password     |
|------|-------------|----------------------|--------------|
| User | `maria`     | maria@gmail.com      | `User@1234`  |
| User | `neha`      | neha@gmail.com       | `User@1234`  |
| User | `animesh`   | animesh@gmail.com    | `User@1234`  |
| User | `biplov`    | biplov@gmail.com     | `User@1234`  |
| User | `binav`     | binav@gmail.com      | `User@1234`  |

> **Note:** These are development/testing credentials only. Change all passwords before deploying to production.

---

## Role Permissions

| Action                          | User | Admin | Super-Admin |
|---------------------------------|:----:|:-----:|:-----------:|
| Register / Login                |  ✓   |   ✓   |      ✓      |
| View & update own profile       |  ✓   |   ✓   |      ✓      |
| Log workouts / nutrition / steps|  ✓   |   ✓   |      ✓      |
| View all users                  |  ✗   |   ✓   |      ✓      |
| View any user's details         |  ✗   |   ✓   |      ✓      |
| Toggle user active/inactive     |  ✗   |   ✓   |      ✓      |
| Delete regular users            |  ✗   |   ✓   |      ✓      |
| Delete admin users              |  ✗   |   ✗   |      ✓      |
| Promote user → admin            |  ✗   |   ✗   |      ✓      |
| Demote admin → user             |  ✗   |   ✗   |      ✓      |
| Promote user → super-admin      |  ✗   |   ✗   |      ✓      |
| Demote super-admin → admin      |  ✗   |   ✗   |      ✓      |
| View platform stats             |  ✗   |   ✓   |      ✓      |

---

## API Endpoints

### Authentication — `/auth`

| Method | Endpoint          | Description                        | Auth Required |
|--------|-------------------|------------------------------------|:-------------:|
| POST   | `/auth/register`  | Register a new user                | No            |
| POST   | `/auth/login`     | Login (returns JWT token)          | No            |
| GET    | `/auth/me`        | Get current user info              | Yes           |

### Profile — `/profile`

| Method | Endpoint    | Description                  | Auth Required |
|--------|-------------|------------------------------|:-------------:|
| GET    | `/profile`  | Get own profile              | Yes           |
| PUT    | `/profile`  | Update own profile           | Yes           |

### Workouts — `/workout`

| Method | Endpoint              | Description              | Auth Required |
|--------|-----------------------|--------------------------|:-------------:|
| GET    | `/workout`            | List own workout logs    | Yes           |
| POST   | `/workout`            | Log a workout            | Yes           |
| DELETE | `/workout/{id}`       | Delete a workout log     | Yes           |

### Nutrition — `/nutrition`

| Method | Endpoint              | Description              | Auth Required |
|--------|-----------------------|--------------------------|:-------------:|
| GET    | `/nutrition`          | List own calorie logs    | Yes           |
| POST   | `/nutrition`          | Log a meal               | Yes           |
| DELETE | `/nutrition/{id}`     | Delete a calorie log     | Yes           |

### Steps — `/steps`

| Method | Endpoint        | Description           | Auth Required |
|--------|-----------------|-----------------------|:-------------:|
| GET    | `/steps`        | List own step logs    | Yes           |
| POST   | `/steps`        | Log steps             | Yes           |

### Admin — `/admin`

| Method | Endpoint                                 | Description                    | Role Required |
|--------|------------------------------------------|--------------------------------|:-------------:|
| GET    | `/admin/users`                           | List all users                 | Admin         |
| GET    | `/admin/users/{id}`                      | Get user details               | Admin         |
| DELETE | `/admin/users/{id}`                      | Delete a user                  | Admin         |
| PATCH  | `/admin/users/{id}/toggle-active`        | Activate / deactivate user     | Admin         |
| PATCH  | `/admin/users/{id}/promote-admin`        | Promote user to admin          | Super-Admin   |
| PATCH  | `/admin/users/{id}/demote-admin`         | Demote admin to user           | Super-Admin   |
| PATCH  | `/admin/users/{id}/promote-super-admin`  | Promote user to super-admin    | Super-Admin   |
| PATCH  | `/admin/users/{id}/demote-super-admin`   | Demote super-admin to admin    | Super-Admin   |
| GET    | `/admin/stats`                           | Platform statistics            | Admin         |

---

## User Management Scripts

### `seed_users.py` — Seed all accounts at once

```bash
python seed_users.py           # Create accounts (skips existing)
python seed_users.py --reset   # Wipe all users, then re-seed
```

### `create_admin.py` — Create or promote individual accounts

```bash
# Interactively create a new admin
python create_admin.py

# Interactively create a new super-admin
python create_admin.py --super

# Promote an existing user to admin
python create_admin.py --promote <username>

# Promote an existing user to super-admin
python create_admin.py --promote-super <username>

# List all admin and super-admin accounts
python create_admin.py --list
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable                      | Default              | Description                        |
|-------------------------------|----------------------|------------------------------------|
| `DATABASE_URL`                | `sqlite:///./getfit.db` | Database connection string      |
| `SECRET_KEY`                  | —                    | JWT signing secret (keep private)  |
| `ALGORITHM`                   | `HS256`              | JWT algorithm                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                 | Token expiry in minutes            |
