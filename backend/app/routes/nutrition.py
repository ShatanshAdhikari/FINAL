from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
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


def _search_openfoodfacts(query: str) -> dict:
    """Search OpenFoodFacts v2 REST API (free, no key) and normalise to Nutritionix shape."""
    url = "https://world.openfoodfacts.org/api/v2/search"
    params = {
        "search_terms": query,
        "fields": "product_name,nutriments,serving_quantity",
        "page_size": 10,
        "json": 1,
    }
    headers: dict[str, str | bytes] = {"User-Agent": "GetFit-App/1.0 (open-source fitness tracker)"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    products = resp.json().get("products", [])

    foods = []
    for p in products:
        name = p.get("product_name", "").strip()
        if not name:
            continue
        n = p.get("nutriments", {})
        kcal = n.get("energy-kcal_100g") or (n.get("energy_100g", 0) / 4.184)
        if not kcal:
            continue  # skip entries with no calorie data
        foods.append({
            "food_name": name,
            "nf_calories": round(float(kcal), 1),
            "nf_protein": round(float(n.get("proteins_100g", 0)), 1),
            "nf_total_carbohydrate": round(float(n.get("carbohydrates_100g", 0)), 1),
            "nf_total_fat": round(float(n.get("fat_100g", 0)), 1),
            "serving_weight_grams": 100,
            "serving_qty": 100,
            "serving_unit": "g",
        })

    return {"foods": foods, "source": "OpenFoodFacts"}


@router.post("/search")
def search_food(data: FoodSearchRequest, current_user: User = Depends(get_current_user)):
    """Search food — uses Nutritionix if API keys are set, else OpenFoodFacts (free)."""
    if settings.NUTRITIONIX_APP_ID and settings.NUTRITIONIX_API_KEY:
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers: dict[str, str | bytes] = {
            "x-app-id": settings.NUTRITIONIX_APP_ID,
            "x-app-key": settings.NUTRITIONIX_API_KEY,
            "Content-Type": "application/json",
        }
        response = requests.post(url, json={"query": data.query}, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Nutritionix API error")
        return response.json()

    try:
        return _search_openfoodfacts(data.query)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Food search is temporarily unavailable. You can still log food manually using the calorie log."
        )


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
    today = datetime.now(timezone.utc).date()
    midnight = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    logs = db.query(CalorieLog).filter(
        CalorieLog.user_id == current_user.id,
        CalorieLog.logged_at >= midnight,
    ).all()

    total: dict[str, float] = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    items = []
    for entry in logs:
        total["calories"] += entry.calories
        total["protein"] += entry.protein or 0
        total["carbs"] += entry.carbs or 0
        total["fat"] += entry.fat or 0
        items.append({
            "id": entry.id,
            "food_name": entry.food_name,
            "calories": entry.calories,
            "protein": entry.protein,
            "carbs": entry.carbs,
            "fat": entry.fat,
            "meal_type": entry.meal_type,
            "logged_at": entry.logged_at.isoformat() if entry.logged_at else None,
        })

    return {"logs": items, "totals": {k: round(v, 1) for k, v in total.items()}}


@router.get("/logs/history")
def get_nutrition_history(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = datetime.now(timezone.utc) - timedelta(days=days)
    logs = db.query(CalorieLog).filter(
        CalorieLog.user_id == current_user.id,
        CalorieLog.logged_at >= start,
    ).all()

    history: dict = {}
    for entry in logs:
        day = entry.logged_at.date().isoformat() if entry.logged_at else ""
        if day not in history:
            history[day] = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        history[day]["calories"] += entry.calories
        history[day]["protein"] += entry.protein or 0
        history[day]["carbs"] += entry.carbs or 0
        history[day]["fat"] += entry.fat or 0

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
