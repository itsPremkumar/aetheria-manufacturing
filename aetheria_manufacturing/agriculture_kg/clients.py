"""API clients with offline cache for Crop Ontology and SoilGrids."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


class BaseClient:
    """Base class for API clients with file-based cache."""

    def __init__(self, cache_dir: str | Path, ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.session = requests.Session()

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            return None
        if time.time() - path.stat().st_mtime > self.ttl:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _cache_put(self, key: str, data: dict[str, Any]) -> None:
        path = self.cache_dir / f"{key}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _get(self, url: str, params: dict | None = None) -> dict[str, Any]:
        """GET with cache. Falls back to cache on network failure (offline-first)."""
        cache_key = url.replace("/", "_").replace(":", "_")
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache hit: %s", url)
            return cached

        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            self._cache_put(cache_key, data)
            return data
        except requests.RequestException as exc:
            logger.warning("Network error, using stale cache if available: %s", exc)
            # Try stale cache
            path = self.cache_dir / f"{cache_key}.json"
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
            raise


class CropOntologyClient(BaseClient):
    """Client for the Crop Ontology API (cropontology.org)."""

    BASE_URL = "https://cropontology.org/api"

    def list_crops(self) -> list[dict[str, Any]]:
        """Fetch the list of crops from CO."""
        data = self._get(f"{self.BASE_URL}/crops/")
        return data.get("crops", data.get("results", []))

    def get_crop(self, crop_id: str) -> dict[str, Any]:
        """Fetch a single crop by ID."""
        return self._get(f"{self.BASE_URL}/crops/{crop_id}/")

    def list_traits(self) -> list[dict[str, Any]]:
        """Fetch all traits."""
        data = self._get(f"{self.BASE_URL}/traits/")
        return data.get("traits", data.get("results", []))

    def get_trait(self, trait_id: str) -> dict[str, Any]:
        """Fetch a single trait by ID."""
        return self._get(f"{self.BASE_URL}/traits/{trait_id}/")


class SoilGridsClient(BaseClient):
    """Client for the SoilGrids API (ISRIC)."""

    BASE_URL = "https://rest.isric.org/soilgrids/v2.0"

    def get_properties(self) -> dict[str, Any]:
        """List available soil properties."""
        return self._get(f"{self.BASE_URL}/properties")

    def query_by_location(
        self, lat: float, lon: float, depth: str = "0-5cm"
    ) -> dict[str, Any]:
        """Query soil properties at a specific location.

        Args:
            lat: Latitude
            lon: Longitude
            depth: Soil depth layer (e.g., "0-5cm", "5-15cm")
        """
        return self._get(
            f"{self.BASE_URL}/properties/query",
            params={"lat": lat, "lon": lon, "depth": depth},
        )

    def query_location(self, lat: float, lon: float) -> dict[str, Any]:
        """Get all soil data for a coordinate."""
        return self._get(
            f"{self.BASE_URL}/location",
            params={"lat": lat, "lon": lon},
        )
