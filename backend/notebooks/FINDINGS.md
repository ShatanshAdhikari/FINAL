# Calorie Burn Model — EDA & Evaluation Findings

**Date:** 2026-06-20  
**Model:** Lasso Regression — `StandardScaler → PolynomialFeatures(degree=3) → Lasso(alpha=0.01)`  
**Dataset:** `backend/app/ml/data/calories.csv`  
**Notebook:** `calorie_model_eda.ipynb`

---

## A — Dataset Overview

| Property | Value |
|----------|-------|
| Total samples | 15,000 |
| Features | 7 (Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp) |
| Target | Calories (continuous) |
| Missing values | **None** |
| Duplicate User_IDs | **None** |

### Descriptive Statistics

| Feature | Mean | Std | Min | Max |
|---------|------|-----|-----|-----|
| Gender (M=1, F=0) | 0.496 | 0.500 | 0 | 1 |
| Age | 42.79 | 16.98 | 20 | 79 |
| Height (cm) | 174.47 | 14.26 | 123 | 222 |
| Weight (kg) | 74.97 | 15.04 | 36 | 132 |
| Duration (min) | 15.53 | 8.32 | 1 | 30 |
| Heart_Rate (BPM) | 95.52 | 9.58 | 67 | 128 |
| Body_Temp (°C) | 40.03 | 0.78 | 37.1 | 41.5 |
| **Calories** | **89.54** | **62.46** | **1** | **314** |

---

## B — Exploratory Data Analysis

### Gender Split
| Gender | Count | Mean Calories |
|--------|-------|--------------|
| Female | 7,553 (50.4%) | 88.15 cal |
| Male | 7,447 (49.6%) | 90.95 cal |

Dataset is well-balanced by gender. Males burn slightly more calories on average (~3% difference).

### Feature Skewness
| Feature | Skewness | Interpretation |
|---------|----------|----------------|
| Body_Temp | −0.994 | Moderately left-skewed |
| Calories | +0.505 | Slightly right-skewed |
| Age | +0.473 | Slightly right-skewed |
| Weight | +0.227 | Near-symmetric |
| Others | < 0.1 | Symmetric |

### Correlation with Calories
| Feature | Pearson r | Strength |
|---------|-----------|----------|
| **Duration** | **0.9554** | Very strong positive |
| **Heart_Rate** | **0.8979** | Strong positive |
| **Body_Temp** | **0.8246** | Strong positive |
| Age | 0.1544 | Weak positive |
| Weight | 0.0355 | Negligible |
| Gender | 0.0224 | Negligible |
| Height | 0.0175 | Negligible |

> **Key insight:** Duration, Heart_Rate, and Body_Temp are the three dominant predictors. Weight, Gender, and Height have minimal direct linear correlation with calories.

### Outliers (IQR Method)
| Feature | Outlier Count | % of Data |
|---------|--------------|-----------|
| Body_Temp | 369 | 2.5% |
| Height | 14 | 0.1% |
| Weight | 6 | 0.0% |
| Heart_Rate | 1 | 0.0% |
| Age | 0 | 0.0% |
| Duration | 0 | 0.0% |
| Calories | 4 | 0.0% |

> Body_Temp has the most outliers (2.5%) due to its left-skewed distribution. All other features are extremely clean.

---

## C — Regression Model Evaluation

### Hold-out Test Set (n = 3,000 / 20%)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **R²** | **0.999976** | Model explains 99.998% of variance |
| **MAE** | **0.26 cal** | Average prediction error of 0.26 calories |
| **RMSE** | **0.30 cal** | Penalised error of 0.30 calories |

### 5-Fold Cross-Validation

| Metric | Value |
|--------|-------|
| Mean R² | 0.999976 |
| Std R² | ±0.000001 |
| Per-fold R² | [1.0, 1.0, 1.0, 1.0, 1.0] |

> The model is **exceptionally consistent** across all folds — no overfitting detected.

### Residuals Analysis

| Stat | Value |
|------|-------|
| Mean residual | −0.004 cal (near-zero bias) |
| Std of residuals | 0.304 cal |
| Max over-prediction | 1.015 cal |
| Max under-prediction | 0.740 cal |

> Residuals are extremely tight (all within ±1.1 calories). The model has virtually no systematic bias.

---

## D — Classification Metrics (Binned Calories)

Calorie output binned into three classes for F1/precision/recall analysis:

| Class | Range |
|-------|-------|
| Low | < 50 cal |
| Medium | 50 – 119 cal |
| High | ≥ 120 cal |

### Classification Report

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Low | 0.99 | 1.00 | **1.00** | 993 |
| Medium | 0.99 | 0.99 | **0.99** | 1,048 |
| High | 1.00 | 0.99 | **1.00** | 959 |
| **Accuracy** | | | **0.99** | **3,000** |
| Macro avg | 0.99 | 0.99 | 0.99 | |
| Weighted avg | 0.99 | 0.99 | 0.99 | |

### Confusion Matrix

```
             Predicted
              Low   Med   High
Actual Low  [ 993     0      0 ]
       Med  [   8  1040      0 ]
       High [   0     9    950 ]
```

### False Positives per Class

| Class | False Positives | Meaning |
|-------|----------------|---------|
| Low | 8 | Predicted Low when actually Medium |
| Medium | 9 | Predicted Medium when actually High |
| High | **0** | Never incorrectly predicted High |

> The model never falsely predicts high calorie burn. The 17 total misclassifications (0.6% of test set) are all adjacent-class errors (Low↔Medium or Medium↔High), never Low↔High jumps.

---

## E — Feature Importance (Lasso Coefficients)

**Non-zero coefficients:** 43 out of 119 polynomial features (Lasso zeroed 64%)

### Top 15 Coefficients (by absolute value)

| Rank | Feature (Polynomial Term) | |Coefficient| | Effect |
|------|--------------------------|-------------|--------|
| 1 | Duration | 41.55 | Positive |
| 2 | Heart_Rate | 18.86 | Positive |
| 3 | Duration × Heart_Rate | 10.22 | Positive |
| 4 | Age | 8.53 | Positive |
| 5 | Age × Duration | 4.63 | Positive |
| 6 | Gender × Weight | 4.07 | Positive |
| 7 | Gender × Age | 4.01 | Positive |
| 8 | Gender × Heart_Rate | 3.11 | Positive |
| 9 | Gender × Age × Duration | 2.15 | Positive |
| 10 | Gender × Weight × Duration | 2.13 | Positive |
| 11 | Gender × Duration × Heart_Rate | 1.67 | Positive |
| 12 | Gender³ | 0.56 | Positive |
| 13 | Weight | 0.45 | Positive |
| 14 | Gender | 0.44 | Positive |
| 15 | Gender × Duration | 0.35 | Positive |

> **Key insight:** Duration is by far the most influential single feature (coeff 41.6), followed by Heart_Rate (18.9). Their interaction term (Duration × Heart_Rate) ranks 3rd, confirming that longer, higher-intensity workouts compound calorie burn non-linearly. Height is not among any non-zero coefficients — Lasso correctly eliminated it as irrelevant.

---

## Summary

| Area | Finding |
|------|---------|
| Data quality | Excellent — no missing values, no duplicates, minimal outliers |
| Most predictive features | Duration > Heart_Rate > Body_Temp |
| Least predictive features | Height, Gender, Weight (low direct correlation) |
| Model accuracy | Near-perfect (R² = 0.9999, MAE = 0.26 cal) |
| Model consistency | Identical performance across all 5 CV folds |
| Classification F1 | 0.99–1.00 across Low/Medium/High bins |
| False positives | Only 17 total (0.6%), all adjacent-class errors |
| Overfitting risk | None detected |
