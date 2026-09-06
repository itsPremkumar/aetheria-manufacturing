"""Tests for crop_ontology_soilgrids.py."""

import pytest
from crop_ontology_soilgrids import (
    CropTrait, SoilProperty, CropOntology, SoilGrids, OntologyIntegrator,
)


class TestCropTrait:
    def test_trait_fields(self):
        trait = CropTrait(
            trait_id="trait_test",
            name="Test Trait",
            description="A test trait",
            category="morphology",
            measurement_unit="cm",
            min_value=0.0,
            max_value=100.0,
        )
        assert trait.trait_id == "trait_test"
        assert trait.name == "Test Trait"
        assert trait.category == "morphology"

    def test_trait_to_dict(self):
        trait = CropTrait(
            trait_id="trait_test",
            name="Test",
            description="Test",
            category="test",
            measurement_unit="cm",
        )
        d = trait.to_dict()
        assert d["trait_id"] == "trait_test"


class TestSoilProperty:
    def test_property_fields(self):
        prop = SoilProperty(
            property_id="prop_test",
            name="Test Property",
            description="A test property",
            unit="cm",
            depth="0-5cm",
            value_range=(0.0, 100.0),
        )
        assert prop.property_id == "prop_test"
        assert prop.name == "Test Property"

    def test_property_to_dict(self):
        prop = SoilProperty(
            property_id="prop_test",
            name="Test",
            description="Test",
            unit="cm",
            depth="0-5cm",
            value_range=(0.0, 100.0),
        )
        d = prop.to_dict()
        assert d["property_id"] == "prop_test"


class TestCropOntology:
    def test_default_traits_loaded(self):
        ontology = CropOntology()
        assert len(ontology.traits) >= 8

    def test_get_trait(self):
        ontology = CropOntology()
        trait = ontology.get_trait("trait_plant_height")
        assert trait is not None
        assert trait.name == "Plant Height"

    def test_get_trait_invalid(self):
        ontology = CropOntology()
        trait = ontology.get_trait("invalid")
        assert trait is None

    def test_search_traits(self):
        ontology = CropOntology()
        results = ontology.search_traits("height")
        assert len(results) > 0

    def test_get_traits_by_category(self):
        ontology = CropOntology()
        traits = ontology.get_traits_by_category("morphology")
        assert len(traits) > 0

    def test_get_categories(self):
        ontology = CropOntology()
        categories = ontology.get_categories()
        assert len(categories) > 0
        assert "morphology" in categories

    def test_list_traits(self):
        ontology = CropOntology()
        traits = ontology.list_traits()
        assert len(traits) >= 8


class TestSoilGrids:
    def test_default_properties_loaded(self):
        grids = SoilGrids()
        assert len(grids.properties) >= 8

    def test_get_property(self):
        grids = SoilGrids()
        prop = grids.get_property("soil_ph")
        assert prop is not None
        assert prop.name == "Soil pH"

    def test_get_property_invalid(self):
        grids = SoilGrids()
        prop = grids.get_property("invalid")
        assert prop is None

    def test_search_properties(self):
        grids = SoilGrids()
        results = grids.search_properties("clay")
        assert len(results) > 0

    def test_get_properties_by_depth(self):
        grids = SoilGrids()
        props = grids.get_properties_by_depth("0-5cm")
        assert len(props) > 0

    def test_list_properties(self):
        grids = SoilGrids()
        props = grids.list_properties()
        assert len(props) >= 8


class TestOntologyIntegrator:
    def test_initialization(self):
        integrator = OntologyIntegrator()
        assert integrator.crop_ontology is not None
        assert integrator.soil_grids is not None

    def test_get_crop_traits_for_crop(self):
        integrator = OntologyIntegrator()
        traits = integrator.get_crop_traits_for_crop("wheat_001")
        assert len(traits) > 0

    def test_get_soil_properties_for_soil(self):
        integrator = OntologyIntegrator()
        props = integrator.get_soil_properties_for_soil("loam_001")
        assert len(props) > 0

    def test_standardize_crop_name(self):
        integrator = OntologyIntegrator()
        assert integrator.standardize_crop_name("wheat") == "Triticum aestivum"
        assert integrator.standardize_crop_name("rice") == "Oryza sativa"
        assert integrator.standardize_crop_name("unknown") == "unknown"

    def test_standardize_soil_name(self):
        integrator = OntologyIntegrator()
        assert integrator.standardize_soil_name("loam") == "Loam"
        assert integrator.standardize_soil_name("clay") == "Clay"
        assert integrator.standardize_soil_name("unknown") == "unknown"

    def test_map_crop_to_soil_requirements(self):
        integrator = OntologyIntegrator()
        reqs = integrator.map_crop_to_soil_requirements("wheat_001")
        assert "ph_range" in reqs
        assert "drainage" in reqs
        assert "texture" in reqs

    def test_get_statistics(self):
        integrator = OntologyIntegrator()
        stats = integrator.get_statistics()
        assert stats["total_traits"] >= 8
        assert stats["total_soil_properties"] >= 8
        assert "trait_categories" in stats
