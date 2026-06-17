"""
Calorie Burn Predictor using Lasso Regression (Polynomial Degree 3)
Features: Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp -> Calories

Real dataset (preferred) — two supported layouts:

  Layout A — two separate files (most common):
      backend/app/ml/data/exercise.csv   (User_ID, Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp)
      backend/app/ml/data/calories.csv   (User_ID, Calories)
      Merged on User_ID automatically.

  Layout B — single merged file:
      backend/app/ml/data/calories_data.csv  (all columns in one file)

  Source: search Kaggle for "Calories Burnt Prediction" and look for a dataset
  with ~15 000 rows and the column names listed above.
  A known upload is by aadhavvignesh ("Calories Burned During Exercise and Activities").

If no files are present the model falls back to synthetic data with a printed warning.
"""
import os
import warnings
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
import joblib

_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(_DIR, "calorie_model.pkl")
DATA_DIR = os.path.join(_DIR, "data")
EXERCISE_CSV = os.path.join(DATA_DIR, "exercise.csv")
CALORIES_CSV = os.path.join(DATA_DIR, "calories.csv")
MERGED_CSV   = os.path.join(DATA_DIR, "calories_data.csv")


# Column name aliases — handles different uploads of the same dataset
_COL_ALIASES = {
    "Gender":     ["Gender", "gender", "Sex", "sex"],
    "Age":        ["Age", "age"],
    "Height":     ["Height", "height"],
    "Weight":     ["Weight", "weight"],
    "Duration":   ["Duration", "duration"],
    "Heart_Rate": ["Heart_Rate", "Heart Rate", "heart_rate", "HeartRate"],
    "Body_Temp":  ["Body_Temp", "Body_Temperature", "body_temp", "BodyTemp"],
    "Calories":   ["Calories", "calories", "Calorie"],
    "User_ID":    ["User_ID", "User_Id", "user_id", "ID"],
}


def _resolve_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names using aliases."""
    rename = {}
    for canonical, aliases in _COL_ALIASES.items():
        for alias in aliases:
            if alias in df.columns and alias != canonical:
                rename[alias] = canonical
                break
    return df.rename(columns=rename)


def _load_real_data():
    """Load real data — supports a single merged CSV or two separate files."""
    FEATURE_COLS = {"Gender", "Age", "Height", "Weight", "Duration", "Heart_Rate", "Body_Temp", "Calories"}

    def _is_merged(path: str) -> bool:
        """Return True if the CSV already contains all required feature columns."""
        try:
            header = pd.read_csv(path, nrows=0)
            resolved = _resolve_columns(header)
            return FEATURE_COLS.issubset(set(resolved.columns))
        except Exception:
            return False

    # Priority: explicit merged file → calories.csv if it contains all columns → two-file merge
    if os.path.exists(MERGED_CSV):
        df = pd.read_csv(MERGED_CSV)
    elif os.path.exists(CALORIES_CSV) and _is_merged(CALORIES_CSV):
        df = pd.read_csv(CALORIES_CSV)
    else:
        exercise = pd.read_csv(EXERCISE_CSV)
        calories = pd.read_csv(CALORIES_CSV)
        exercise = _resolve_columns(exercise)
        calories = _resolve_columns(calories)
        merge_key = "User_ID" if "User_ID" in exercise.columns else exercise.columns[0]
        df = exercise.merge(calories, on=merge_key)

    df.columns = [c.strip() for c in df.columns]
    df = _resolve_columns(df)

    # Encode Gender string → int if needed (handles both object and StringDtype)
    if not pd.api.types.is_numeric_dtype(df["Gender"]):
        df["Gender"] = (df["Gender"].str.lower() == "male").astype(int)

    feature_cols = ["Gender", "Age", "Height", "Weight", "Duration", "Heart_Rate", "Body_Temp"]
    target_col = "Calories"

    missing = [c for c in feature_cols + [target_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}. Found: {list(df.columns)}")

    df = df[feature_cols + [target_col]].dropna()
    X = df[feature_cols].values.astype(float)
    y = df[target_col].values.astype(float)
    return X, y


def _generate_synthetic_data(n: int = 1000):
    """Fallback synthetic dataset based on physiological relationships."""
    warnings.warn(
        "Real dataset not found — training on synthetic data. "
        "Place exercise.csv and calories.csv in backend/app/ml/data/ for real data.",
        UserWarning,
        stacklevel=2,
    )
    rng = np.random.default_rng(42)
    gender = rng.integers(0, 2, n)
    age = rng.integers(18, 65, n)
    height = rng.uniform(150, 195, n)
    weight = rng.uniform(45, 120, n)
    duration = rng.uniform(5, 60, n)
    heart_rate = rng.uniform(60, 180, n)
    body_temp = rng.uniform(36.0, 41.0, n)

    calories = (
        0.014 * heart_rate * duration
        + 0.012 * weight * duration
        + 0.001 * age * duration
        + 0.5 * gender * duration
        + 0.3 * (body_temp - 37) * duration
        + rng.normal(0, 5, n)
    )
    calories = np.clip(calories, 5, 800)

    X = np.column_stack([gender, age, height, weight, duration, heart_rate, body_temp])
    return X, calories


def _get_training_data():
    """Return (X, y) from real data if available, else synthetic."""
    has_two_files = os.path.exists(EXERCISE_CSV) and os.path.exists(CALORIES_CSV)
    if os.path.exists(MERGED_CSV) or has_two_files or os.path.exists(CALORIES_CSV):
        try:
            X, y = _load_real_data()
            print(f"[calorie_predictor] Loaded real dataset — {len(y)} samples.")
            return X, y
        except Exception as exc:
            warnings.warn(
                f"Failed to load real dataset ({exc}). Falling back to synthetic data.",
                UserWarning,
                stacklevel=2,
            )
    return _generate_synthetic_data()


def train_model():
    """Train and save the Lasso regression model with polynomial features (degree 3)."""
    X, y = _get_training_data()

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("poly", PolynomialFeatures(degree=3, include_bias=False)),
        ("lasso", Lasso(alpha=0.01, max_iter=10000)),
    ])

    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"[calorie_predictor] Model saved to {MODEL_PATH}")
    return model


def load_model():
    """Load the saved model, training it first if it does not exist."""
    if not os.path.exists(MODEL_PATH):
        return train_model()
    return joblib.load(MODEL_PATH)


_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def predict_calories(
    gender: str,
    age: int,
    height: float,      # cm
    weight: float,      # kg
    duration: float,    # minutes
    heart_rate: float,  # BPM
    body_temp: float = 37.5,
) -> float:
    """Predict calories burned during a workout session."""
    model = get_model()
    gender_encoded = 1 if gender.lower() == "male" else 0
    X = np.array([[gender_encoded, age, height, weight, duration, heart_rate, body_temp]])
    prediction = model.predict(X)[0]
    return round(max(float(prediction), 1.0), 2)


def retrain():
    """Force a full retrain (call this after adding the real dataset)."""
    global _model
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
    _model = train_model()
    return {"status": "retrained", "model_path": MODEL_PATH}
