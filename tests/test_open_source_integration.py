"""Tests for agriculture KG open-source integrations (USDA, FAO, WorldClim, SoilGrids, CHIRPS)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from aetheria_manufacturing.agriculture_kg.opensource_integration import (
    USDAIntegration,
    FAOIntegration,
    WorldClimIntegration,
    SoilGridsIntegration,
    CHIRPSIntegration,
    AgriOpenSourceIntegrator,
    CropProductionRecord,
    ClimateRecord,
    SoilDataRecord,
)


class TestCropProductionRecord:
    def test_to_dict(self):
        record = CropProductionRecord(
            record_id="test_001",
            crop_name="Wheat",
            region="Kansas",
            year=2023,
            area_harvested=3500000,
            production=10500000,
            yield_per_hectare=3.0,
            source="USDA NASS",
        )
        d = record.to_dict()
        assert d["record_id"] == "test_001"
        assert d["crop_name"] == "Wheat"

    def test_record_fields(self):
        record = CropProductionRecord(
            record_id="r1",
            crop_name="Corn",
            region="Iowa",
            year=2024,
            area_harvested=1000,
            production=5000,
            yield_per_hectare=5.0,
            source="Test",
        )
        assert record.crop_name == "Corn"
        assert record.region == "Iowa"


class TestUSDAIntegration:
    def test_sample_data_loaded(self):
        usda = USDAIntegration()
        assert len(usda.records) >= 3

    def test_get_all_records(self):
        usda = USDAIntegration()
        records = usda.list_records()
        assert len(records) > 0
        assert all(isinstance(r, CropProductionRecord) for r in records)

    def test_get_records_by_crop(self):
        usda = USDAIntegration()
        wheat_records = usda.get_records(crop_name="Wheat")
        assert len(wheat_records) > 0
        assert all(r.crop_name == "Wheat" for r in wheat_records)

    def test_get_records_by_region(self):
        usda = USDAIntegration()
        kansas_records = usda.get_records(region="Kansas")
        assert len(kansas_records) > 0
        assert all(r.region == "Kansas" for r in kansas_records)

    def test_get_records_no_match(self):
        usda = USDAIntegration()
        records = usda.get_records(crop_name="NonexistentCrop")
        assert len(records) == 0

    def test_average_yield(self):
        usda = USDAIntegration()
        avg = usda.get_average_yield("Wheat")
        assert avg > 0

    def test_average_yield_no_match(self):
        usda = USDAIntegration()
        avg = usda.get_average_yield("Nonexistent")
        assert avg == 0.0

    def test_record_to_dict(self):
        usda = USDAIntegration()
        records = usda.list_records()
        d = records[0].to_dict()
        assert "record_id" in d
        assert "crop_name" in d
        assert "region" in d


class TestFAOIntegration:
    def test_sample_data_loaded(self):
        fao = FAOIntegration()
        assert len(fao.records) >= 3

    def test_get_records_by_crop(self):
        fao = FAOIntegration()
        rice_records = fao.get_records(crop_name="Rice")
        assert len(rice_records) > 0
        assert all(r.crop_name == "Rice" for r in rice_records)

    def test_get_records_by_region(self):
        fao = FAOIntegration()
        india_records = fao.get_records(region="India")
        assert len(india_records) > 0

    def test_get_global_production(self):
        fao = FAOIntegration()
        global_rice = fao.get_global_production("Rice")
        assert global_rice > 0

    def test_get_global_production_no_match(self):
        fao = FAOIntegration()
        prod = fao.get_global_production("Nonexistent")
        assert prod == 0.0


class TestWorldClimIntegration:
    def test_sample_data_loaded(self):
        wc = WorldClimIntegration()
        assert len(wc.records) >= 4

    def test_get_records_by_region(self):
        wc = WorldClimIntegration()
        india_records = wc.get_records(region="India")
        assert len(india_records) > 0
        assert all(r.region == "India" for r in india_records)

    def test_get_records_by_month(self):
        wc = WorldClimIntegration()
        jan_records = wc.get_records(month=1)
        assert len(jan_records) > 0
        assert all(r.month == 1 for r in jan_records)

    def test_get_average_temperature(self):
        wc = WorldClimIntegration()
        avg = wc.get_average_temperature("India")
        assert avg > 0

    def test_get_average_temperature_no_match(self):
        wc = WorldClimIntegration()
        avg = wc.get_average_temperature("Nonexistent")
        assert avg == 0.0

    def test_get_total_rainfall(self):
        wc = WorldClimIntegration()
        total = wc.get_total_rainfall("India")
        assert total > 0


class TestSoilGridsIntegration:
    def test_sample_data_loaded(self):
        sg = SoilGridsIntegration()
        assert len(sg.records) >= 3

    def test_get_records_by_region(self):
        sg = SoilGridsIntegration()
        punjab_records = sg.get_records(region="Punjab")
        assert len(punjab_records) > 0

    def test_get_records_by_soil_type(self):
        sg = SoilGridsIntegration()
        loam_records = sg.get_records(soil_type="Loam")
        assert len(loam_records) > 0

    def test_get_average_ph(self):
        sg = SoilGridsIntegration()
        avg = sg.get_average_ph("Punjab")
        assert avg > 0

    def test_get_average_ph_no_match(self):
        sg = SoilGridsIntegration()
        avg = sg.get_average_ph("Nonexistent")
        assert avg == 0.0


class TestCHIRPSIntegration:
    def test_sample_data_loaded(self):
        chirps = CHIRPSIntegration()
        assert len(chirps.records) >= 2

    def test_get_records_by_region(self):
        chirps = CHIRPSIntegration()
        india_records = chirps.get_records(region="India")
        assert len(india_records) > 0

    def test_get_monsoon_rainfall(self):
        chirps = CHIRPSIntegration()
        rainfall = chirps.get_monsoon_rainfall("India")
        assert rainfall > 0

    def test_get_monsoon_rainfall_no_match(self):
        chirps = CHIRPSIntegration()
        rainfall = chirps.get_monsoon_rainfall("Nonexistent")
        assert rainfall == 0.0


class TestAgriOpenSourceIntegrator:
    def test_initialization(self):
        integrator = AgriOpenSourceIntegrator()
        assert integrator.usda is not None
        assert integrator.fao is not None
        assert integrator.worldclim is not None
        assert integrator.soilgrids is not None
        assert integrator.chirps is not None

    def test_get_crop_summary(self):
        integrator = AgriOpenSourceIntegrator()
        summary = integrator.get_crop_summary("Wheat")
        assert summary["crop"] == "Wheat"
        assert "usda_records" in summary
        assert "fao_records" in summary

    def test_get_crop_summary_no_match(self):
        integrator = AgriOpenSourceIntegrator()
        summary = integrator.get_crop_summary("NonexistentCrop")
        assert summary["crop"] == "NonexistentCrop"
        assert summary["usda_records"] == 0
        assert summary["fao_records"] == 0

    def test_get_region_summary(self):
        integrator = AgriOpenSourceIntegrator()
        summary = integrator.get_region_summary("India")
        assert summary["region"] == "India"
        assert "avg_temperature" in summary
        assert "total_rainfall" in summary

    def test_get_region_summary_no_match(self):
        integrator = AgriOpenSourceIntegrator()
        summary = integrator.get_region_summary("NonexistentRegion")
        assert summary["region"] == "NonexistentRegion"
        assert summary["avg_temperature"] == 0

    def test_get_statistics(self):
        integrator = AgriOpenSourceIntegrator()
        stats = integrator.get_statistics()
        assert stats["usda_records"] > 0
        assert stats["fao_records"] > 0
        assert stats["worldclim_records"] > 0
        assert stats["soilgrids_records"] > 0
        assert stats["chirps_records"] > 0


class TestClimateRecord:
    def test_to_dict(self):
        record = ClimateRecord(
            record_id="test_climate",
            region="India",
            month=7,
            temperature_avg=30.0,
            rainfall=250.0,
            humidity=85.0,
            source="WorldClim",
        )
        d = record.to_dict()
        assert d["record_id"] == "test_climate"
        assert d["region"] == "India"
        assert d["month"] == 7


class TestSoilDataRecord:
    def test_to_dict(self):
        record = SoilDataRecord(
            record_id="test_soil",
            region="Punjab",
            latitude=31.0,
            longitude=75.0,
            soil_type="Loam",
            ph=7.2,
            organic_carbon=0.8,
            clay_content=25.0,
            sand_content=35.0,
            source="SoilGrids",
        )
        d = record.to_dict()
        assert d["record_id"] == "test_soil"
        assert d["region"] == "Punjab"
        assert d["soil_type"] == "Loam"
