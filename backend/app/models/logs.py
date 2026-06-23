from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class CalorieLog(Base):
    __tablename__ = "calorie_logs"
    __table_args__ = (
        Index("ix_calorie_logs_user_id", "user_id"),
        Index("ix_calorie_logs_logged_at", "logged_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    food_name: Mapped[str] = mapped_column(String, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[Optional[float]] = mapped_column(Float, default=0)
    carbs: Mapped[Optional[float]] = mapped_column(Float, default=0)
    fat: Mapped[Optional[float]] = mapped_column(Float, default=0)
    meal_type: Mapped[Optional[str]] = mapped_column(String, default="snack")
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship("User", back_populates="calorie_logs")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    __table_args__ = (
        Index("ix_workout_logs_user_id", "user_id"),
        Index("ix_workout_logs_logged_at", "logged_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    heart_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship("User", back_populates="workout_logs")


class StepLog(Base):
    __tablename__ = "step_logs"
    __table_args__ = (
        Index("ix_step_logs_user_id", "user_id"),
        Index("ix_step_logs_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    steps: Mapped[int] = mapped_column(Integer, nullable=False)
    calories_from_steps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    date: Mapped[str] = mapped_column(String, nullable=False)  # YYYY-MM-DD

    user: Mapped[User] = relationship("User", back_populates="step_logs")


class WeightLog(Base):
    __tablename__ = "weight_logs"
    __table_args__ = (
        Index("ix_weight_logs_user_id", "user_id"),
        Index("ix_weight_logs_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # kg
    date: Mapped[str] = mapped_column(String, nullable=False)     # YYYY-MM-DD
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship("User", back_populates="weight_logs")
