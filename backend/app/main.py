from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine, Base
import app.models  # ensure models are registered

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
