import pytest
from app.ml.calorie_predictor import predict_calories, get_model


class TestCaloirePredictor:
    def test_model_loads(self):
        model = get_model()
        assert model is not None

    def test_prediction_returns_positive(self):
        result = predict_calories(
            gender="male", age=30, height=175, weight=75,
            duration=30, heart_rate=130, body_temp=37.5,
        )
        assert result["calories"] >= 1.0

    def test_prediction_has_confidence_range(self):
        result = predict_calories("male", 30, 175, 75, 20, 130, 37.5)
        assert "calories" in result
        assert "low" in result
        assert "high" in result
        assert result["low"] <= result["calories"] <= result["high"]

    def test_prediction_is_float(self):
        result = predict_calories(
            gender="female", age=25, height=165, weight=60,
            duration=20, heart_rate=120, body_temp=37.2,
        )
        assert isinstance(result["calories"], float)

    def test_longer_duration_more_calories(self):
        short = predict_calories("male", 30, 175, 75, 10, 130, 37.5)
        long = predict_calories("male", 30, 175, 75, 30, 130, 37.5)
        assert long["calories"] > short["calories"]

    def test_higher_heart_rate_more_calories(self):
        low_hr = predict_calories("male", 30, 175, 75, 20, 90, 37.5)
        high_hr = predict_calories("male", 30, 175, 75, 20, 160, 37.5)
        assert high_hr["calories"] > low_hr["calories"]

    def test_gender_case_insensitive(self):
        upper = predict_calories("MALE", 30, 175, 75, 20, 130, 37.5)
        lower = predict_calories("male", 30, 175, 75, 20, 130, 37.5)
        assert upper["calories"] == lower["calories"]

    def test_minimum_clamp_at_one(self):
        # Very short duration, low HR — result should still be >= 1.0
        result = predict_calories("female", 79, 123, 36, 1, 67, 37.1)
        assert result["calories"] >= 1.0
