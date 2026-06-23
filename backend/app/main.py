from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from app.core.database import engine, Base
import app.models  # ensure models are registered

limiter = Limiter(key_func=get_remote_address)

# Create tables
Base.metadata.create_all(bind=engine)

# Migrate existing workout_logs table to add sets/reps columns if missing
with engine.connect() as conn:
    existing = {row[1] for row in conn.execute(text("PRAGMA table_info(workout_logs)"))}
    if "sets" not in existing:
        conn.execute(text("ALTER TABLE workout_logs ADD COLUMN sets INTEGER"))
    if "reps" not in existing:
        conn.execute(text("ALTER TABLE workout_logs ADD COLUMN reps INTEGER"))
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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
