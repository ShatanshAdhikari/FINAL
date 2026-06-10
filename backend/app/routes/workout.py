from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.logs import WorkoutLog
from app.services.workout_recommender import generate_workout_plan
from app.ml.calorie_predictor import predict_calories

router = APIRouter(prefix="/workout", tags=["Workout"])


class WorkoutLogCreate(BaseModel):
    exercise_name: str
    duration_minutes: float
    heart_rate: Optional[float] = None
    calories_burned: Optional[float] = None
    notes: Optional[str] = None


class CaloriePredictRequest(BaseModel):
    duration_minutes: float
    heart_rate: float
    body_temp: Optional[float] = 37.5


@router.get("/plan")
def get_workout_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not all([current_user.fitness_level, current_user.goal, current_user.workout_frequency]):
        raise HTTPException(status_code=400, detail="Please complete your profile first (fitness_level, goal, workout_frequency)")

    plan = generate_workout_plan(
        fitness_level=current_user.fitness_level,
        goal=current_user.goal,
        workout_frequency=current_user.workout_frequency,
        age=current_user.age or 25,
        gender=current_user.gender or "male",
    )
    return plan


@router.post("/predict-calories")
def predict_workout_calories(
    data: CaloriePredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    missing = [f for f, v in {
        "gender": current_user.gender,
        "age":    current_user.age,
        "weight": current_user.weight,
        "height": current_user.height,
    }.items() if not v]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Profile incomplete — please set: {', '.join(missing)}"
        )

    calories = predict_calories(
        gender=current_user.gender,
        age=current_user.age,
        height=current_user.height,
        weight=current_user.weight,
        duration=data.duration_minutes,
        heart_rate=data.heart_rate,
        body_temp=data.body_temp or 37.5,
    )
    return {"predicted_calories_burned": calories}


@router.post("/log")
def log_workout(
    data: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = WorkoutLog(
        user_id=current_user.id,
        exercise_name=data.exercise_name,
        duration_minutes=data.duration_minutes,
        heart_rate=data.heart_rate,
        calories_burned=data.calories_burned,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Workout logged", "id": log.id}


@router.get("/logs")
def get_workout_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = db.query(WorkoutLog).filter(WorkoutLog.user_id == current_user.id).order_by(WorkoutLog.logged_at.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "exercise_name": l.exercise_name,
            "duration_minutes": l.duration_minutes,
            "heart_rate": l.heart_rate,
            "calories_burned": l.calories_burned,
            "notes": l.notes,
            "logged_at": l.logged_at.isoformat(),
        }
        for l in logs
    ]
