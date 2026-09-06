"""
agri_opensource_integration.py — Agriculture KG Open-Source Integration.

Integrates with open-source agriculture datasets:
- USDA NASS: crop production statistics
- FAO STAT: global food and agriculture data
- WorldClim: global climate data
- SoilGrids: global soil property maps
- CHIRPS: rainfall estimates

Provides offline-first integration with sample data.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json


@dataclass
class CropProductionRecord:
    """A crop production record."""
    record_id: str
    crop_name: str
    region: str
    year: int
    area_harvested: float  # hectares
    production: float  # tonnes
    yield_per_hectare: float  # t/ha
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "crop_name": self.crop_name,
            "region": self.region,
            "year": self.year,
            "area_harvested": self.area_harvested,
            "production": self.production,
            "yield_per_hectare": self.yield_per_hectare,
            "source": self.source,
        }


@dataclass
class ClimateRecord:
    """A climate record."""
    record_id: str
    region: str
    month: int
    temperature_avg: float
    rainfall: float
    humidity: float
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "region": self.region,
            "month": self.month,
            "temperature_avg": self.temperature_avg,
            "rainfall": self.rainfall,
            "humidity": self.humidity,
            "source": self.source,
        }


@dataclass
class SoilDataRecord:
    """A soil data record."""
    record_id: str
    region: str
    latitude: float
    longitude: float
    soil_type: str
    ph: float
    organic_carbon: float
    clay_content: float
    sand_content: float
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "soil_type": self.soil_type,
            "ph": self.ph,
            "organic_carbon": self.organic_carbon,
            "clay_content": self.clay_content,
            "sand_content": self.sand_content,
            "source": self.source,
        }


class USDAIntegration:
    """USDA NASS integration."""

    def __init__(self):
        self.records: list[CropProductionRecord] = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample USDA data."""
        self.records = [
            CropProductionRecord("usda_wheat_2023", "Wheat", "Kansas", 2023, 3500000, 10500000, 3.0, "USDA NASS"),
            CropProductionRecord("usda_corn_2023", "Corn", "Iowa", 2023, 5200000, 24000000, 4.6, "USDA NASS"),
            CropProductionRecord("usda_soybean_2023", "Soybean", "Illinois", 2023, 4100000, 12300000, 3.0, "USDA NASS"),
            CropProductionRecord("usda_rice_2023", "Rice", "Arkansas", 2023, 550000, 4400000, 8.0, "USDA NASS"),
            CropProductionRecord("usda_cotton_2023", "Cotton", "Texas", 2023, 2800000, 4200000, 1.5, "USDA NASS"),
        ]

    def get_records(self, crop_name: str | None = None, region: str | None = None) -> list[CropProductionRecord]:
        """Get production records."""
        results = self.records
        if crop_name:
            results = [r for r in results if r.crop_name.lower() == crop_name.lower()]
        if region:
            results = [r for r in results if r.region.lower() == region.lower()]
        return results

    def get_average_yield(self, crop_name: str) -> float:
        """Get average yield for a crop."""
        records = self.get_records(crop_name=crop_name)
        if not records:
            return 0.0
        return sum(r.yield_per_hectare for r in records) / len(records)

    def list_records(self) -> list[CropProductionRecord]:
        """List all records."""
        return self.records


class FAOIntegration:
    """FAO STAT integration."""

    def __init__(self):
        self.records: list[CropProductionRecord] = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample FAO data."""
        self.records = [
            CropProductionRecord("fao_wheat_india_2023", "Wheat", "India", 2023, 30000000, 110000000, 3.67, "FAO STAT"),
            CropProductionRecord("fao_rice_india_2023", "Rice", "India", 2023, 45000000, 135000000, 3.0, "FAO STAT"),
            CropProductionRecord("fao_rice_china_2023", "Rice", "China", 2023, 30000000, 210000000, 7.0, "FAO STAT"),
            CropProductionRecord("fao_corn_usa_2023", "Corn", "USA", 2023, 35000000, 385000000, 11.0, "FAO STAT"),
            CropProductionRecord("fao_soybean_brazil_2023", "Soybean", "Brazil", 2023, 40000000, 150000000, 3.75, "FAO STAT"),
        ]

    def get_records(self, crop_name: str | None = None, region: str | None = None) -> list[CropProductionRecord]:
        """Get production records."""
        results = self.records
        if crop_name:
            results = [r for r in results if r.crop_name.lower() == crop_name.lower()]
        if region:
            results = [r for r in results if r.region.lower() == region.lower()]
        return results

    def get_global_production(self, crop_name: str) -> float:
        """Get global production for a crop."""
        records = self.get_records(crop_name=crop_name)
        return sum(r.production for r in records)

    def list_records(self) -> list[CropProductionRecord]:
        """List all records."""
        return self.records


class WorldClimIntegration:
    """WorldClim climate data integration."""

    def __init__(self):
        self.records: list[ClimateRecord] = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample climate data."""
        self.records = [
            ClimateRecord("wc_india_jan", "India", 1, 15.0, 10.0, 55.0, "WorldClim"),
            ClimateRecord("wc_india_jun", "India", 6, 32.0, 150.0, 75.0, "WorldClim"),
            ClimateRecord("wc_india_jul", "India", 7, 30.0, 250.0, 85.0, "WorldClim"),
            ClimateRecord("wc_usa_jan", "USA", 1, 5.0, 50.0, 60.0, "WorldClim"),
            ClimateRecord("wc_usa_jul", "USA", 7, 25.0, 30.0, 55.0, "WorldClim"),
            ClimateRecord("wc_brazil_jan", "Brazil", 1, 28.0, 200.0, 80.0, "WorldClim"),
            ClimateRecord("wc_brazil_jul", "Brazil", 7, 22.0, 50.0, 65.0, "WorldClim"),
        ]

    def get_records(self, region: str | None = None, month: int | None = None) -> list[ClimateRecord]:
        """Get climate records."""
        results = self.records
        if region:
            results = [r for r in results if r.region.lower() == region.lower()]
        if month:
            results = [r for r in results if r.month == month]
        return results

    def get_average_temperature(self, region: str) -> float:
        """Get average temperature for a region."""
        records = self.get_records(region=region)
        if not records:
            return 0.0
        return sum(r.temperature_avg for r in records) / len(records)

    def get_total_rainfall(self, region: str) -> float:
        """Get total rainfall for a region."""
        records = self.get_records(region=region)
        return sum(r.rainfall for r in records)

    def list_records(self) -> list[ClimateRecord]:
        """List all records."""
        return self.records


class SoilGridsIntegration:
    """SoilGrids data integration."""

    def __init__(self):
        self.records: list[SoilDataRecord] = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample soil data."""
        self.records = [
            SoilDataRecord("sg_punjab_1", "Punjab", 31.0, 75.0, "Loam", 7.2, 0.8, 25.0, 35.0, "SoilGrids"),
            SoilDataRecord("sg_up_1", "Uttar Pradesh", 27.0, 80.0, "Clay", 7.5, 1.2, 40.0, 20.0, "SoilGrids"),
            SoilDataRecord("sg_karnataka_1", "Karnataka", 15.0, 75.0, "Sandy", 6.0, 0.5, 10.0, 70.0, "SoilGrids"),
            SoilDataRecord("sg_texas_1", "Texas", 31.0, -97.0, "Clay", 7.8, 1.5, 45.0, 15.0, "SoilGrids"),
            SoilDataRecord("sg_iowa_1", "Iowa", 42.0, -93.0, "Loam", 6.8, 2.0, 30.0, 30.0, "SoilGrids"),
        ]

    def get_records(self, region: str | None = None, soil_type: str | None = None) -> list[SoilDataRecord]:
        """Get soil records."""
        results = self.records
        if region:
            results = [r for r in results if r.region.lower() == region.lower()]
        if soil_type:
            results = [r for r in results if r.soil_type.lower() == soil_type.lower()]
        return results

    def get_average_ph(self, region: str) -> float:
        """Get average pH for a region."""
        records = self.get_records(region=region)
        if not records:
            return 0.0
        return sum(r.ph for r in records) / len(records)

    def list_records(self) -> list[SoilDataRecord]:
        """List all records."""
        return self.records


class CHIRPSIntegration:
    """CHIRPS rainfall data integration."""

    def __init__(self):
        self.records: list[ClimateRecord] = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample CHIRPS data."""
        self.records = [
            ClimateRecord("ch_india_monsoon", "India", 7, 28.0, 300.0, 90.0, "CHIRPS"),
            ClimateRecord("ch_india_post_monsoon", "India", 10, 25.0, 100.0, 70.0, "CHIRPS"),
            ClimateRecord("ch_ethiopia_belg", "Ethiopia", 4, 20.0, 150.0, 75.0, "CHIRPS"),
            ClimateRecord("ch_ethiopia_kiremt", "Ethiopia", 7, 18.0, 250.0, 80.0, "CHIRPS"),
        ]

    def get_records(self, region: str | None = None) -> list[ClimateRecord]:
        """Get rainfall records."""
        results = self.records
        if region:
            results = [r for r in results if r.region.lower() == region.lower()]
        return results

    def get_monsoon_rainfall(self, region: str) -> float:
        """Get monsoon rainfall for a region."""
        records = self.get_records(region=region)
        return sum(r.rainfall for r in records)

    def list_records(self) -> list[ClimateRecord]:
        """List all records."""
        return self.records


class AgriOpenSourceIntegrator:
    """
    Integrates all open-source agriculture data sources.
    """

    def __init__(self):
        self.usda = USDAIntegration()
        self.fao = FAOIntegration()
        self.worldclim = WorldClimIntegration()
        self.soilgrids = SoilGridsIntegration()
        self.chirps = CHIRPSIntegration()

    def get_crop_summary(self, crop_name: str) -> dict[str, Any]:
        """Get a summary for a crop across all sources."""
        usda_records = self.usda.get_records(crop_name=crop_name)
        fao_records = self.fao.get_records(crop_name=crop_name)

        return {
            "crop": crop_name,
            "usda_records": len(usda_records),
            "fao_records": len(fao_records),
            "average_yield_usda": self.usda.get_average_yield(crop_name) if usda_records else 0,
            "global_production_fao": self.fao.get_global_production(crop_name) if fao_records else 0,
        }

    def get_region_summary(self, region: str) -> dict[str, Any]:
        """Get a summary for a region across all sources."""
        climate = self.worldclim.get_records(region=region)
        soil = self.soilgrids.get_records(region=region)
        rainfall = self.chirps.get_records(region=region)

        return {
            "region": region,
            "avg_temperature": self.worldclim.get_average_temperature(region) if climate else 0,
            "total_rainfall": self.worldclim.get_total_rainfall(region) if climate else 0,
            "soil_records": len(soil),
            "avg_soil_ph": self.soilgrids.get_average_ph(region) if soil else 0,
            "monsoon_rainfall": self.chirps.get_monsoon_rainfall(region) if rainfall else 0,
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get integrator statistics."""
        return {
            "usda_records": len(self.usda.records),
            "fao_records": len(self.fao.records),
            "worldclim_records": len(self.worldclim.records),
            "soilgrids_records": len(self.soilgrids.records),
            "chirps_records": len(self.chirps.records),
        }
