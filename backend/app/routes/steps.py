from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.logs import StepLog
from app.services.nutrition_calculator import calculate_calories_from_steps, calculate_bmr

router = APIRouter(prefix="/steps", tags=["Steps"])


class StepLogCreate(BaseModel):
    steps: int = Field(..., ge=0, le=100_000)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


@router.post("/log")
def log_steps(
    data: StepLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    weight = current_user.weight or 70
    calories = calculate_calories_from_steps(data.steps, weight)

    # Update or create
    existing = db.query(StepLog).filter(
        StepLog.user_id == current_user.id,
        StepLog.date == data.date
    ).first()

    if existing:
        existing.steps = data.steps
        existing.calories_from_steps = calories
        db.commit()
        db.refresh(existing)
        return {"message": "Steps updated", "calories_from_steps": calories}

    log = StepLog(
        user_id=current_user.id,
        steps=data.steps,
        calories_from_steps=calories,
        date=data.date,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Steps logged", "calories_from_steps": calories}


@router.get("/today")
def get_today_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date().isoformat()
    log = db.query(StepLog).filter(
        StepLog.user_id == current_user.id,
        StepLog.date == today
    ).first()

    bmr = None
    if all([current_user.gender, current_user.weight, current_user.height, current_user.age]):
        bmr = round(calculate_bmr(current_user.gender or "", current_user.weight or 0.0, current_user.height or 0.0, current_user.age or 0), 0)

    return {
        "date": today,
        "steps": log.steps if log else 0,
        "calories_from_steps": log.calories_from_steps if log else 0,
        "bmr": bmr,
    }


@router.get("/history")
def get_step_history(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dates = [(datetime.now(timezone.utc).date() - timedelta(days=i)).isoformat() for i in range(days)]
    logs = db.query(StepLog).filter(
        StepLog.user_id == current_user.id,
        StepLog.date.in_(dates)
    ).all()

    log_map = {l.date: l for l in logs}
    return [
        {
            "date": d,
            "steps": log_map[d].steps if d in log_map else 0,
            "calories": log_map[d].calories_from_steps if d in log_map else 0,
        }
        for d in reversed(dates)
    ]
