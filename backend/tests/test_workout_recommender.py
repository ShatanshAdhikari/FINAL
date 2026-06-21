import pytest
from app.services.workout_recommender import generate_workout_plan


LEVELS = ["beginner", "intermediate", "advanced"]
GOALS = ["fat_loss", "muscle_gain", "strength", "endurance"]


class TestGenerateWorkoutPlan:
    def test_plan_has_correct_number_of_days(self):
        for freq in [1, 3, 4, 5, 7]:
            plan = generate_workout_plan("beginner", "fat_loss", freq, user_id=1)
            assert len(plan["weekly_plan"]) == freq

    def test_plan_days_are_non_empty(self):
        plan = generate_workout_plan("intermediate", "muscle_gain", 3, user_id=2)
        for day_data in plan["weekly_plan"].values():
            assert len(day_data["exercises"]) > 0

    def test_each_exercise_has_required_keys(self):
        plan = generate_workout_plan("advanced", "strength", 5, user_id=3)
        for day_data in plan["weekly_plan"].values():
            for ex in day_data["exercises"]:
                assert "name" in ex
                assert "sets" in ex
                assert "reps" in ex

    def test_plan_structure_has_meta(self):
        plan = generate_workout_plan("beginner", "endurance", 4, user_id=4)
        assert "goal" in plan
        assert "fitness_level" in plan
        assert "days_per_week" in plan
        assert "weekly_plan" in plan

    def test_all_fitness_levels(self):
        for level in LEVELS:
            plan = generate_workout_plan(level, "muscle_gain", 3, user_id=99)
            assert len(plan["weekly_plan"]) == 3

    def test_all_goals(self):
        for goal in GOALS:
            plan = generate_workout_plan("intermediate", goal, 3, user_id=99)
            assert len(plan["weekly_plan"]) == 3

    def test_same_user_same_week_deterministic(self):
        plan_a = generate_workout_plan("intermediate", "muscle_gain", 4, user_id=7)
        plan_b = generate_workout_plan("intermediate", "muscle_gain", 4, user_id=7)
        assert plan_a == plan_b

    def test_different_users_may_differ(self):
        plan_a = generate_workout_plan("intermediate", "muscle_gain", 4, user_id=10)
        plan_b = generate_workout_plan("intermediate", "muscle_gain", 4, user_id=11)
        # Plans are seeded by user_id — they may or may not differ, but both valid
        assert "weekly_plan" in plan_a and "weekly_plan" in plan_b

    def test_full_body_split_for_low_frequency(self):
        plan = generate_workout_plan("beginner", "fat_loss", 2, user_id=5)
        for day_data in plan["weekly_plan"].values():
            assert day_data["type"] == "Full Body"

    def test_upper_lower_split_for_four_days(self):
        plan = generate_workout_plan("intermediate", "muscle_gain", 4, user_id=6)
        types = {d["type"] for d in plan["weekly_plan"].values()}
        assert "Upper Body" in types
        assert "Lower Body" in types
