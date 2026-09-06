"""Local SQLite database for offline-first agriculture KG."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS crops (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    scientific_name TEXT,
    family TEXT,
    genus TEXT,
    traits TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS soil_profiles (
    id TEXT PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    properties TEXT NOT NULL,
    depth_layers TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crop_soil_matches (
    id TEXT PRIMARY KEY,
    crop_id TEXT NOT NULL,
    soil_id TEXT NOT NULL,
    suitability_score REAL,
    matching_traits TEXT,
    FOREIGN KEY (crop_id) REFERENCES crops(id),
    FOREIGN KEY (soil_id) REFERENCES soil_profiles(id)
);

CREATE TABLE IF NOT EXISTS pests_diseases (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('pest', 'disease')),
    affected_crops TEXT,
    symptoms TEXT,
    treatments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seasonal_patterns (
    id TEXT PRIMARY KEY,
    crop_id TEXT NOT NULL,
    region TEXT,
    planting_months TEXT,
    harvest_months TEXT,
    growth_duration_days INTEGER,
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);

CREATE TABLE IF NOT EXISTS weather_interactions (
    id TEXT PRIMARY KEY,
    crop_id TEXT NOT NULL,
    temperature_range TEXT,
    rainfall_range TEXT,
    humidity_range TEXT,
    optimal_conditions TEXT,
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);
"""


class Database:
    """Thin wrapper around SQLite for the agriculture KG."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---- Crops ----
    def upsert_crop(self, crop: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO crops (id, name, scientific_name, family, genus, traits)
            VALUES (:id, :name, :scientific_name, :family, :genus, :traits)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                scientific_name=excluded.scientific_name,
                family=excluded.family,
                genus=excluded.genus,
                traits=excluded.traits
            """,
            {**crop, "traits": json.dumps(crop.get("traits", {}))},
        )
        self.conn.commit()

    def get_crop(self, crop_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM crops WHERE id = ?", (crop_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["traits"] = json.loads(d["traits"])
        return d

    def list_crops(self, family: str | None = None) -> list[dict[str, Any]]:
        if family:
            rows = self.conn.execute(
                "SELECT * FROM crops WHERE family = ?", (family,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM crops").fetchall()
        return [
            {**dict(r), "traits": json.loads(r["traits"])} for r in rows
        ]

    # ---- Soil Profiles ----
    def upsert_soil(self, soil: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO soil_profiles (id, latitude, longitude, properties, depth_layers)
            VALUES (:id, :latitude, :longitude, :properties, :depth_layers)
            ON CONFLICT(id) DO UPDATE SET
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                properties=excluded.properties,
                depth_layers=excluded.depth_layers
            """,
            {
                **soil,
                "properties": json.dumps(soil["properties"]),
                "depth_layers": json.dumps(soil.get("depth_layers", {})),
            },
        )
        self.conn.commit()

    def get_soil(self, soil_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM soil_profiles WHERE id = ?", (soil_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["properties"] = json.loads(d["properties"])
        d["depth_layers"] = json.loads(d["depth_layers"])
        return d

    def list_soils_in_region(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM soil_profiles
            WHERE latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
            """,
            (min_lat, max_lat, min_lon, max_lon),
        ).fetchall()
        return [
            {
                **dict(r),
                "properties": json.loads(r["properties"]),
                "depth_layers": json.loads(r["depth_layers"]),
            }
            for r in rows
        ]

    # ---- Crop-Soil Matches ----
    def save_match(self, match: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO crop_soil_matches
                (id, crop_id, soil_id, suitability_score, matching_traits)
            VALUES (:id, :crop_id, :soil_id, :suitability_score, :matching_traits)
            ON CONFLICT(id) DO UPDATE SET
                suitability_score=excluded.suitability_score,
                matching_traits=excluded.matching_traits
            """,
            {
                **match,
                "matching_traits": json.dumps(match.get("matching_traits", {})),
            },
        )
        self.conn.commit()

    def get_matches_for_crop(self, crop_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM crop_soil_matches
            WHERE crop_id = ?
            ORDER BY suitability_score DESC
            """,
            (crop_id,),
        ).fetchall()
        return [
            {**dict(r), "matching_traits": json.loads(r["matching_traits"])}
            for r in rows
        ]

    # ---- Pests & Diseases ----
    def upsert_pest(self, pest: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO pests_diseases
                (id, name, type, affected_crops, symptoms, treatments)
            VALUES (:id, :name, :type, :affected_crops, :symptoms, :treatments)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                type=excluded.type,
                affected_crops=excluded.affected_crops,
                symptoms=excluded.symptoms,
                treatments=excluded.treatments
            """,
            {
                **pest,
                "affected_crops": json.dumps(pest.get("affected_crops", [])),
                "symptoms": json.dumps(pest.get("symptoms", [])),
                "treatments": json.dumps(pest.get("treatments", [])),
            },
        )
        self.conn.commit()

    def find_pests_by_crop(self, crop_name: str) -> list[dict[str, Any]]:
        """Fuzzy-match crop name against affected_crops JSON."""
        rows = self.conn.execute(
            "SELECT * FROM pests_diseases WHERE affected_crops LIKE ?",
            (f"%{crop_name}%",),
        ).fetchall()
        return [
            {
                **dict(r),
                "affected_crops": json.loads(r["affected_crops"]),
                "symptoms": json.loads(r["symptoms"]),
                "treatments": json.loads(r["treatments"]),
            }
            for r in rows
        ]

    # ---- Seasonal Patterns ----
    def upsert_seasonal(self, pattern: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO seasonal_patterns
                (id, crop_id, region, planting_months, harvest_months, growth_duration_days)
            VALUES (:id, :crop_id, :region, :planting_months, :harvest_months, :growth_duration_days)
            ON CONFLICT(id) DO UPDATE SET
                region=excluded.region,
                planting_months=excluded.planting_months,
                harvest_months=excluded.harvest_months,
                growth_duration_days=excluded.growth_duration_days
            """,
            {
                **pattern,
                "planting_months": json.dumps(pattern.get("planting_months", [])),
                "harvest_months": json.dumps(pattern.get("harvest_months", [])),
            },
        )
        self.conn.commit()

    def get_seasonal(self, crop_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM seasonal_patterns WHERE crop_id = ?", (crop_id,)
        ).fetchall()
        return [
            {
                **dict(r),
                "planting_months": json.loads(r["planting_months"]),
                "harvest_months": json.loads(r["harvest_months"]),
            }
            for r in rows
        ]

    # ---- Weather Interactions ----
    def upsert_weather(self, weather: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO weather_interactions
                (id, crop_id, temperature_range, rainfall_range, humidity_range, optimal_conditions)
            VALUES (:id, :crop_id, :temperature_range, :rainfall_range, :humidity_range, :optimal_conditions)
            ON CONFLICT(id) DO UPDATE SET
                temperature_range=excluded.temperature_range,
                rainfall_range=excluded.rainfall_range,
                humidity_range=excluded.humidity_range,
                optimal_conditions=excluded.optimal_conditions
            """,
            {
                **weather,
                "temperature_range": json.dumps(weather.get("temperature_range", {})),
                "rainfall_range": json.dumps(weather.get("rainfall_range", {})),
                "humidity_range": json.dumps(weather.get("humidity_range", {})),
                "optimal_conditions": json.dumps(weather.get("optimal_conditions", {})),
            },
        )
        self.conn.commit()

    def get_weather(self, crop_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM weather_interactions WHERE crop_id = ?", (crop_id,)
        ).fetchall()
        return [
            {
                **dict(r),
                "temperature_range": json.loads(r["temperature_range"]),
                "rainfall_range": json.loads(r["rainfall_range"]),
                "humidity_range": json.loads(r["humidity_range"]),
                "optimal_conditions": json.loads(r["optimal_conditions"]),
            }
            for r in rows
        ]

    def close(self) -> None:
        self.conn.close()
