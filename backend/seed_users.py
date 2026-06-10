"""
Seed the database with:
  • 1 Super-Admin
  • 2 Admins
  • 5 Regular Users  (with full profile data)

Run from the backend/ directory:
    python seed_users.py

Use --reset to wipe existing users before seeding:
    python seed_users.py --reset
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
import app.models  # register all models

# ─── Seed Data ────────────────────────────────────────────────────────────────

SUPER_ADMIN = {
    "email": "superadmin@getfit.com",
    "username": "superadmin",
    "password": "SuperAdmin@123",
    "is_admin": True,
    "is_super_admin": True,
}

ADMINS = [
    {
        "email": "admin1@getfit.com",
        "username": "admin_alex",
        "password": "Admin@1234",
        "is_admin": True,
        "is_super_admin": False,
    },
    {
        "email": "admin2@getfit.com",
        "username": "admin_sara",
        "password": "Admin@1234",
        "is_admin": True,
        "is_super_admin": False,
    },
]

REGULAR_USERS = [
    {
        "email": "john.doe@example.com",
        "username": "john_doe",
        "password": "User@1234",
        "age": 28,
        "gender": "male",
        "weight": 80.0,
        "height": 178.0,
        "fitness_level": "beginner",
        "goal": "fat_loss",
        "activity_level": "moderate",
        "workout_frequency": 3,
        "equipment": "dumbbells,resistance_bands",
    },
    {
        "email": "jane.smith@example.com",
        "username": "jane_smith",
        "password": "User@1234",
        "age": 24,
        "gender": "female",
        "weight": 60.0,
        "height": 165.0,
        "fitness_level": "intermediate",
        "goal": "muscle_gain",
        "activity_level": "active",
        "workout_frequency": 4,
        "equipment": "barbell,dumbbells,pull_up_bar",
    },
    {
        "email": "mike.chen@example.com",
        "username": "mike_chen",
        "password": "User@1234",
        "age": 32,
        "gender": "male",
        "weight": 75.0,
        "height": 175.0,
        "fitness_level": "advanced",
        "goal": "endurance",
        "activity_level": "very_active",
        "workout_frequency": 6,
        "equipment": "treadmill,dumbbells",
    },
    {
        "email": "priya.patel@example.com",
        "username": "priya_patel",
        "password": "User@1234",
        "age": 27,
        "gender": "female",
        "weight": 55.0,
        "height": 160.0,
        "fitness_level": "beginner",
        "goal": "fat_loss",
        "activity_level": "light",
        "workout_frequency": 2,
        "equipment": "yoga_mat,resistance_bands",
    },
    {
        "email": "carlos.garcia@example.com",
        "username": "carlos_garcia",
        "password": "User@1234",
        "age": 35,
        "gender": "male",
        "weight": 90.0,
        "height": 182.0,
        "fitness_level": "intermediate",
        "goal": "strength",
        "activity_level": "active",
        "workout_frequency": 5,
        "equipment": "barbell,bench,cable_machine",
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _role(u: User) -> str:
    if u.is_super_admin:
        return "SUPER-ADMIN"
    if u.is_admin:
        return "ADMIN"
    return "user"


def _upsert(db, data: dict) -> tuple[User, bool]:
    """Create user if not exists; return (user, created)."""
    existing = db.query(User).filter(
        (User.email == data["email"]) | (User.username == data["username"])
    ).first()
    if existing:
        return existing, False

    user_fields = {k: v for k, v in data.items() if k != "password"}
    user = User(
        **user_fields,
        hashed_password=get_password_hash(data["password"]),
    )
    db.add(user)
    db.flush()   # get id without full commit yet
    return user, True


# ─── Main ─────────────────────────────────────────────────────────────────────

def _migrate(engine):
    """Add missing columns to existing DB without a full migration framework."""
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    with engine.connect() as conn:
        if "is_super_admin" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0 NOT NULL"))
            conn.commit()
            print("[migrate] Added column: users.is_super_admin")


def seed():
    Base.metadata.create_all(bind=engine)
    _migrate(engine)
    db = SessionLocal()
    created_count = 0
    skipped_count = 0

    try:
        if "--reset" in sys.argv:
            confirm = input(
                "[!] This will DELETE all users. Type 'yes' to confirm: "
            ).strip()
            if confirm != "yes":
                print("Aborted.")
                return
            db.query(User).delete()
            db.commit()
            print("[!] All users deleted.\n")

        print("\n" + "=" * 55)
        print("  GetFit — User Seeder")
        print("=" * 55)

        # ── Super-Admin ──
        print("\n[*] Super-Admin")
        user, created = _upsert(db, SUPER_ADMIN)
        tag = "[OK] Created" if created else "[--] Already exists"
        if created:
            created_count += 1
        else:
            skipped_count += 1
        print(f"   {tag}: [{_role(user) if not created else 'SUPER-ADMIN'}] "
              f"{SUPER_ADMIN['username']} ({SUPER_ADMIN['email']})")
        if created:
            print(f"   Password : {SUPER_ADMIN['password']}")

        # ── Admins ──
        print("\n[*] Admins")
        for data in ADMINS:
            user, created = _upsert(db, data)
            tag = "[OK] Created" if created else "[--] Already exists"
            if created:
                created_count += 1
            else:
                skipped_count += 1
            print(f"   {tag}: [{_role(user) if not created else 'ADMIN'}] "
                  f"{data['username']} ({data['email']})")
            if created:
                print(f"   Password : {data['password']}")

        # ── Regular Users ──
        print("\n[*] Regular Users")
        for data in REGULAR_USERS:
            user, created = _upsert(db, data)
            tag = "[OK] Created" if created else "[--] Already exists"
            if created:
                created_count += 1
            else:
                skipped_count += 1
            print(f"   {tag}: [user] {data['username']} ({data['email']})")
            if created:
                print(f"   Password : {data['password']}")

        db.commit()

        print("\n" + "=" * 55)
        print(f"  Done — {created_count} created, {skipped_count} skipped")
        print("=" * 55 + "\n")

        if created_count > 0:
            print("Credentials summary:")
            print(f"   Super-Admin  -> {SUPER_ADMIN['email']} / {SUPER_ADMIN['password']}")
            for d in ADMINS:
                print(f"   Admin        -> {d['email']} / {d['password']}")
            for d in REGULAR_USERS:
                print(f"   User         -> {d['email']} / {d['password']}")
            print()

    except KeyboardInterrupt:
        db.rollback()
        print("\nAborted — no changes saved.")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed()
