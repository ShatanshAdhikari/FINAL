from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import requests
from app.core.database import get_db
from app.core.config import settings
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.logs import CalorieLog

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


class FoodSearchRequest(BaseModel):
    query: str


class CalorieLogCreate(BaseModel):
    food_name: str
    calories: float
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    meal_type: Optional[str] = "snack"


@router.post("/search")
def search_food(data: FoodSearchRequest):
    """Search food using Nutritionix API."""
    if not settings.NUTRITIONIX_APP_ID or not settings.NUTRITIONIX_API_KEY:
        # Return mock data if no API key
        return {
            "foods": [
                {"food_name": data.query, "nf_calories": 200, "nf_protein": 10,
                 "nf_total_carbohydrate": 25, "nf_total_fat": 8, "serving_qty": 1, "serving_unit": "serving"}
            ],
            "note": "Using mock data. Add NUTRITIONIX_APP_ID and NUTRITIONIX_API_KEY to .env for real data."
        }

    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": settings.NUTRITIONIX_APP_ID,
        "x-app-key": settings.NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.post(url, json={"query": data.query}, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Nutritionix API error")
    return response.json()


@router.post("/log")
def log_food(
    data: CalorieLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = CalorieLog(
        user_id=current_user.id,
        food_name=data.food_name,
        calories=data.calories,
        protein=data.protein,
        carbs=data.carbs,
        fat=data.fat,
        meal_type=data.meal_type,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Food logged", "id": log.id}


@router.get("/logs/today")
def get_today_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.utcnow().date()
    logs = db.query(CalorieLog).filter(
        CalorieLog.user_id == current_user.id,
        CalorieLog.logged_at >= datetime.combine(today, datetime.min.time()),
    ).all()

    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    items = []
    for l in logs:
        total["calories"] += l.calories
        total["protein"] += l.protein or 0
        total["carbs"] += l.carbs or 0
        total["fat"] += l.fat or 0
        items.append({
            "id": l.id,
            "food_name": l.food_name,
            "calories": l.calories,
            "protein": l.protein,
            "carbs": l.carbs,
            "fat": l.fat,
            "meal_type": l.meal_type,
            "logged_at": l.logged_at.isoformat(),
        })

    return {"logs": items, "totals": {k: round(v, 1) for k, v in total.items()}}


@router.get("/logs/history")
def get_nutrition_history(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import timedelta
    start = datetime.utcnow() - timedelta(days=days)
    logs = db.query(CalorieLog).filter(
        CalorieLog.user_id == current_user.id,
        CalorieLog.logged_at >= start,
    ).all()

    history = {}
    for l in logs:
        day = l.logged_at.date().isoformat()
        if day not in history:
            history[day] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        history[day]["calories"] += l.calories
        history[day]["protein"] += l.protein or 0
        history[day]["carbs"] += l.carbs or 0
        history[day]["fat"] += l.fat or 0

    return [{"date": k, **{m: round(v, 1) for m, v in vals.items()}} for k, vals in sorted(history.items())]


@router.delete("/log/{log_id}")
def delete_food_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(CalorieLog).filter(CalorieLog.id == log_id, CalorieLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"message": "Log deleted"}
