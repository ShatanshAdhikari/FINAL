from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.logs import WeightLog
from app.services.nutrition_calculator import get_full_nutrition_plan

router = APIRouter(prefix="/profile", tags=["Profile"])

VALID_GOALS = {"fat_loss", "muscle_gain", "strength", "endurance"}
VALID_FITNESS_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_ACTIVITY_LEVELS = {"sedentary", "light", "moderate", "active", "very_active"}
VALID_GENDERS = {"male", "female"}


class ProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Literal["male", "female"]] = None
    weight: Optional[float] = Field(None, ge=20, le=500)
    height: Optional[float] = Field(None, ge=50, le=300)
    fitness_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    goal: Optional[Literal["fat_loss", "muscle_gain", "strength", "endurance"]] = None
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = None
    workout_frequency: Optional[int] = Field(None, ge=1, le=7)
    equipment: Optional[str] = Field(None, max_length=200)
    allergies: Optional[str] = Field(None, max_length=500)
    diseases: Optional[str] = Field(None, max_length=500)


@router.put("/")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated", "user": {
        "id": current_user.id,
        "username": current_user.username,
        "age": current_user.age,
        "gender": current_user.gender,
        "weight": current_user.weight,
        "height": current_user.height,
        "fitness_level": current_user.fitness_level,
        "goal": current_user.goal,
        "activity_level": current_user.activity_level,
        "workout_frequency": current_user.workout_frequency,
        "equipment": current_user.equipment,
        "allergies": current_user.allergies,
        "diseases": current_user.diseases,
    }}


class WeightLogCreate(BaseModel):
    weight: float = Field(..., ge=20, le=500)
    date: Optional[str] = None  # YYYY-MM-DD, defaults to today


@router.post("/weight")
def log_weight(
    data: WeightLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    date_str = data.date or datetime.now(timezone.utc).date().isoformat()
    # Upsert: replace entry for the same date if it exists
    existing = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id,
        WeightLog.date == date_str,
    ).first()
    if existing:
        existing.weight = data.weight
        existing.logged_at = datetime.now(timezone.utc)
    else:
        db.add(WeightLog(user_id=current_user.id, weight=data.weight, date=date_str))
    db.commit()
    return {"message": "Weight logged", "weight": data.weight, "date": date_str}


@router.get("/weight-history")
def get_weight_history(
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    logs = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == current_user.id, WeightLog.date >= since)
        .order_by(WeightLog.date)
        .all()
    )
    return [{"date": l.date, "weight": l.weight} for l in logs]


@router.get("/nutrition-plan")
def get_nutrition_plan(current_user: User = Depends(get_current_user)):
    if not all([current_user.gender, current_user.age, current_user.weight, current_user.height,
                current_user.activity_level, current_user.goal, current_user.fitness_level]):
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    plan = get_full_nutrition_plan(
        gender=current_user.gender or "",
        age=current_user.age or 0,
        weight=current_user.weight or 0.0,
        height=current_user.height or 0.0,
        activity_level=current_user.activity_level or "",
        goal=current_user.goal or "",
        fitness_level=current_user.fitness_level or "",
        conditions=current_user.diseases,
        allergies=current_user.allergies,
    )
    return plan
