"""
Create or manage admin / super-admin users.
Run from the backend/ directory:

  python create_admin.py                         # interactive — create admin
  python create_admin.py --super                 # interactive — create super-admin
  python create_admin.py --promote <username>    # promote existing user → admin
  python create_admin.py --promote-super <username>  # promote existing user → super-admin
  python create_admin.py --list                  # list all privileged users
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
import app.models  # register all models


def _role_label(u: User) -> str:
    if u.is_super_admin:
        return "super-admin"
    if u.is_admin:
        return "admin"
    return "user"


def list_privileged(db):
    users = db.query(User).filter(
        (User.is_admin == True) | (User.is_super_admin == True)
    ).all()
    if not users:
        print("No admin or super-admin accounts found.")
        return
    print(f"\n{'ID':<5} {'Username':<20} {'Email':<35} {'Role':<12} {'Active'}")
    print("-" * 80)
    for u in users:
        active = "✓" if u.is_active else "✗"
        print(f"{u.id:<5} {u.username:<20} {u.email:<35} {_role_label(u):<12} {active}")
    print()


def create_privileged_user(db, is_super_admin: bool = False):
    role = "super-admin" if is_super_admin else "admin"
    print(f"\n=== GetFit {role.title()} Setup ===\n")

    email = input(f"{role.title()} email: ").strip()
    username = input(f"{role.title()} username: ").strip()
    password = input(f"{role.title()} password: ").strip()

    if not email or not username or not password:
        print("❌ All fields are required.")
        return

    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing:
        promote = input(
            f"User '{existing.username}' already exists. Promote to {role}? [y/N] "
        ).strip().lower()
        if promote == "y":
            existing.is_admin = True
            if is_super_admin:
                existing.is_super_admin = True
            db.commit()
            print(f"✅ User '{existing.username}' is now a {role}!")
        else:
            print("Aborted.")
        return

    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        is_admin=True,
        is_super_admin=is_super_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"\n✅ {role.title()} '{username}' created successfully!")
    print(f"   Email   : {email}")
    print(f"   ID      : {user.id}")
    print(f"   Role    : {_role_label(user)}")
    print(f"\nYou can now log in at http://localhost:5173/login\n")


def promote_user(db, username: str, to_super_admin: bool = False):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found.")
        return
    user.is_admin = True
    if to_super_admin:
        user.is_super_admin = True
    db.commit()
    role = "super-admin" if to_super_admin else "admin"
    print(f"✅ User '{username}' is now a {role}!")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        args = sys.argv[1:]

        if not args:
            create_privileged_user(db, is_super_admin=False)

        elif args[0] == "--super":
            create_privileged_user(db, is_super_admin=True)

        elif args[0] == "--promote" and len(args) >= 2:
            promote_user(db, args[1], to_super_admin=False)

        elif args[0] == "--promote-super" and len(args) >= 2:
            promote_user(db, args[1], to_super_admin=True)

        elif args[0] == "--list":
            list_privileged(db)

        else:
            print(__doc__)

    except KeyboardInterrupt:
        print("\nAborted.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
