"""Seed database with sample agriculture data (offline demo)."""

from __future__ import annotations

import uuid
from typing import Any

from .database import Database


SAMPLE_CROPS: list[dict[str, Any]] = [
    {
        "id": "crop_wheat",
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "family": "Poaceae",
        "genus": "Triticum",
        "traits": {
            "optimal_ph": [5.5, 7.5],
            "optimal_clay": [100, 350],
            "drought_tolerance": "moderate",
            "growth_period_days": [90, 150],
        },
    },
    {
        "id": "crop_soybean",
        "name": "Soybean",
        "scientific_name": "Glycine max",
        "family": "Fabaceae",
        "genus": "Glycine",
        "traits": {
            "optimal_ph": [5.5, 7.0],
            "optimal_clay": [150, 400],
            "drought_tolerance": "low",
            "growth_period_days": [80, 120],
        },
    },
    {
        "id": "crop_potato",
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "family": "Solanaceae",
        "genus": "Solanum",
        "traits": {
            "optimal_ph": [5.5, 7.0],
            "optimal_clay": [100, 300],
            "drought_tolerance": "low",
            "growth_period_days": [90, 120],
        },
    },
]

SAMPLE_SOILS: list[dict[str, Any]] = [
    {
        "id": "soil_midwest_us",
        "latitude": 41.0,
        "longitude": -93.0,
        "properties": {
            "phh2o": 65,   # pH 6.5
            "clay": 250,
            "silt": 350,
            "sand": 400,
            "cec": 20,
            "soc": 12,
            "nitrogen": 8,
        },
        "depth_layers": {
            "0-5cm": {"phh2o": 65, "clay": 250},
            "5-15cm": {"phh2o": 64, "clay": 260},
        },
    },
    {
        "id": "soil_indo_gangetic",
        "latitude": 26.0,
        "longitude": 82.0,
        "properties": {
            "phh2o": 75,   # pH 7.5
            "clay": 350,
            "silt": 400,
            "sand": 250,
            "cec": 25,
            "soc": 15,
            "nitrogen": 10,
        },
        "depth_layers": {
            "0-5cm": {"phh2o": 75, "clay": 350},
        },
    },
    {
        "id": "soil_savanna",
        "latitude": 6.5,
        "longitude": 3.4,
        "properties": {
            "phh2o": 55,   # pH 5.5
            "clay": 150,
            "silt": 200,
            "sand": 650,
            "cec": 10,
            "soc": 6,
            "nitrogen": 4,
        },
        "depth_layers": {
            "0-5cm": {"phh2o": 55, "clay": 150},
        },
    },
]

SAMPLE_PESTS: list[dict[str, Any]] = [
    {
        "id": "pest_aphid_soybean",
        "name": "Soybean Aphid",
        "type": "pest",
        "affected_crops": ["Soybean", "Glycine max"],
        "symptoms": ["Leaf curling", "Stunted growth", "Honeydew secretion"],
        "treatments": ["Ladybug release", "Neem oil spray", "Pyrethroid insecticides"],
    },
    {
        "id": "disease_blight_potato",
        "name": "Late Blight",
        "type": "disease",
        "affected_crops": ["Potato", "Tomato", "Solanum tuberosum"],
        "symptoms": ["Water-soaked lesions", "White fungal growth", "Tuber rot"],
        "treatments": ["Copper fungicide", "Resistant varieties", "Crop rotation"],
    },
    {
        "id": "disease_rust_wheat",
        "name": "Wheat Rust",
        "type": "disease",
        "affected_crops": ["Wheat", "Triticum aestivum"],
        "symptoms": ["Orange-brown pustules", "Leaf yellowing", "Reduced grain fill"],
        "treatments": ["Fungicide application", "Resistant cultivars", "Early planting"],
    },
]

SAMPLE_SEASONAL: list[dict[str, Any]] = [
    {
        "id": "season_wheat_india",
        "crop_id": "crop_wheat",
        "region": "South Asia",
        "planting_months": [11, 12],
        "harvest_months": [3, 4, 5],
        "growth_duration_days": 120,
    },
    {
        "id": "season_soybean_us",
        "crop_id": "crop_soybean",
        "region": "North America",
        "planting_months": [5, 6],
        "harvest_months": [9, 10],
        "growth_duration_days": 100,
    },
    {
        "id": "season_potato_india",
        "crop_id": "crop_potato",
        "region": "South Asia",
        "planting_months": [10, 11],
        "harvest_months": [1, 2, 3],
        "growth_duration_days": 100,
    },
]

SAMPLE_WEATHER: list[dict[str, Any]] = [
    {
        "id": "weather_wheat",
        "crop_id": "crop_wheat",
        "temperature_range": {"min": 10, "max": 25},
        "rainfall_range": {"min": 400, "max": 800},
        "humidity_range": {"min": 40, "max": 70},
        "optimal_conditions": {
            "temperature": 18,
            "rainfall": 600,
            "humidity": 55,
        },
    },
    {
        "id": "weather_soybean",
        "crop_id": "crop_soybean",
        "temperature_range": {"min": 20, "max": 30},
        "rainfall_range": {"min": 500, "max": 900},
        "humidity_range": {"min": 50, "max": 80},
        "optimal_conditions": {
            "temperature": 25,
            "rainfall": 700,
            "humidity": 65,
        },
    },
    {
        "id": "weather_potato",
        "crop_id": "crop_potato",
        "temperature_range": {"min": 15, "max": 22},
        "rainfall_range": {"min": 500, "max": 700},
        "humidity_range": {"min": 60, "max": 80},
        "optimal_conditions": {
            "temperature": 18,
            "rainfall": 600,
            "humidity": 70,
        },
    },
]


def seed_database(db: Database) -> None:
    """Populate the database with sample data for offline demonstration."""
    for crop in SAMPLE_CROPS:
        db.upsert_crop(crop)
    for soil in SAMPLE_SOILS:
        db.upsert_soil(soil)
    for pest in SAMPLE_PESTS:
        db.upsert_pest(pest)
    for season in SAMPLE_SEASONAL:
        db.upsert_seasonal(season)
    for weather in SAMPLE_WEATHER:
        db.upsert_weather(weather)
