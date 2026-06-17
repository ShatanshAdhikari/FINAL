from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class CalorieLog(Base):
    __tablename__ = "calorie_logs"

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    heart_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship("User", back_populates="workout_logs")


class StepLog(Base):
    __tablename__ = "step_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    steps: Mapped[int] = mapped_column(Integer, nullable=False)
    calories_from_steps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    date: Mapped[str] = mapped_column(String, nullable=False)  # YYYY-MM-DD

    user: Mapped[User] = relationship("User", back_populates="step_logs")


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # kg
    date: Mapped[str] = mapped_column(String, nullable=False)     # YYYY-MM-DD
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship("User", back_populates="weight_logs")
