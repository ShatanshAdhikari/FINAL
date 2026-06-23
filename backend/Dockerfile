FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

CMD ["sh", "-c", "\
  if [ ! -f /data/getfit.db ]; then \
    echo '[docker] Seeding demo users...' && \
    DATABASE_URL=sqlite:////data/getfit.db python seed_users.py; \
  else \
    echo '[docker] Database exists -- skipping seed.'; \
  fi && \
  DATABASE_URL=sqlite:////data/getfit.db \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 \
"]
