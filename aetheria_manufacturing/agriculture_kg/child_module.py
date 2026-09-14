"""
agri_knowledge_graph_child.py — Agriculture KG Child Module.

Child modules for the Agriculture Knowledge Graph:
- Weather Integration: weather-crop interactions
- Fertilizer Recommendations: nutrient-based suggestions
- Irrigation Scheduler: water management
- Harvest Predictor: yield and timing estimation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json


@dataclass
class WeatherPattern:
    """A weather pattern affecting crops."""
    pattern_id: str
    name: str
    description: str
    temperature_range: tuple[float, float]
    rainfall_range: tuple[float, float]
    humidity_range: tuple[float, float]
    season: str
    affected_crops: list[str]  # crop_ids
    risks: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "temperature_range": self.temperature_range,
            "rainfall_range": self.rainfall_range,
            "humidity_range": self.humidity_range,
            "season": self.season,
            "affected_crops": self.affected_crops,
            "risks": self.risks,
        }


@dataclass
class FertilizerRecommendation:
    """A fertilizer recommendation."""
    recommendation_id: str
    crop_id: str
    soil_id: str
    nutrient: str  # N, P, K, etc.
    fertilizer_type: str
    application_rate: str
    application_timing: str
    notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "recommendation_id": self.recommendation_id,
            "crop_id": self.crop_id,
            "soil_id": self.soil_id,
            "nutrient": self.nutrient,
            "fertilizer_type": self.fertilizer_type,
            "application_rate": self.application_rate,
            "application_timing": self.application_timing,
            "notes": self.notes,
        }


@dataclass
class IrrigationSchedule:
    """An irrigation schedule."""
    schedule_id: str
    crop_id: str
    soil_id: str
    growth_stage: str
    water_amount: float  # mm
    frequency: str
    method: str
    notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schedule_id": self.schedule_id,
            "crop_id": self.crop_id,
            "soil_id": self.soil_id,
            "growth_stage": self.growth_stage,
            "water_amount": self.water_amount,
            "frequency": self.frequency,
            "method": self.method,
            "notes": self.notes,
        }


@dataclass
class HarvestPrediction:
    """A harvest prediction."""
    prediction_id: str
    crop_id: str
    planting_date: str
    expected_harvest: str
    expected_yield: float  # t/ha
    confidence: float
    notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "prediction_id": self.prediction_id,
            "crop_id": self.crop_id,
            "planting_date": self.planting_date,
            "expected_harvest": self.expected_harvest,
            "expected_yield": self.expected_yield,
            "confidence": self.confidence,
            "notes": self.notes,
        }


class WeatherIntegrator:
    """
    Weather-crop interaction mapping.
    """

    def __init__(self):
        self.patterns: dict[str, WeatherPattern] = {}
        self._load_default_patterns()

    def _load_default_patterns(self):
        """Load default weather patterns."""
        patterns = [
            WeatherPattern(
                pattern_id="monsoon_001",
                name="Monsoon",
                description="Heavy seasonal rainfall",
                temperature_range=(20.0, 35.0),
                rainfall_range=(200.0, 1000.0),
                humidity_range=(70.0, 100.0),
                season="kharif",
                affected_crops=["rice_001", "maize_001", "cotton_001"],
                risks=["waterlogging", "flooding", "disease pressure"],
            ),
            WeatherPattern(
                pattern_id="winter_001",
                name="Winter",
                description="Cool dry season",
                temperature_range=(5.0, 20.0),
                rainfall_range=(0.0, 50.0),
                humidity_range=(30.0, 60.0),
                season="rabi",
                affected_crops=["wheat_001", "potato_001"],
                risks=["frost damage", "cold stress"],
            ),
            WeatherPattern(
                pattern_id="summer_001",
                name="Summer",
                description="Hot dry season",
                temperature_range=(30.0, 45.0),
                rainfall_range=(0.0, 30.0),
                humidity_range=(20.0, 50.0),
                season="summer",
                affected_crops=["groundnut_001"],
                risks=["heat stress", "drought"],
            ),
        ]
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern

    def get_pattern(self, pattern_id: str) -> WeatherPattern | None:
        """Get a weather pattern by ID."""
        return self.patterns.get(pattern_id)

    def get_patterns_for_season(self, season: str) -> list[WeatherPattern]:
        """Get patterns for a season."""
        return [p for p in self.patterns.values() if p.season == season]

    def get_patterns_for_crop(self, crop_id: str) -> list[WeatherPattern]:
        """Get patterns affecting a crop."""
        return [p for p in self.patterns.values() if crop_id in p.affected_crops]

    def list_patterns(self) -> list[WeatherPattern]:
        """List all patterns."""
        return list(self.patterns.values())


class FertilizerRecommender:
    """
    Fertilizer recommendation engine.
    """

    def __init__(self):
        self.recommendations: list[FertilizerRecommendation] = []
        self._load_default_recommendations()

    def _load_default_recommendations(self):
        """Load default fertilizer recommendations."""
        self.recommendations = [
            FertilizerRecommendation(
                recommendation_id="fert_wheat_n",
                crop_id="wheat_001",
                soil_id="loam_001",
                nutrient="N",
                fertilizer_type="Urea",
                application_rate="120 kg/ha",
                application_timing="Split: 50% at sowing, 50% at tillering",
                notes="Adjust based on soil test",
            ),
            FertilizerRecommendation(
                recommendation_id="fert_rice_n",
                crop_id="rice_001",
                soil_id="clay_001",
                nutrient="N",
                fertilizer_type="Urea",
                application_rate="100 kg/ha",
                application_timing="Split: 33% at basal, 33% at tillering, 34% at panicle initiation",
                notes="Use neem-coated urea for slow release",
            ),
            FertilizerRecommendation(
                recommendation_id="fert_potato_k",
                crop_id="potato_001",
                soil_id="loam_001",
                nutrient="K",
                fertilizer_type="Muriate of Potash",
                application_rate="100 kg/ha",
                application_timing="At planting",
                notes="Potassium is critical for tuber development",
            ),
        ]

    def get_recommendations(self, crop_id: str, soil_id: str | None = None) -> list[FertilizerRecommendation]:
        """Get recommendations for a crop/soil."""
        results = [r for r in self.recommendations if r.crop_id == crop_id]
        if soil_id:
            results = [r for r in results if r.soil_id == soil_id]
        return results

    def add_recommendation(self, recommendation: FertilizerRecommendation) -> None:
        """Add a recommendation."""
        self.recommendations.append(recommendation)

    def list_recommendations(self) -> list[FertilizerRecommendation]:
        """List all recommendations."""
        return self.recommendations


class IrrigationScheduler:
    """
    Irrigation scheduling engine.
    """

    def __init__(self):
        self.schedules: list[IrrigationSchedule] = []
        self._load_default_schedules()

    def _load_default_schedules(self):
        """Load default irrigation schedules."""
        self.schedules = [
            IrrigationSchedule(
                schedule_id="irr_wheat_veg",
                crop_id="wheat_001",
                soil_id="loam_001",
                growth_stage="vegetative",
                water_amount=25.0,
                frequency="every 7 days",
                method="furrow",
                notes="Reduce if rainfall occurs",
            ),
            IrrigationSchedule(
                schedule_id="irr_rice_veg",
                crop_id="rice_001",
                soil_id="clay_001",
                growth_stage="vegetative",
                water_amount=50.0,
                frequency="continuous flooding",
                method="flood",
                notes="Maintain 5cm standing water",
            ),
            IrrigationSchedule(
                schedule_id="irr_potato_tuber",
                crop_id="potato_001",
                soil_id="loam_001",
                growth_stage="tuber formation",
                water_amount=30.0,
                frequency="every 5 days",
                method="drip",
                notes="Critical stage for water",
            ),
        ]

    def get_schedules(self, crop_id: str, soil_id: str | None = None) -> list[IrrigationSchedule]:
        """Get schedules for a crop/soil."""
        results = [s for s in self.schedules if s.crop_id == crop_id]
        if soil_id:
            results = [s for s in results if s.soil_id == soil_id]
        return results

    def add_schedule(self, schedule: IrrigationSchedule) -> None:
        """Add a schedule."""
        self.schedules.append(schedule)

    def list_schedules(self) -> list[IrrigationSchedule]:
        """List all schedules."""
        return self.schedules


class HarvestPredictor:
    """
    Harvest prediction engine.
    """

    def __init__(self):
        self.predictions: list[HarvestPrediction] = []

    def predict_harvest(
        self,
        crop_id: str,
        planting_date: str,
        expected_yield: float,
        confidence: float = 0.7,
    ) -> HarvestPrediction:
        """Predict harvest for a crop."""
        prediction = HarvestPrediction(
            prediction_id=f"pred_{crop_id}_{planting_date}",
            crop_id=crop_id,
            planting_date=planting_date,
            expected_harvest=f"{planting_date} + 120 days",
            expected_yield=expected_yield,
            confidence=confidence,
            notes="Based on average growth duration",
        )
        self.predictions.append(prediction)
        return prediction

    def get_predictions(self, crop_id: str | None = None) -> list[HarvestPrediction]:
        """Get predictions."""
        if crop_id:
            return [p for p in self.predictions if p.crop_id == crop_id]
        return self.predictions


class AgriKGChild:
    """
    Child module combining all sub-modules.
    """

    def __init__(self):
        self.weather = WeatherIntegrator()
        self.fertilizer = FertilizerRecommender()
        self.irrigation = IrrigationScheduler()
        self.harvest = HarvestPredictor()

    def get_full_recommendation(
        self,
        crop_id: str,
        soil_id: str,
        season: str,
    ) -> dict[str, Any]:
        """Get a full recommendation for a crop-soil-season combination."""
        weather_patterns = self.weather.get_patterns_for_season(season)
        fertilizers = self.fertilizer.get_recommendations(crop_id, soil_id)
        irrigation = self.irrigation.get_schedules(crop_id, soil_id)

        return {
            "crop_id": crop_id,
            "soil_id": soil_id,
            "season": season,
            "weather_patterns": [p.to_dict() for p in weather_patterns],
            "fertilizer_recommendations": [f.to_dict() for f in fertilizers],
            "irrigation_schedules": [s.to_dict() for s in irrigation],
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get child module statistics."""
        return {
            "weather_patterns": len(self.weather.patterns),
            "fertilizer_recommendations": len(self.fertilizer.recommendations),
            "irrigation_schedules": len(self.irrigation.schedules),
            "harvest_predictions": len(self.harvest.predictions),
        }
