from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class GoalEnum(str, enum.Enum):
    fat_loss = "fat_loss"
    muscle_gain = "muscle_gain"
    endurance = "endurance"
    strength = "strength"


class FitnessLevelEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class ActivityLevelEnum(str, enum.Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile data
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    weight = Column(Float, nullable=True)   # kg
    height = Column(Float, nullable=True)   # cm
    fitness_level = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    workout_frequency = Column(Integer, nullable=True)  # days per week
    equipment = Column(String, nullable=True)  # comma-separated list

    # Relationships
    calorie_logs = relationship("CalorieLog", back_populates="user", cascade="all, delete")
    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete")
    step_logs = relationship("StepLog", back_populates="user", cascade="all, delete")
