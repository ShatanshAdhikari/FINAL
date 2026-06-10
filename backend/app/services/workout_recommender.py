"""
Rule-Based Workout Recommender System
As described in the GetFit project documentation (Section 3.2.2)
"""
import random
from typing import List, Dict, Any

# Exercise database organized by type and difficulty
EXERCISE_DATABASE = {
    "push": {
        "beginner": [
            {"name": "Push-Ups", "muscles": "Chest, Triceps, Shoulders", "equipment": "none"},
            {"name": "Incline Push-Ups", "muscles": "Upper Chest, Triceps", "equipment": "none"},
            {"name": "Dumbbell Chest Press", "muscles": "Chest, Triceps", "equipment": "dumbbells"},
            {"name": "Shoulder Press (Dumbbells)", "muscles": "Shoulders, Triceps", "equipment": "dumbbells"},
            {"name": "Lateral Raises", "muscles": "Shoulders", "equipment": "dumbbells"},
            {"name": "Tricep Dips", "muscles": "Triceps", "equipment": "none"},
        ],
        "intermediate": [
            {"name": "Bench Press", "muscles": "Chest, Triceps", "equipment": "barbell"},
            {"name": "Overhead Press", "muscles": "Shoulders, Triceps", "equipment": "barbell"},
            {"name": "Diamond Push-Ups", "muscles": "Triceps, Chest", "equipment": "none"},
            {"name": "Arnold Press", "muscles": "Shoulders", "equipment": "dumbbells"},
            {"name": "Cable Flyes", "muscles": "Chest", "equipment": "cable"},
            {"name": "Skull Crushers", "muscles": "Triceps", "equipment": "barbell"},
        ],
        "advanced": [
            {"name": "Weighted Bench Press", "muscles": "Chest, Triceps", "equipment": "barbell"},
            {"name": "Incline Barbell Press", "muscles": "Upper Chest", "equipment": "barbell"},
            {"name": "Dips (Weighted)", "muscles": "Triceps, Chest", "equipment": "none"},
            {"name": "Pike Push-Ups", "muscles": "Shoulders", "equipment": "none"},
        ],
    },
    "pull": {
        "beginner": [
            {"name": "Dumbbell Rows", "muscles": "Back, Biceps", "equipment": "dumbbells"},
            {"name": "Band Pull-Aparts", "muscles": "Upper Back", "equipment": "resistance_band"},
            {"name": "Bicep Curls", "muscles": "Biceps", "equipment": "dumbbells"},
            {"name": "Hammer Curls", "muscles": "Biceps, Forearms", "equipment": "dumbbells"},
            {"name": "Face Pulls", "muscles": "Rear Delts, Upper Back", "equipment": "resistance_band"},
        ],
        "intermediate": [
            {"name": "Pull-Ups", "muscles": "Back, Biceps", "equipment": "pullup_bar"},
            {"name": "Barbell Rows", "muscles": "Back, Biceps", "equipment": "barbell"},
            {"name": "Lat Pulldown", "muscles": "Lats", "equipment": "cable"},
            {"name": "Seated Cable Row", "muscles": "Mid Back", "equipment": "cable"},
            {"name": "Preacher Curls", "muscles": "Biceps", "equipment": "barbell"},
        ],
        "advanced": [
            {"name": "Weighted Pull-Ups", "muscles": "Back, Biceps", "equipment": "pullup_bar"},
            {"name": "T-Bar Row", "muscles": "Back", "equipment": "barbell"},
            {"name": "Single-Arm Dumbbell Row", "muscles": "Back", "equipment": "dumbbells"},
            {"name": "Rack Pulls", "muscles": "Back, Traps", "equipment": "barbell"},
        ],
    },
    "legs": {
        "beginner": [
            {"name": "Bodyweight Squats", "muscles": "Quads, Glutes", "equipment": "none"},
            {"name": "Lunges", "muscles": "Quads, Glutes, Hamstrings", "equipment": "none"},
            {"name": "Glute Bridges", "muscles": "Glutes, Hamstrings", "equipment": "none"},
            {"name": "Calf Raises", "muscles": "Calves", "equipment": "none"},
            {"name": "Step-Ups", "muscles": "Quads, Glutes", "equipment": "none"},
        ],
        "intermediate": [
            {"name": "Goblet Squat", "muscles": "Quads, Glutes", "equipment": "dumbbells"},
            {"name": "Romanian Deadlift", "muscles": "Hamstrings, Glutes", "equipment": "dumbbells"},
            {"name": "Leg Press", "muscles": "Quads, Glutes", "equipment": "machine"},
            {"name": "Walking Lunges", "muscles": "Quads, Glutes", "equipment": "dumbbells"},
            {"name": "Bulgarian Split Squat", "muscles": "Quads, Glutes", "equipment": "none"},
        ],
        "advanced": [
            {"name": "Barbell Back Squat", "muscles": "Quads, Glutes, Core", "equipment": "barbell"},
            {"name": "Deadlift", "muscles": "Hamstrings, Glutes, Back", "equipment": "barbell"},
            {"name": "Front Squat", "muscles": "Quads, Core", "equipment": "barbell"},
            {"name": "Hip Thrust (Barbell)", "muscles": "Glutes", "equipment": "barbell"},
        ],
    },
    "cardio": {
        "beginner": [
            {"name": "Brisk Walking", "muscles": "Full Body", "equipment": "none"},
            {"name": "Jumping Jacks", "muscles": "Full Body", "equipment": "none"},
            {"name": "March in Place", "muscles": "Full Body", "equipment": "none"},
        ],
        "intermediate": [
            {"name": "Jogging (20 min)", "muscles": "Full Body", "equipment": "none"},
            {"name": "Jump Rope", "muscles": "Full Body", "equipment": "jump_rope"},
            {"name": "Cycling (30 min)", "muscles": "Legs, Cardio", "equipment": "none"},
            {"name": "High Knees", "muscles": "Full Body", "equipment": "none"},
        ],
        "advanced": [
            {"name": "Running (30 min)", "muscles": "Full Body", "equipment": "none"},
            {"name": "HIIT Circuit", "muscles": "Full Body", "equipment": "none"},
            {"name": "Stair Climbing", "muscles": "Legs, Cardio", "equipment": "none"},
        ],
    },
    "core": {
        "beginner": [
            {"name": "Plank (30s)", "muscles": "Core", "equipment": "none"},
            {"name": "Crunches", "muscles": "Abs", "equipment": "none"},
            {"name": "Dead Bug", "muscles": "Core", "equipment": "none"},
        ],
        "intermediate": [
            {"name": "Plank (60s)", "muscles": "Core", "equipment": "none"},
            {"name": "Bicycle Crunches", "muscles": "Abs, Obliques", "equipment": "none"},
            {"name": "Russian Twists", "muscles": "Obliques", "equipment": "none"},
            {"name": "Mountain Climbers", "muscles": "Core, Cardio", "equipment": "none"},
        ],
        "advanced": [
            {"name": "Dragon Flag", "muscles": "Core", "equipment": "none"},
            {"name": "Hanging Leg Raises", "muscles": "Lower Abs", "equipment": "pullup_bar"},
            {"name": "Ab Wheel Rollout", "muscles": "Core", "equipment": "ab_wheel"},
        ],
    },
}


def _get_sets_reps_rest(goal: str, fitness_level: str) -> Dict:
    """Return sets/reps/rest based on goal and fitness level."""
    configs = {
        "fat_loss": {
            "beginner":     {"sets": 3, "reps": "12-15", "rest": "45s", "intensity": "Moderate"},
            "intermediate": {"sets": 4, "reps": "12-15", "rest": "30s", "intensity": "Moderate-High"},
            "advanced":     {"sets": 4, "reps": "15-20", "rest": "20s", "intensity": "High"},
        },
        "muscle_gain": {
            "beginner":     {"sets": 3, "reps": "8-12", "rest": "90s", "intensity": "Moderate"},
            "intermediate": {"sets": 4, "reps": "8-12", "rest": "75s", "intensity": "Moderate-High"},
            "advanced":     {"sets": 5, "reps": "6-10", "rest": "60s", "intensity": "High"},
        },
        "strength": {
            "beginner":     {"sets": 3, "reps": "5-8",  "rest": "2min", "intensity": "Moderate-High"},
            "intermediate": {"sets": 4, "reps": "3-6",  "rest": "2-3min", "intensity": "High"},
            "advanced":     {"sets": 5, "reps": "1-5",  "rest": "3-5min", "intensity": "Max"},
        },
        "endurance": {
            "beginner":     {"sets": 2, "reps": "15-20", "rest": "30s", "intensity": "Low-Moderate"},
            "intermediate": {"sets": 3, "reps": "15-20", "rest": "20s", "intensity": "Moderate"},
            "advanced":     {"sets": 4, "reps": "20-25", "rest": "15s", "intensity": "Moderate-High"},
        },
    }
    goal_key = goal.lower().replace(" ", "_")
    level_key = fitness_level.lower()
    return configs.get(goal_key, configs["muscle_gain"]).get(level_key, configs["muscle_gain"]["beginner"])


def _get_exercises_for_type(workout_type: str, fitness_level: str, count: int = 4) -> List[Dict]:
    """Get exercises for a given workout type and fitness level."""
    level = fitness_level.lower()
    pool = []

    if level == "beginner":
        pool = EXERCISE_DATABASE.get(workout_type, {}).get("beginner", [])
    elif level == "intermediate":
        pool = (EXERCISE_DATABASE.get(workout_type, {}).get("beginner", []) +
                EXERCISE_DATABASE.get(workout_type, {}).get("intermediate", []))
    else:  # advanced
        pool = (EXERCISE_DATABASE.get(workout_type, {}).get("intermediate", []) +
                EXERCISE_DATABASE.get(workout_type, {}).get("advanced", []))

    if not pool:
        pool = EXERCISE_DATABASE.get(workout_type, {}).get("beginner", [])

    return random.sample(pool, min(count, len(pool)))


def generate_workout_plan(
    fitness_level: str,
    goal: str,
    workout_frequency: int,
    age: int = 25,
    gender: str = "male",
) -> Dict[str, Any]:
    """
    Generate a personalized weekly workout plan.

    Args:
        fitness_level: beginner / intermediate / advanced
        goal: fat_loss / muscle_gain / strength / endurance
        workout_frequency: days per week (1-7)
        age: user age
        gender: male / female

    Returns:
        Dict with weekly workout plan
    """
    random.seed(42)  # consistent recommendations
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    workout_days = days[:workout_frequency]

    plan = {}
    config = _get_sets_reps_rest(goal, fitness_level)

    if workout_frequency <= 3:
        # Full body workouts
        for day in workout_days:
            exercises = []
            for wtype in ["push", "pull", "legs", "core"]:
                exs = _get_exercises_for_type(wtype, fitness_level, count=2)
                for ex in exs:
                    exercises.append({**ex, **config})
            plan[day] = {"type": "Full Body", "exercises": exercises}

    elif workout_frequency == 4:
        # Upper / Lower split
        splits = ["upper", "lower", "upper", "lower"]
        for day, split in zip(workout_days, splits):
            exercises = []
            if split == "upper":
                for wtype in ["push", "pull"]:
                    exs = _get_exercises_for_type(wtype, fitness_level, count=3)
                    for ex in exs:
                        exercises.append({**ex, **config})
                exs = _get_exercises_for_type("core", fitness_level, count=2)
                for ex in exs:
                    exercises.append({**ex, **config})
                plan[day] = {"type": "Upper Body", "exercises": exercises}
            else:
                exs = _get_exercises_for_type("legs", fitness_level, count=5)
                for ex in exs:
                    exercises.append({**ex, **config})
                exs = _get_exercises_for_type("core", fitness_level, count=2)
                for ex in exs:
                    exercises.append({**ex, **config})
                plan[day] = {"type": "Lower Body", "exercises": exercises}

    else:
        # Push / Pull / Legs split (5-7 days)
        split_cycle = ["push", "pull", "legs", "push", "pull", "legs", "core"]
        for day, split in zip(workout_days, split_cycle[:workout_frequency]):
            exercises = []
            if split == "core":
                exs = _get_exercises_for_type("core", fitness_level, count=5)
                for ex in exs:
                    exercises.append({**ex, **config})
                exs = _get_exercises_for_type("cardio", fitness_level, count=2)
                for ex in exs:
                    exercises.append({**ex, **config})
                plan[day] = {"type": "Core & Cardio", "exercises": exercises}
            else:
                exs = _get_exercises_for_type(split, fitness_level, count=5)
                for ex in exs:
                    exercises.append({**ex, **config})
                exs = _get_exercises_for_type("core", fitness_level, count=2)
                for ex in exs:
                    exercises.append({**ex, **config})
                plan[day] = {"type": split.capitalize(), "exercises": exercises}

    return {
        "goal": goal,
        "fitness_level": fitness_level,
        "days_per_week": workout_frequency,
        "weekly_plan": plan,
    }
