"""Knowledge graph reasoning engine for agriculture data."""

from __future__ import annotations

import json
import uuid
from typing import Any

from .database import Database


# ---------------------------------------------------------------------------
# Crop-soil matching heuristics
# ---------------------------------------------------------------------------

# Preferred soil pH ranges (pH * 10 as in SoilGrids) per crop family
CROP_PH_PREFERENCE: dict[str, tuple[int, int]] = {
    "Fabaceae": (55, 70),   # 5.5–7.0
    "Poaceae":  (55, 75),   # 5.5–7.5
    "Solanaceae": (55, 70),
    "Brassicaceae": (60, 75),
    "Cucurbitaceae": (55, 70),
    "default": (55, 75),
}

# Preferred clay content range (g/kg) per crop family
_CLAY_PREF: dict[str, tuple[int, int]] = {
    "Fabaceae": (150, 400),
    "Poaceae":  (100, 350),
    "Solanaceae": (100, 300),
    "default": (100, 400),
}


class CropSoilMatcher:
    """Score how suitable a soil profile is for a given crop."""

    def __init__(self, db: Database):
        self.db = db

    def _score_ph(self, ph: int, family: str) -> float:
        lo, hi = CROP_PH_PREFERENCE.get(family, CROP_PH_PREFERENCE["default"])
        if lo <= ph <= hi:
            return 1.0
        dist = min(abs(ph - lo), abs(ph - hi))
        return max(0.0, 1.0 - dist / 50.0)

    def _score_clay(self, clay: int, family: str) -> float:
        lo, hi = _CLAY_PREF.get(family, _CLAY_PREF["default"])
        if lo <= clay <= hi:
            return 1.0
        dist = min(abs(clay - lo), abs(clay - hi))
        return max(0.0, 1.0 - dist / 400.0)

    def _score_cec(self, cec: int) -> float:
        """Cation exchange capacity — higher is generally better, up to a point."""
        return min(1.0, cec / 30.0)

    def match(self, crop_id: str, soil_id: str) -> dict[str, Any]:
        """Compute suitability score between a crop and a soil profile."""
        crop = self.db.get_crop(crop_id)
        soil = self.db.get_soil(soil_id)
        if crop is None or soil is None:
            raise ValueError("crop or soil not found")

        props = soil["properties"]
        family = crop.get("family", "default")

        ph_raw = props.get("phh2o", 70)  # SoilGrids stores pH * 10
        clay = props.get("clay", 200)
        cec = props.get("cec", 15)

        scores = {
            "ph": self._score_ph(int(ph_raw), family),
            "clay": self._score_clay(int(clay), family),
            "cec": self._score_cec(int(cec)),
        }
        overall = sum(scores.values()) / len(scores)

        match = {
            "id": str(uuid.uuid4()),
            "crop_id": crop_id,
            "soil_id": soil_id,
            "suitability_score": round(overall, 4),
            "matching_traits": {
                "crop_family": family,
                "soil_properties_used": props,
                "component_scores": scores,
            },
        }
        self.db.save_match(match)
        return match

    def match_all_soils(self, crop_id: str) -> list[dict[str, Any]]:
        """Match a crop against all cached soil profiles."""
        # Fetch all soils via a broad bounding box
        soils = self.db.list_soils_in_region(-90, 90, -180, 180)
        return [self.match(crop_id, s["id"]) for s in soils]


class PestDiseaseIdentifier:
    """Identify pests and diseases affecting a crop."""

    def __init__(self, db: Database):
        self.db = db

    def identify(self, crop_name: str) -> list[dict[str, Any]]:
        """Return pests/diseases known to affect *crop_name*."""
        return self.db.find_pests_by_crop(crop_name)


class SeasonalReasoner:
    """Reason about planting/harvest windows."""

    def __init__(self, db: Database):
        self.db = db

    def get_planting_window(self, crop_id: str, region: str | None = None) -> list[dict[str, Any]]:
        """Return planting months for a crop, optionally filtered by region."""
        patterns = self.db.get_seasonal(crop_id)
        if region:
            patterns = [p for p in patterns if p.get("region") == region]
        return patterns

    def is_planting_season(self, crop_id: str, month: int, region: str | None = None) -> bool:
        """Check if a given month (1-12) falls within the planting window."""
        patterns = self.get_planting_window(crop_id, region)
        return any(month in p.get("planting_months", []) for p in patterns)


class WeatherMapper:
    """Map weather interactions for crops."""

    def __init__(self, db: Database):
        self.db = db

    def get_optimal_conditions(self, crop_id: str) -> list[dict[str, Any]]:
        """Return optimal weather conditions for a crop."""
        records = self.db.get_weather(crop_id)
        return [r.get("optimal_conditions", {}) for r in records]

    def is_suitable_weather(
        self, crop_id: str, temperature: float, rainfall: float
    ) -> dict[str, Any]:
        """Check if current weather is within crop's tolerance."""
        records = self.db.get_weather(crop_id)
        for rec in records:
            t_range = rec.get("temperature_range", {})
            r_range = rec.get("rainfall_range", {})
            t_ok = (
                t_range.get("min", -50) <= temperature <= t_range.get("max", 60)
            )
            r_ok = (
                r_range.get("min", 0) <= rainfall <= r_range.get("max", 10000)
            )
            if t_ok and r_ok:
                return {"suitable": True, "record": rec}
        return {"suitable": False, "record": None}
