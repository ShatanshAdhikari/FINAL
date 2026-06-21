import pytest
from app.services.nutrition_calculator import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_goal,
    calculate_macros,
    calculate_calories_from_steps,
    get_full_nutrition_plan,
)


class TestCalculateBMR:
    def test_male_bmr(self):
        # 70kg, 175cm, 30yo male → 10*70 + 6.25*175 - 5*30 + 5 = 1648.75
        result = calculate_bmr("male", 70, 175, 30)
        assert abs(result - 1648.75) < 0.01

    def test_female_bmr(self):
        # 60kg, 165cm, 25yo female → 10*60 + 6.25*165 - 5*25 - 161 = 1345.25
        result = calculate_bmr("female", 60, 165, 25)
        assert abs(result - 1345.25) < 0.01

    def test_male_higher_than_female_same_stats(self):
        male = calculate_bmr("male", 70, 170, 30)
        female = calculate_bmr("female", 70, 170, 30)
        assert male > female

    def test_bmr_positive(self):
        assert calculate_bmr("male", 50, 160, 20) > 0
        assert calculate_bmr("female", 50, 160, 20) > 0


class TestCalculateTDEE:
    def test_sedentary_multiplier(self):
        assert abs(calculate_tdee(1000, "sedentary") - 1200.0) < 0.01

    def test_very_active_multiplier(self):
        assert abs(calculate_tdee(1000, "very_active") - 1900.0) < 0.01

    def test_unknown_level_defaults_to_sedentary(self):
        assert abs(calculate_tdee(1000, "unknown") - 1200.0) < 0.01

    def test_tdee_greater_than_bmr(self):
        bmr = 1500
        for level in ["sedentary", "light", "moderate", "active", "very_active"]:
            assert calculate_tdee(bmr, level) >= bmr


class TestCalculateCalorieGoal:
    def test_fat_loss_deficit(self):
        assert calculate_calorie_goal(2000, "fat_loss") == 1500.0

    def test_muscle_gain_surplus(self):
        assert calculate_calorie_goal(2000, "muscle_gain") == 2300.0

    def test_strength_no_change(self):
        assert calculate_calorie_goal(2000, "strength") == 2000.0

    def test_endurance_surplus(self):
        assert calculate_calorie_goal(2000, "endurance") == 2150.0


class TestCalculateMacros:
    def test_macros_sum_roughly_to_calories(self):
        macros = calculate_macros(2000, 70, "intermediate", "muscle_gain")
        total = (macros["protein_g"] * 4) + (macros["fat_g"] * 9) + (macros["carbs_g"] * 4)
        assert abs(total - 2000) < 5

    def test_protein_scales_with_weight(self):
        light = calculate_macros(2000, 60, "beginner", "fat_loss")
        heavy = calculate_macros(2000, 90, "beginner", "fat_loss")
        assert heavy["protein_g"] > light["protein_g"]

    def test_advanced_more_protein_than_beginner(self):
        beginner = calculate_macros(2000, 70, "beginner", "muscle_gain")
        advanced = calculate_macros(2000, 70, "advanced", "muscle_gain")
        assert advanced["protein_g"] > beginner["protein_g"]

    def test_returns_required_keys(self):
        macros = calculate_macros(2000, 70, "intermediate", "fat_loss")
        assert all(k in macros for k in ["calories", "protein_g", "fat_g", "carbs_g"])


class TestCalculateCaloriesFromSteps:
    def test_zero_steps(self):
        assert calculate_calories_from_steps(0, 70) == 0.0

    def test_10000_steps_70kg(self):
        # 10000 * 0.05 * (70/70) = 500
        assert abs(calculate_calories_from_steps(10000, 70) - 500.0) < 0.01

    def test_heavier_person_burns_more(self):
        light = calculate_calories_from_steps(5000, 60)
        heavy = calculate_calories_from_steps(5000, 100)
        assert heavy > light


class TestGetFullNutritionPlan:
    def test_full_plan_structure(self):
        plan = get_full_nutrition_plan("male", 30, 75, 175, "moderate", "muscle_gain", "intermediate")
        assert all(k in plan for k in ["bmr", "tdee", "calorie_goal", "macros", "goal", "activity_level"])

    def test_tdee_greater_than_bmr(self):
        plan = get_full_nutrition_plan("female", 25, 60, 165, "active", "fat_loss", "beginner")
        assert plan["tdee"] > plan["bmr"]

    def test_fat_loss_calorie_goal_below_tdee(self):
        plan = get_full_nutrition_plan("male", 35, 80, 180, "moderate", "fat_loss", "intermediate")
        assert plan["calorie_goal"] < plan["tdee"]

    def test_muscle_gain_calorie_goal_above_tdee(self):
        plan = get_full_nutrition_plan("male", 25, 75, 178, "active", "muscle_gain", "advanced")
        assert plan["calorie_goal"] > plan["tdee"]
