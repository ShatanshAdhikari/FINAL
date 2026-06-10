from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.services.nutrition_calculator import get_full_nutrition_plan

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    fitness_level: Optional[str] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    workout_frequency: Optional[int] = None
    equipment: Optional[str] = None


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
    }}


@router.get("/nutrition-plan")
def get_nutrition_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not all([current_user.gender, current_user.age, current_user.weight, current_user.height,
                current_user.activity_level, current_user.goal, current_user.fitness_level]):
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    plan = get_full_nutrition_plan(
        gender=current_user.gender,
        age=current_user.age,
        weight=current_user.weight,
        height=current_user.height,
        activity_level=current_user.activity_level,
        goal=current_user.goal,
        fitness_level=current_user.fitness_level,
    )
    return plan
