from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CalorieLog(Base):
    __tablename__ = "calorie_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    meal_type = Column(String, default="snack")  # breakfast/lunch/dinner/snack
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calorie_logs")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    heart_rate = Column(Float, nullable=True)
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_logs")


class StepLog(Base):
    __tablename__ = "step_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    steps = Column(Integer, nullable=False)
    calories_from_steps = Column(Float, nullable=True)
    date = Column(String, nullable=False)  # YYYY-MM-DD

    user = relationship("User", back_populates="step_logs")
