# Calorie Burn Model — EDA & Evaluation Documentation

## Overview

This folder contains the EDA and model evaluation notebook for the GetFit calorie burn predictor.

| File | Purpose |
|------|---------|
| `calorie_model_eda.ipynb` | Runnable Jupyter notebook — EDA, regression metrics, classification metrics, feature importance |
| `calorie_model_eda.md` | This file — static documentation and results reference |

---

## Dataset

**File:** `backend/app/ml/data/calories.csv`  
**Rows:** 15,000  
**Source:** Kaggle — "Calories Burned During Exercise and Activities" (aadhavvignesh)

### Columns

| Column | Type | Description |
|--------|------|-------------|
| User_ID | int | Unique identifier (dropped before training) |
| Gender | str → int | male=1, female=0 |
| Age | int | Age in years |
| Height | float | Height in cm |
| Weight | float | Weight in kg |
| Duration | float | Exercise duration in minutes |
| Heart_Rate | float | Heart rate in BPM during exercise |
| Body_Temp | float | Body temperature in °C during exercise |
| **Calories** | float | **Target — calories burned** |

> `exercise_dataset.csv` (248 rows) is an activity lookup table and is **not** used in model training.

---

## Model Architecture

**Pipeline:** `StandardScaler → PolynomialFeatures(degree=3) → Lasso(alpha=0.01)`

**File:** `backend/app/ml/calorie_predictor.py`  
**Saved model:** `backend/app/ml/calorie_model.pkl`

| Step | Class | Parameters |
|------|-------|------------|
| Scaler | `StandardScaler` | default |
| Poly | `PolynomialFeatures` | degree=3, include_bias=False |
| Regressor | `Lasso` | alpha=0.01, max_iter=10000 |

---

## Metric Note

Lasso is a **regression** model (continuous output). The notebook reports:

### Regression metrics (Section C)
| Metric | Meaning |
|--------|---------|
| R² | Proportion of variance explained (1.0 = perfect) |
| MAE | Mean absolute error in calories |
| RMSE | Root mean squared error — penalises large errors more |

### Classification metrics (Section D)
Calorie predictions are binned into three classes for F1/precision/recall reporting:

| Class | Calorie Range |
|-------|--------------|
| Low | < 50 cal |
| Medium | 50 – 119 cal |
| High | ≥ 120 cal |

A **false positive** for a class = model predicted that class when the actual was different.

---

## How to Run

```bash
# 1. Install dependencies (first time only)
cd backend
pip install matplotlib seaborn scipy jupyter

# 2. Launch the notebook
jupyter notebook notebooks/calorie_model_eda.ipynb
```

Run all cells top-to-bottom (`Kernel → Restart & Run All`).

---

## How to Retrain

```python
# From backend/app/ml/calorie_predictor.py
from app.ml.calorie_predictor import retrain
retrain()
```

Or via the API endpoint (if wired up):
```
POST /api/admin/retrain-model
```

---

## Evaluation Results

> Fill this section in after running the notebook.

| Metric | Value |
|--------|-------|
| R² (hold-out) | — |
| MAE | — cal |
| RMSE | — cal |
| CV R² (5-fold) | — ± — |

### Classification Report (binned)

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Low | — | — | — |
| Medium | — | — | — |
| High | — | — | — |
