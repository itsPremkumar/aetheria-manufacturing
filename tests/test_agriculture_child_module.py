"""Tests for agriculture KG child module (weather, fertilizer, irrigation, harvest)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from aetheria_manufacturing.agriculture_kg.child_module import (
    WeatherPattern,
    FertilizerRecommendation,
    IrrigationSchedule,
    HarvestPrediction,
    WeatherIntegrator,
    FertilizerRecommender,
    IrrigationScheduler,
    HarvestPredictor,
    AgriKGChild,
)


class TestWeatherPattern:
    def test_to_dict(self):
        pattern = WeatherPattern(
            pattern_id="test_pattern",
            name="Test Pattern",
            description="A test pattern",
            temperature_range=(20.0, 30.0),
            rainfall_range=(100.0, 500.0),
            humidity_range=(50.0, 80.0),
            season="kharif",
            affected_crops=["rice_001"],
            risks=["flooding"],
        )
        d = pattern.to_dict()
        assert d["pattern_id"] == "test_pattern"
        assert d["name"] == "Test Pattern"
        assert d["season"] == "kharif"


class TestFertilizerRecommendation:
    def test_to_dict(self):
        rec = FertilizerRecommendation(
            recommendation_id="test_rec",
            crop_id="wheat_001",
            soil_id="loam_001",
            nutrient="N",
            fertilizer_type="Urea",
            application_rate="120 kg/ha",
            application_timing="Split application",
            notes="Test notes",
        )
        d = rec.to_dict()
        assert d["recommendation_id"] == "test_rec"
        assert d["nutrient"] == "N"


class TestIrrigationSchedule:
    def test_to_dict(self):
        schedule = IrrigationSchedule(
            schedule_id="test_schedule",
            crop_id="wheat_001",
            soil_id="loam_001",
            growth_stage="vegetative",
            water_amount=25.0,
            frequency="every 7 days",
            method="furrow",
            notes="Test schedule",
        )
        d = schedule.to_dict()
        assert d["schedule_id"] == "test_schedule"
        assert d["water_amount"] == 25.0


class TestHarvestPrediction:
    def test_to_dict(self):
        prediction = HarvestPrediction(
            prediction_id="test_pred",
            crop_id="wheat_001",
            planting_date="2024-01-01",
            expected_harvest="2024-05-01",
            expected_yield=4.5,
            confidence=0.8,
            notes="Test prediction",
        )
        d = prediction.to_dict()
        assert d["prediction_id"] == "test_pred"
        assert d["expected_yield"] == 4.5


class TestWeatherIntegrator:
    def test_default_patterns_loaded(self):
        integrator = WeatherIntegrator()
        assert len(integrator.patterns) >= 2

    def test_get_pattern(self):
        integrator = WeatherIntegrator()
        pattern = integrator.get_pattern("monsoon_001")
        assert pattern is not None
        assert pattern.name == "Monsoon"

    def test_get_pattern_invalid(self):
        integrator = WeatherIntegrator()
        pattern = integrator.get_pattern("invalid")
        assert pattern is None

    def test_get_patterns_for_season(self):
        integrator = WeatherIntegrator()
        patterns = integrator.get_patterns_for_season("kharif")
        assert len(patterns) > 0
        assert all(p.season == "kharif" for p in patterns)

    def test_get_patterns_for_crop(self):
        integrator = WeatherIntegrator()
        patterns = integrator.get_patterns_for_crop("rice_001")
        assert len(patterns) > 0

    def test_get_patterns_for_crop_no_match(self):
        integrator = WeatherIntegrator()
        patterns = integrator.get_patterns_for_crop("nonexistent_crop")
        assert len(patterns) == 0

    def test_list_patterns(self):
        integrator = WeatherIntegrator()
        patterns = integrator.list_patterns()
        assert len(patterns) >= 2


class TestFertilizerRecommender:
    def test_default_recommendations_loaded(self):
        recommender = FertilizerRecommender()
        assert len(recommender.recommendations) >= 2

    def test_get_recommendations_for_crop(self):
        recommender = FertilizerRecommender()
        recs = recommender.get_recommendations("wheat_001")
        assert len(recs) > 0
        assert all(r.crop_id == "wheat_001" for r in recs)

    def test_get_recommendations_for_crop_and_soil(self):
        recommender = FertilizerRecommender()
        recs = recommender.get_recommendations("wheat_001", "loam_001")
        assert len(recs) > 0

    def test_get_recommendations_no_match(self):
        recommender = FertilizerRecommender()
        recs = recommender.get_recommendations("nonexistent")
        assert len(recs) == 0

    def test_add_recommendation(self):
        recommender = FertilizerRecommender()
        initial_count = len(recommender.recommendations)
        new_rec = FertilizerRecommendation(
            recommendation_id="test_new",
            crop_id="test_crop",
            soil_id="test_soil",
            nutrient="P",
            fertilizer_type="DAP",
            application_rate="50 kg/ha",
            application_timing="At sowing",
            notes="Test",
        )
        recommender.add_recommendation(new_rec)
        assert len(recommender.recommendations) == initial_count + 1

    def test_list_recommendations(self):
        recommender = FertilizerRecommender()
        recs = recommender.list_recommendations()
        assert len(recs) >= 2


class TestIrrigationScheduler:
    def test_default_schedules_loaded(self):
        scheduler = IrrigationScheduler()
        assert len(scheduler.schedules) >= 2

    def test_get_schedules_for_crop(self):
        scheduler = IrrigationScheduler()
        schedules = scheduler.get_schedules("wheat_001")
        assert len(schedules) > 0

    def test_get_schedules_for_crop_and_soil(self):
        scheduler = IrrigationScheduler()
        schedules = scheduler.get_schedules("wheat_001", "loam_001")
        assert len(schedules) > 0

    def test_get_schedules_no_match(self):
        scheduler = IrrigationScheduler()
        schedules = scheduler.get_schedules("nonexistent")
        assert len(schedules) == 0

    def test_add_schedule(self):
        scheduler = IrrigationScheduler()
        initial_count = len(scheduler.schedules)
        new_schedule = IrrigationSchedule(
            schedule_id="test_schedule",
            crop_id="test_crop",
            soil_id="test_soil",
            growth_stage="flowering",
            water_amount=40.0,
            frequency="every 3 days",
            method="sprinkler",
            notes="Test",
        )
        scheduler.add_schedule(new_schedule)
        assert len(scheduler.schedules) == initial_count + 1

    def test_list_schedules(self):
        scheduler = IrrigationScheduler()
        schedules = scheduler.list_schedules()
        assert len(schedules) >= 2


class TestHarvestPredictor:
    def test_predict_harvest(self):
        predictor = HarvestPredictor()
        prediction = predictor.predict_harvest("wheat_001", "2024-01-01", 4.5)
        assert prediction.crop_id == "wheat_001"
        assert prediction.expected_yield == 4.5

    def test_predict_harvest_stored(self):
        predictor = HarvestPredictor()
        predictor.predict_harvest("wheat_001", "2024-01-01", 4.5)
        predictions = predictor.get_predictions("wheat_001")
        assert len(predictions) > 0

    def test_get_predictions_all(self):
        predictor = HarvestPredictor()
        predictor.predict_harvest("wheat_001", "2024-01-01", 4.5)
        predictor.predict_harvest("rice_001", "2024-06-01", 6.0)
        predictions = predictor.get_predictions()
        assert len(predictions) >= 2

    def test_get_predictions_by_crop(self):
        predictor = HarvestPredictor()
        predictor.predict_harvest("wheat_001", "2024-01-01", 4.5)
        predictions = predictor.get_predictions("wheat_001")
        assert len(predictions) == 1

    def test_get_predictions_no_match(self):
        predictor = HarvestPredictor()
        predictions = predictor.get_predictions("nonexistent")
        assert len(predictions) == 0


class TestAgriKGChild:
    def test_initialization(self):
        child = AgriKGChild()
        assert child.weather is not None
        assert child.fertilizer is not None
        assert child.irrigation is not None
        assert child.harvest is not None

    def test_get_full_recommendation(self):
        child = AgriKGChild()
        rec = child.get_full_recommendation("wheat_001", "loam_001", "rabi")
        assert rec["crop_id"] == "wheat_001"
        assert rec["soil_id"] == "loam_001"
        assert rec["season"] == "rabi"
        assert "weather_patterns" in rec
        assert "fertilizer_recommendations" in rec
        assert "irrigation_schedules" in rec

    def test_get_statistics(self):
        child = AgriKGChild()
        stats = child.get_statistics()
        assert stats["weather_patterns"] >= 2
        assert stats["fertilizer_recommendations"] >= 2
        assert stats["irrigation_schedules"] >= 2
        assert "harvest_predictions" in stats
