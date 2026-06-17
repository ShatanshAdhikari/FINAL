from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Boolean, DateTime
from datetime import datetime, timezone
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.logs import CalorieLog, WorkoutLog, StepLog, WeightLog


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Profile data
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)       # kg
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)       # cm
    fitness_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    goal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    activity_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workout_frequency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # days per week
    equipment: Mapped[Optional[str]] = mapped_column(String, nullable=True)     # comma-separated

    # Relationships
    calorie_logs: Mapped[List["CalorieLog"]] = relationship("CalorieLog", back_populates="user", cascade="all, delete")
    workout_logs: Mapped[List["WorkoutLog"]] = relationship("WorkoutLog", back_populates="user", cascade="all, delete")
    step_logs: Mapped[List["StepLog"]] = relationship("StepLog", back_populates="user", cascade="all, delete")
    weight_logs: Mapped[List["WeightLog"]] = relationship("WeightLog", back_populates="user", cascade="all, delete")
