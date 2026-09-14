"""Tests for agriculture KG reasoning engine (CropSoilMatcher, PestDiseaseIdentifier, SeasonalReasoner, WeatherMapper)."""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from aetheria_manufacturing.agriculture_kg.database import Database
from aetheria_manufacturing.agriculture_kg.engine import (
    CropSoilMatcher,
    PestDiseaseIdentifier,
    SeasonalReasoner,
    WeatherMapper,
)


@pytest.fixture
def db():
    """Create a temporary database with sample data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    
    # Insert sample crop
    db.upsert_crop({
        "id": "crop_wheat",
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "family": "Poaceae",
        "genus": "Triticum",
        "traits": {"optimal_ph": [5.5, 7.5]},
    })
    
    # Insert sample soil
    db.upsert_soil({
        "id": "soil_test_1",
        "latitude": 31.0,
        "longitude": 75.0,
        "properties": {"phh2o": 65, "clay": 200, "cec": 20},
        "depth_layers": {},
    })
    
    # Insert sample pest
    db.upsert_pest({
        "id": "pest_aphid",
        "name": "Aphid",
        "type": "pest",
        "affected_crops": ["wheat", "rice"],
        "symptoms": ["leaf curling", "stunted growth"],
        "treatments": ["neem oil", "insecticide"],
    })
    
    # Insert sample seasonal pattern
    db.upsert_seasonal({
        "id": "season_wheat_rabi",
        "crop_id": "crop_wheat",
        "region": "India",
        "planting_months": [11, 12],
        "harvest_months": [3, 4],
        "growth_duration_days": 120,
    })
    
    # Insert sample weather interaction
    db.upsert_weather({
        "id": "weather_wheat",
        "crop_id": "crop_wheat",
        "temperature_range": {"min": 5, "max": 25},
        "rainfall_range": {"min": 0, "max": 100},
        "humidity_range": {"min": 30, "max": 70},
        "optimal_conditions": {"temperature": 15, "rainfall": 50},
    })
    
    yield db
    db.close()
    os.unlink(db_path)


class TestCropSoilMatcher:
    def test_initialization(self, db):
        matcher = CropSoilMatcher(db)
        assert matcher.db is not None

    def test_match_crop_soil(self, db):
        matcher = CropSoilMatcher(db)
        result = matcher.match("crop_wheat", "soil_test_1")
        assert result["crop_id"] == "crop_wheat"
        assert result["soil_id"] == "soil_test_1"
        assert 0 <= result["suitability_score"] <= 1

    def test_match_invalid_crop(self, db):
        matcher = CropSoilMatcher(db)
        with pytest.raises(ValueError):
            matcher.match("invalid_crop", "soil_test_1")

    def test_match_invalid_soil(self, db):
        matcher = CropSoilMatcher(db)
        with pytest.raises(ValueError):
            matcher.match("crop_wheat", "invalid_soil")

    def test_match_saves_to_db(self, db):
        matcher = CropSoilMatcher(db)
        result = matcher.match("crop_wheat", "soil_test_1")
        matches = db.get_matches_for_crop("crop_wheat")
        assert len(matches) > 0

    def test_match_all_soils(self, db):
        matcher = CropSoilMatcher(db)
        results = matcher.match_all_soils("crop_wheat")
        assert len(results) > 0

    def test_score_components(self, db):
        matcher = CropSoilMatcher(db)
        result = matcher.match("crop_wheat", "soil_test_1")
        scores = result["matching_traits"]["component_scores"]
        assert "ph" in scores
        assert "clay" in scores
        assert "cec" in scores


class TestPestDiseaseIdentifier:
    def test_initialization(self, db):
        identifier = PestDiseaseIdentifier(db)
        assert identifier.db is not None

    def test_identify_pests_for_crop(self, db):
        identifier = PestDiseaseIdentifier(db)
        results = identifier.identify("wheat")
        assert len(results) > 0

    def test_identify_pests_no_match(self, db):
        identifier = PestDiseaseIdentifier(db)
        results = identifier.identify("nonexistent_crop")
        assert len(results) == 0


class TestSeasonalReasoner:
    def test_initialization(self, db):
        reasoner = SeasonalReasoner(db)
        assert reasoner.db is not None

    def test_get_planting_window(self, db):
        reasoner = SeasonalReasoner(db)
        windows = reasoner.get_planting_window("crop_wheat")
        assert len(windows) > 0

    def test_get_planting_window_with_region(self, db):
        reasoner = SeasonalReasoner(db)
        windows = reasoner.get_planting_window("crop_wheat", region="India")
        assert len(windows) > 0

    def test_get_planting_window_no_match(self, db):
        reasoner = SeasonalReasoner(db)
        windows = reasoner.get_planting_window("invalid_crop")
        assert len(windows) == 0

    def test_is_planting_season(self, db):
        reasoner = SeasonalReasoner(db)
        assert reasoner.is_planting_season("crop_wheat", 11) is True

    def test_is_not_planting_season(self, db):
        reasoner = SeasonalReasoner(db)
        assert reasoner.is_planting_season("crop_wheat", 6) is False


class TestWeatherMapper:
    def test_initialization(self, db):
        mapper = WeatherMapper(db)
        assert mapper.db is not None

    def test_get_optimal_conditions(self, db):
        mapper = WeatherMapper(db)
        conditions = mapper.get_optimal_conditions("crop_wheat")
        assert len(conditions) > 0

    def test_get_optimal_conditions_no_match(self, db):
        mapper = WeatherMapper(db)
        conditions = mapper.get_optimal_conditions("invalid_crop")
        assert len(conditions) == 0

    def test_is_suitable_weather(self, db):
        mapper = WeatherMapper(db)
        result = mapper.is_suitable_weather("crop_wheat", 15.0, 50.0)
        assert result["suitable"] is True

    def test_is_not_suitable_weather(self, db):
        mapper = WeatherMapper(db)
        result = mapper.is_suitable_weather("crop_wheat", 40.0, 500.0)
        assert result["suitable"] is False

    def test_suitable_weather_returns_record(self, db):
        mapper = WeatherMapper(db)
        result = mapper.is_suitable_weather("crop_wheat", 15.0, 50.0)
        assert result["record"] is not None

    def test_unsuitable_weather_returns_none_record(self, db):
        mapper = WeatherMapper(db)
        result = mapper.is_suitable_weather("crop_wheat", 40.0, 500.0)
        assert result["record"] is None


class TestDatabase:
    def test_initialization(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            db = Database(db_path)
            assert db.conn is not None
            db.close()
        finally:
            os.unlink(db_path)

    def test_upsert_and_get_crop(self, db):
        crop = {
            "id": "crop_test",
            "name": "Test Crop",
            "scientific_name": "Testus cropus",
            "family": "Testaceae",
            "genus": "Testus",
            "traits": {},
        }
        db.upsert_crop(crop)
        result = db.get_crop("crop_test")
        assert result is not None
        assert result["name"] == "Test Crop"

    def test_upsert_and_get_soil(self, db):
        soil = {
            "id": "soil_test",
            "latitude": 0.0,
            "longitude": 0.0,
            "properties": {"phh2o": 70},
            "depth_layers": {},
        }
        db.upsert_soil(soil)
        result = db.get_soil("soil_test")
        assert result is not None
        assert result["latitude"] == 0.0

    def test_get_nonexistent_crop(self, db):
        result = db.get_crop("nonexistent")
        assert result is None

    def test_get_nonexistent_soil(self, db):
        result = db.get_soil("nonexistent")
        assert result is None

    def test_list_crops(self, db):
        crops = db.list_crops()
        assert len(crops) > 0

    def test_list_crops_by_family(self, db):
        crops = db.list_crops(family="Poaceae")
        assert len(crops) > 0
        assert all(c["family"] == "Poaceae" for c in crops)
