FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

# DATABASE_URL comes from the environment (Neon Postgres in prod; falls back to
# the SQLite volume for local docker-compose). PORT is provided by Render.
# seed_users.py is idempotent (upserts by email/username) so it's safe to run
# on every start — it creates demo users only if they're missing.
ENV DATABASE_URL=sqlite:////data/getfit.db
CMD ["sh", "-c", "\
  echo '[docker] Seeding demo users (idempotent)...' && \
  python seed_users.py; \
  uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} \
"]
