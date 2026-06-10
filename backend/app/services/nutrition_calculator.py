"""
Nutrition Calculator - BMR, TDEE, and Macronutrient Distribution
Based on Mifflin-St Jeor equation as described in the GetFit documentation (Section 3.2.4)
"""
from typing import Dict


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


def get_full_nutrition_plan(
    gender: str,
    age: int,
    weight: float,
    height: float,
    activity_level: str,
    goal: str,
    fitness_level: str,
) -> Dict:
    """Return complete nutrition plan including BMR, TDEE, calorie goal, and macros."""
    bmr = calculate_bmr(gender, weight, height, age)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_goal = calculate_calorie_goal(tdee, goal)
    macros = calculate_macros(calorie_goal, weight, fitness_level, goal)

    return {
        "bmr": round(bmr, 0),
        "tdee": round(tdee, 0),
        "calorie_goal": round(calorie_goal, 0),
        "macros": macros,
        "goal": goal,
        "activity_level": activity_level,
    }


def calculate_calories_from_steps(steps: int, weight: float) -> float:
    """Estimate calories burned from steps (formula from documentation)."""
    calories = steps * (0.05 * (weight / 70))
    return round(calories, 2)
