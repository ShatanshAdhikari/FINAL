from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from app.core.database import engine, Base
from app.core.config import settings
import app.models  # ensure models are registered

limiter = Limiter(key_func=get_remote_address)

# Create tables
Base.metadata.create_all(bind=engine)

# Legacy in-place column migrations use SQLite PRAGMA syntax. On Postgres the
# schema above is created complete from the models, so these are skipped.
if engine.dialect.name == "sqlite":
    # Migrate existing workout_logs table to add sets/reps columns if missing
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(workout_logs)"))}
        if "sets" not in existing:
            conn.execute(text("ALTER TABLE workout_logs ADD COLUMN sets INTEGER"))
        if "reps" not in existing:
            conn.execute(text("ALTER TABLE workout_logs ADD COLUMN reps INTEGER"))
        conn.commit()

    # Migrate existing users table to add new account/health/oauth columns if missing
    with engine.connect() as conn:
        user_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        # Existing rows are pre-verification accounts with real passwords → default verified.
        if "is_verified" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 1 NOT NULL"))
        if "oauth_provider" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR"))
        if "google_sub" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN google_sub VARCHAR"))
        if "allergies" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN allergies TEXT"))
        if "diseases" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN diseases TEXT"))
        conn.commit()

app = FastAPI(
    title="GetFit API",
    description="Personalized Fitness & Nutrition App API",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from app.routes import auth, profile, workout, nutrition, steps, admin
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(workout.router)
app.include_router(nutrition.router)
app.include_router(steps.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Welcome to GetFit API 💪", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
