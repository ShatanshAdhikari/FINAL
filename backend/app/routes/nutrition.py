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


def _search_usda(query: str) -> dict:
    """Search USDA FoodData Central (free, no-signup DEMO_KEY works for dev)."""
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": query,
        "api_key": settings.USDA_API_KEY,
        "pageSize": 10,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("foods", [])

    foods = []
    for item in items:
        name = item.get("description", "").strip()
        if not name:
            continue
        nutrients = {n["nutrientName"]: n.get("value", 0) for n in item.get("foodNutrients", [])}
        kcal = nutrients.get("Energy", 0)
        if not kcal:
            continue
        foods.append({
            "food_name": name.title(),
            "nf_calories": round(float(kcal), 1),
            "nf_protein": round(float(nutrients.get("Protein", 0)), 1),
            "nf_total_carbohydrate": round(float(nutrients.get("Carbohydrate, by difference", 0)), 1),
            "nf_total_fat": round(float(nutrients.get("Total lipid (fat)", 0)), 1),
            "serving_weight_grams": 100,
            "serving_qty": 100,
            "serving_unit": "g",
        })

    return {"foods": foods, "source": "USDA FoodData Central"}


def _flag_allergens(result: dict, allergies: Optional[str]) -> dict:
    """Annotate each returned food with an allergen warning if its name matches a user allergy."""
    tokens = [a.strip().lower() for a in (allergies or "").split(",") if a.strip()]
    if not tokens:
        return result
    for food in result.get("foods", []) or []:
        name = str(food.get("food_name", "")).lower()
        matched = [t for t in tokens if t and t in name]
        if matched:
            food["allergen_warning"] = True
            food["matched_allergens"] = matched
    return result


@router.post("/search")
def search_food(data: FoodSearchRequest, current_user: User = Depends(get_current_user)):
    """Search food — uses Nutritionix if API keys are set, else USDA FoodData Central (free)."""
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
        return _flag_allergens(response.json(), current_user.allergies)

    try:
        return _flag_allergens(_search_usda(data.query), current_user.allergies)
    except HTTPException:
        raise
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
