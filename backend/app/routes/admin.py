from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── Role Dependency Helpers ──────────────────────────────────────────────────

def require_admin(current_user: User = Depends(get_current_user)):
    """Allow both admins and super-admins."""
    if not current_user.is_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_super_admin(current_user: User = Depends(get_current_user)):
    """Allow super-admins only."""
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super-admin access required")
    return current_user


def _user_dict(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "username": u.username,
        "is_admin": u.is_admin,
        "is_super_admin": u.is_super_admin,
        "is_active": u.is_active,
        "age": u.age,
        "gender": u.gender,
        "weight": u.weight,
        "height": u.height,
        "fitness_level": u.fitness_level,
        "goal": u.goal,
        "activity_level": u.activity_level,
        "workout_frequency": u.workout_frequency,
        "equipment": u.equipment,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


# ─── User Listing ─────────────────────────────────────────────────────────────

@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).all()
    return [_user_dict(u) for u in users]


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_dict(user)


# ─── User Management (Admin) ──────────────────────────────────────────────────

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Cannot delete a super-admin")
    if user.is_admin and not admin.is_super_admin:
        raise HTTPException(status_code=403, detail="Only a super-admin can delete an admin")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Cannot deactivate a super-admin")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}", "is_active": user.is_active}


# ─── Role Promotion / Demotion (Super-Admin only) ─────────────────────────────

@router.patch("/users/{user_id}/promote-admin")
def promote_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_super_admin),
):
    """Promote a regular user to admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin or user.is_super_admin:
        raise HTTPException(status_code=400, detail="User is already an admin or super-admin")
    user.is_admin = True
    db.commit()
    db.refresh(user)
    return {"message": f"User '{user.username}' promoted to admin", "user": _user_dict(user)}


@router.patch("/users/{user_id}/demote-admin")
def demote_from_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_super_admin),
):
    """Demote an admin back to regular user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Cannot demote a super-admin")
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="User is not an admin")
    user.is_admin = False
    db.commit()
    db.refresh(user)
    return {"message": f"User '{user.username}' demoted to regular user", "user": _user_dict(user)}


@router.patch("/users/{user_id}/promote-super-admin")
def promote_to_super_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_super_admin),
):
    """Promote a user to super-admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_super_admin:
        raise HTTPException(status_code=400, detail="User is already a super-admin")
    user.is_admin = True          # super-admin implies admin
    user.is_super_admin = True
    db.commit()
    db.refresh(user)
    return {"message": f"User '{user.username}' promoted to super-admin", "user": _user_dict(user)}


@router.patch("/users/{user_id}/demote-super-admin")
def demote_from_super_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_super_admin),
):
    """Demote a super-admin to regular admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot demote yourself")
    if not user.is_super_admin:
        raise HTTPException(status_code=400, detail="User is not a super-admin")
    user.is_super_admin = False
    # keep is_admin = True so they stay as regular admin after demotion
    db.commit()
    db.refresh(user)
    return {"message": f"User '{user.username}' demoted to admin", "user": _user_dict(user)}


# ─── ML Model ────────────────────────────────────────────────────────────────

@router.post("/ml/retrain")
def retrain_model(admin: User = Depends(require_admin)):
    """Force retrain the calorie predictor (run after uploading new CSV data)."""
    from app.ml.calorie_predictor import retrain
    result = retrain()
    return result


@router.get("/ml/status")
def ml_status(admin: User = Depends(require_admin)):
    """Check whether the real Kaggle dataset is present."""
    import os
    from app.ml.calorie_predictor import EXERCISE_CSV, CALORIES_CSV, MERGED_CSV, MODEL_PATH
    two_files = os.path.exists(EXERCISE_CSV) and os.path.exists(CALORIES_CSV)
    merged = os.path.exists(MERGED_CSV)
    return {
        "exercise_csv_found": os.path.exists(EXERCISE_CSV),
        "calories_csv_found": os.path.exists(CALORIES_CSV),
        "merged_csv_found": merged,
        "model_trained": os.path.exists(MODEL_PATH),
        "using_real_data": two_files or merged,
    }


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    from app.models.logs import CalorieLog, WorkoutLog, StepLog
    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_active == True).count(),
        "admin_users": db.query(User).filter(User.is_admin == True).count(),
        "super_admin_users": db.query(User).filter(User.is_super_admin == True).count(),
        "total_calorie_logs": db.query(CalorieLog).count(),
        "total_workout_logs": db.query(WorkoutLog).count(),
        "total_step_logs": db.query(StepLog).count(),
    }
