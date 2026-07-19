"""
Nutrition Calculator - BMR, TDEE, and Macronutrient Distribution
Based on Mifflin-St Jeor equation as described in the GetFit documentation (Section 3.2.4)
"""
from typing import Dict, List, Optional


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Protein per kg based on fitness level (g/kg)
PROTEIN_PER_KG = {
    "beginner":     {"fat_loss": 1.6, "muscle_gain": 1.8, "strength": 1.8, "endurance": 1.4},
    "intermediate": {"fat_loss": 1.8, "muscle_gain": 2.0, "strength": 2.0, "endurance": 1.6},
    "advanced":     {"fat_loss": 2.0, "muscle_gain": 2.2, "strength": 2.4, "endurance": 1.8},
}

# Fat and Carb % of remaining calories after protein
MACRO_RATIOS = {
    "fat_loss":    {"fat": 35, "carb": 65},
    "muscle_gain": {"fat": 25, "carb": 75},
    "strength":    {"fat": 30, "carb": 70},
    "endurance":   {"fat": 20, "carb": 80},
}


def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level.lower(), 1.2)
    return round(bmr * multiplier, 2)


def calculate_calorie_goal(tdee: float, goal: str) -> float:
    """Adjust calories based on fitness goal."""
    adjustments = {
        "fat_loss":    -500,
        "muscle_gain": +300,
        "endurance":   +150,
        "strength":    0,
    }
    adj = adjustments.get(goal.lower(), 0)
    return round(tdee + adj, 2)


def calculate_macros(
    total_calories: float,
    weight: float,
    fitness_level: str,
    goal: str,
) -> Dict:
    """Calculate macronutrient distribution."""
    level = fitness_level.lower()
    goal_key = goal.lower()

    # Protein
    protein_g_per_kg = PROTEIN_PER_KG.get(level, PROTEIN_PER_KG["beginner"]).get(goal_key, 1.8)
    protein_g = round(weight * protein_g_per_kg, 1)
    protein_kcal = protein_g * 4

    # Remaining calories for fat and carbs
    remaining_kcal = max(total_calories - protein_kcal, 0)
    ratios = MACRO_RATIOS.get(goal_key, MACRO_RATIOS["muscle_gain"])

    fat_kcal = remaining_kcal * (ratios["fat"] / 100)
    carb_kcal = remaining_kcal * (ratios["carb"] / 100)

    fat_g = round(fat_kcal / 9, 1)
    carb_g = round(carb_kcal / 4, 1)

    return {
        "calories": round(total_calories, 0),
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carbs_g": carb_g,
        "protein_pct": round((protein_kcal / total_calories) * 100, 1) if total_calories else 0,
        "fat_pct": round((fat_kcal / total_calories) * 100, 1) if total_calories else 0,
        "carbs_pct": round((carb_kcal / total_calories) * 100, 1) if total_calories else 0,
    }


def _apply_condition_adjustments(macros: Dict, conditions: Optional[str]) -> List[str]:
    """
    Adjust macros in place for certain diseases and return advisory notes.
    Kept conservative and clearly advisory — not medical advice.
    """
    notes: List[str] = []
    if not conditions:
        return notes
    tokens = [c.strip().lower() for c in conditions.split(",") if c.strip()]

    def has(*keys: str) -> bool:
        return any(any(k in t for k in keys) for t in tokens)

    if has("diabet"):
        # Shift ~15% of carb grams toward protein/fat to reduce glycemic load.
        shift = round(macros["carbs_g"] * 0.15, 1)
        macros["carbs_g"] = round(macros["carbs_g"] - shift, 1)
        macros["protein_g"] = round(macros["protein_g"] + shift * 0.5, 1)
        macros["fat_g"] = round(macros["fat_g"] + (shift * 0.5) * (4 / 9), 1)
        notes.append("Carbohydrates were reduced to help manage blood sugar (diabetes reported).")
    if has("pcos", "insulin resist", "prediabet", "fatty liver"):
        # Same insulin-sensitivity rationale as diabetes — trim refined carbs.
        shift = round(macros["carbs_g"] * 0.10, 1)
        macros["carbs_g"] = round(macros["carbs_g"] - shift, 1)
        macros["protein_g"] = round(macros["protein_g"] + shift * 0.5, 1)
        notes.append("Refined carbohydrates were trimmed to support insulin sensitivity.")
    if has("hypertension", "blood pressure"):
        notes.append("Keep sodium low (<1500mg/day) — hypertension reported.")
    if has("cholesterol", "heart", "cardiac", "atheroscler"):
        # Nudge fat down / carbs up to favor a heart-healthy split.
        shift = round(macros["fat_g"] * 0.15, 1)
        macros["fat_g"] = round(macros["fat_g"] - shift, 1)
        macros["carbs_g"] = round(macros["carbs_g"] + shift * (9 / 4), 1)
        notes.append("Saturated fat was reduced — favor unsaturated fats (heart/cholesterol reported).")
    if has("kidney", "renal"):
        # Cap protein for renal safety and rebalance the calories into carbs.
        if macros["protein_g"] > 0:
            cut = round(macros["protein_g"] * 0.20, 1)
            macros["protein_g"] = round(macros["protein_g"] - cut, 1)
            macros["carbs_g"] = round(macros["carbs_g"] + cut, 1)
        notes.append("Protein was lowered for kidney safety — consult your doctor before high-protein diets.")
    if has("gout", "uric"):
        notes.append("Limit high-purine foods (red meat, shellfish, alcohol) — gout reported.")
    if has("celiac", "gluten"):
        notes.append("Choose gluten-free carbohydrate sources (celiac/gluten sensitivity reported).")
    if has("lactose", "dairy"):
        notes.append("Use lactose-free or plant-based dairy for your protein sources.")
    if has("gerd", "acid reflux", "ulcer"):
        notes.append("Prefer smaller, low-acid, low-spice meals (GERD/reflux reported).")
    if has("ibs", "crohn", "colitis", "ibd"):
        notes.append("Favor gentle, low-FODMAP fiber sources (digestive condition reported).")
    if has("anemia", "iron def"):
        notes.append("Prioritize iron-rich foods with vitamin C to aid absorption (anemia reported).")
    if has("thyroid", "hypothyroid"):
        notes.append("Metabolism may run lower with thyroid conditions — monitor weight trends and adjust.")
    if has("osteoporosis", "osteopenia"):
        notes.append("Ensure adequate calcium and vitamin D (bone-density condition reported).")
    return notes


def get_full_nutrition_plan(
    gender: str,
    age: int,
    weight: float,
    height: float,
    activity_level: str,
    goal: str,
    fitness_level: str,
    conditions: Optional[str] = None,
    allergies: Optional[str] = None,
) -> Dict:
    """Return complete nutrition plan including BMR, TDEE, calorie goal, and macros."""
    bmr = calculate_bmr(gender, weight, height, age)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_goal = calculate_calorie_goal(tdee, goal)
    macros = calculate_macros(calorie_goal, weight, fitness_level, goal)

    notes = _apply_condition_adjustments(macros, conditions)
    if allergies and allergies.strip():
        allergen_list = [a.strip() for a in allergies.split(",") if a.strip()]
        if allergen_list:
            notes.append("Avoid foods containing: " + ", ".join(allergen_list) + ".")

    return {
        "bmr": round(bmr, 0),
        "tdee": round(tdee, 0),
        "calorie_goal": round(calorie_goal, 0),
        "macros": macros,
        "goal": goal,
        "activity_level": activity_level,
        "notes": notes,
    }


def calculate_calories_from_steps(steps: int, weight: float) -> float:
    """Estimate calories burned from steps (formula from documentation)."""
    calories = steps * (0.05 * (weight / 70))
    return round(calories, 2)
