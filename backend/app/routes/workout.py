from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
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
def get_workout_plan(current_user: User = Depends(get_current_user)):
    if not all([current_user.fitness_level, current_user.goal, current_user.workout_frequency]):
        raise HTTPException(status_code=400, detail="Please complete your profile first (fitness_level, goal, workout_frequency)")

    plan = generate_workout_plan(
        fitness_level=current_user.fitness_level or "",
        goal=current_user.goal or "",
        workout_frequency=current_user.workout_frequency or 3,
        age=current_user.age or 25,
        gender=current_user.gender or "male",
        user_id=current_user.id,
    )
    return plan


@router.post("/predict-calories")
def predict_workout_calories(
    data: CaloriePredictRequest,
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
        gender=current_user.gender or "",
        age=current_user.age or 0,
        height=current_user.height or 0.0,
        weight=current_user.weight or 0.0,
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
            "id": log.id,
            "exercise_name": log.exercise_name,
            "duration_minutes": log.duration_minutes,
            "heart_rate": log.heart_rate,
            "calories_burned": log.calories_burned,
            "notes": log.notes,
            "logged_at": log.logged_at.isoformat() if log.logged_at else None,
        }
        for log in logs
    ]
