"""
Seed ~14 days of realistic activity (meals, weight, steps, workouts) for one
demo user so the dashboard charts and the PDF progress report look rich.

Idempotent: wipes the target user's existing logs first, then reinserts.
Dates are relative to datetime.now(UTC) so they line up with the app's
"today" / history windows on whatever server runs it.

Usage (against Neon):
    DATABASE_URL=postgresql://... SECRET_KEY=... \
        python seed_demo_activity.py [email]
Defaults to maria@gmail.com.
"""
import sys
from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.models.user import User
from app.models.logs import CalorieLog, WeightLog, StepLog, WorkoutLog

TARGET_EMAIL = sys.argv[1] if len(sys.argv) > 1 else "maria@gmail.com"
DAYS = 14

# A day's meals: (food, meal_type, kcal, protein, carbs, fat). ~1290 kcal/day.
MEAL_PLANS = [
    [("Greek yogurt & berries", "breakfast", 240, 18, 30, 5),
     ("Grilled chicken salad", "lunch", 420, 42, 22, 16),
     ("Salmon, rice & broccoli", "dinner", 520, 38, 48, 20),
     ("Almonds", "snack", 110, 4, 4, 9)],
    [("Oats with banana", "breakfast", 300, 10, 55, 6),
     ("Turkey wrap", "lunch", 400, 32, 40, 12),
     ("Tofu stir-fry", "dinner", 460, 26, 50, 18),
     ("Apple", "snack", 95, 0, 25, 0)],
    [("Egg-white omelette", "breakfast", 220, 24, 6, 10),
     ("Quinoa bowl", "lunch", 450, 20, 60, 14),
     ("Lean beef & sweet potato", "dinner", 540, 40, 45, 20),
     ("Protein shake", "snack", 130, 25, 5, 2)],
]


def main():
    db = SessionLocal()
    user = db.query(User).filter(User.email == TARGET_EMAIL).first()
    if not user:
        print(f"[!] user {TARGET_EMAIL} not found")
        return
    uid = user.id

    # wipe existing logs for a clean, idempotent reseed
    for model in (CalorieLog, WeightLog, StepLog, WorkoutLog):
        db.query(model).filter(model.user_id == uid).delete(synchronize_session=False)
    db.commit()

    now = datetime.now(timezone.utc)
    today = now.date()
    start_weight = 60.4  # trends down to ~58.0 over the window

    cal_rows = step_rows = weight_rows = workout_rows = 0

    for d in range(DAYS - 1, -1, -1):          # oldest → today
        day_date = today - timedelta(days=d)
        midnight = datetime(day_date.year, day_date.month, day_date.day, tzinfo=timezone.utc)
        plan = MEAL_PLANS[(DAYS - 1 - d) % len(MEAL_PLANS)]

        # meals — spread across the day
        for hour, (food, meal, kcal, p, c, f) in zip((8, 13, 19, 16), plan):
            db.add(CalorieLog(
                user_id=uid, food_name=food, calories=float(kcal),
                protein=float(p), carbs=float(c), fat=float(f),
                meal_type=meal, logged_at=midnight + timedelta(hours=hour),
            ))
            cal_rows += 1

        # weight — steady downward trend with tiny wobble
        w = round(start_weight - (DAYS - 1 - d) * 0.17 + (0.15 if d % 3 == 0 else 0.0), 1)
        db.add(WeightLog(user_id=uid, weight=w, date=day_date.isoformat(),
                         logged_at=midnight + timedelta(hours=7)))
        weight_rows += 1

        # steps — 6.5k–11k, calories ~0.045/step
        steps = 6500 + (d * 317) % 4500
        db.add(StepLog(user_id=uid, steps=steps,
                       calories_from_steps=round(steps * 0.045, 1),
                       date=day_date.isoformat()))
        step_rows += 1

        # workout every other day
        if d % 2 == 0:
            db.add(WorkoutLog(
                user_id=uid, exercise_name="Full-body strength",
                duration_minutes=45.0, sets=4, reps=12, heart_rate=132.0,
                calories_burned=310.0, notes="demo",
                logged_at=midnight + timedelta(hours=18),
            ))
            workout_rows += 1

    db.commit()
    print(f"[ok] seeded for {TARGET_EMAIL} (id {uid}) over {DAYS} days:")
    print(f"     {cal_rows} meals, {weight_rows} weigh-ins, {step_rows} step-days, {workout_rows} workouts")
    # quick summary
    latest = db.query(WeightLog).filter(WeightLog.user_id == uid).order_by(WeightLog.date).all()
    print(f"     weight {latest[0].weight}kg → {latest[-1].weight}kg")


if __name__ == "__main__":
    main()
