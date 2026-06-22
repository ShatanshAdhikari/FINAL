# PR: Add Docker support for one-command demo startup

## Summary

- Add `backend/Dockerfile`, `frontend/Dockerfile`, and `docker-compose.yml` so the entire GetFit app starts with `docker compose up --build` — no Python or Node.js installation required on the host.
- Add `backend/.dockerignore` and `frontend/.dockerignore` to keep images lean and secrets out.
- Update `frontend/vite.config.js` to read the proxy target from `VITE_API_TARGET` env var (falls back to `http://localhost:8000`), so the Vite proxy works both in Docker and via the existing `.bat` scripts.
- Update `DOCUMENTATION.md` to v1.3.0: new Section 17 (Docker Setup), Option D in How to Run, Infrastructure table in Technology Stack, updated Vite proxy explanation, and v1.3.0 changelog entry.

## What changed

| File | Change |
|---|---|
| `backend/Dockerfile` | New — Python 3.11-slim, pip install, conditional DB seed on first run, Uvicorn |
| `backend/.dockerignore` | New — excludes venv, .env, *.db, tests/, notebooks/ |
| `frontend/Dockerfile` | New — Node 20-slim, npm ci, Vite dev server bound to 0.0.0.0 |
| `frontend/.dockerignore` | New — excludes node_modules/ and dist/ |
| `docker-compose.yml` | New — both services, named SQLite volume, healthcheck, frontend waits for backend |
| `frontend/vite.config.js` | Updated proxy target: `process.env.VITE_API_TARGET \|\| 'http://localhost:8000'` |
| `DOCUMENTATION.md` | Updated to v1.3.0 — Section 17, Option D, Infrastructure stack, changelog |

## How it works

```
Browser
  ├── :5173  →  frontend container (Vite dev server)
  │                  └── /api/* proxy  →  backend container (Uvicorn :8000)
  │                                             └── SQLite at /data/getfit.db
  │                                                     (named Docker volume)
  └── :8000  →  backend container (direct API / Swagger docs)
```

**First run behaviour:** The backend container checks whether `/data/getfit.db` exists. If not, it runs `seed_users.py` to create 8 demo accounts, then starts the server. On subsequent runs, seeding is skipped automatically.

**Secret handling:** `SECRET_KEY`, `USDA_API_KEY`, and all other secrets are read from `backend/.env` via `env_file` in compose — they are never baked into the Docker image. `DATABASE_URL` is overridden to point to the named volume.

**Existing `.bat` workflow unchanged:** The `VITE_API_TARGET` fallback means local dev still proxies to `http://localhost:8000` with no changes required.

## Test plan

- [ ] `docker compose up --build` completes without errors
- [ ] Backend logs show `[docker] Seeding demo users...` on first run
- [ ] `http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `http://localhost:5173` loads the React app
- [ ] Login with `superadmin@getfit.com / SuperAdmin@123` succeeds and all pages work
- [ ] `docker compose down && docker compose up` — second run shows `[docker] Database exists -- skipping seed.`
- [ ] `start-all.bat` still works as before (local dev not broken)
- [ ] DOCUMENTATION.md Section 17 renders correctly on GitHub

---

Generated with [Claude Code](https://claude.com/claude-code)
