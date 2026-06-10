"""
Calorie Burn Predictor using Lasso Regression (Polynomial Degree 3)
Based on: heart rate, duration, age, weight, height, gender
As described in the GetFit project documentation.
"""
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "calorie_model.pkl")


def _generate_synthetic_training_data(n=1000):
    """
    Generate synthetic training data based on physiological relationships.
    In production, replace with the actual Kaggle dataset.
    """
    np.random.seed(42)
    gender = np.random.randint(0, 2, n)          # 0=female, 1=male
    age = np.random.randint(18, 65, n)
    height = np.random.uniform(150, 195, n)       # cm
    weight = np.random.uniform(45, 120, n)        # kg
    duration = np.random.uniform(5, 60, n)        # minutes
    heart_rate = np.random.uniform(60, 180, n)    # BPM
    body_temp = np.random.uniform(36.0, 41.0, n)  # Celsius

    # Approximate physiological formula for calories burned
    calories = (
        0.014 * heart_rate * duration
        + 0.012 * weight * duration
        + 0.001 * age * duration
        + 0.5 * gender * duration
        + 0.3 * (body_temp - 37) * duration
        + np.random.normal(0, 5, n)
    )
    calories = np.clip(calories, 5, 800)

    X = np.column_stack([gender, age, height, weight, duration, heart_rate, body_temp])
    return X, calories


def train_model():
    """Train and save the Lasso regression model with polynomial features (degree 3)."""
    X, y = _generate_synthetic_training_data()

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("poly", PolynomialFeatures(degree=3, include_bias=False)),
        ("lasso", Lasso(alpha=0.01, max_iter=10000)),
    ])

    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")
    return model


def load_model():
    """Load the model, training it first if it doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        return train_model()
    return joblib.load(MODEL_PATH)


# Lazy-load the model
_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def predict_calories(
    gender: str,       # "male" or "female"
    age: int,
    height: float,     # cm
    weight: float,     # kg
    duration: float,   # minutes
    heart_rate: float, # BPM
    body_temp: float = 37.5,  # Celsius (optional, default avg)
) -> float:
    """Predict calories burned during a workout session."""
    model = get_model()
    gender_encoded = 1 if gender.lower() == "male" else 0
    X = np.array([[gender_encoded, age, height, weight, duration, heart_rate, body_temp]])
    prediction = model.predict(X)[0]
    return round(max(float(prediction), 1.0), 2)
