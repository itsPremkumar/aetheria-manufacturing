"""
crop_ontology_soilgrids.py — Crop Ontology and SoilGrids Integration.

Provides standardized crop and soil classifications:
- Crop Ontology: standardized crop trait definitions
- SoilGrids: global soil property mappings
- Integration with the Agriculture KG
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json


@dataclass
class CropTrait:
    """A standardized crop trait from Crop Ontology."""
    trait_id: str
    name: str
    description: str
    category: str
    measurement_unit: str
    min_value: float | None = None
    max_value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "trait_id": self.trait_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "measurement_unit": self.measurement_unit,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }


@dataclass
class SoilProperty:
    """A soil property from SoilGrids."""
    property_id: str
    name: str
    description: str
    unit: str
    depth: str  # soil depth (e.g., "0-5cm")
    value_range: tuple[float, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "property_id": self.property_id,
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "depth": self.depth,
            "value_range": self.value_range,
        }


class CropOntology:
    """
    Crop Ontology: standardized crop trait definitions.
    """

    def __init__(self):
        self.traits: dict[str, CropTrait] = {}
        self._load_default_traits()

    def _load_default_traits(self):
        """Load default crop traits."""
        traits = [
            CropTrait("trait_plant_height", "Plant Height", "Height of the plant from ground to tip", "morphology", "cm", 10.0, 300.0),
            CropTrait("trait_leaf_area", "Leaf Area", "Surface area of a single leaf", "morphology", "cm2", 5.0, 500.0),
            CropTrait("trait_root_depth", "Root Depth", "Maximum depth of root system", "morphology", "cm", 10.0, 200.0),
            CropTrait("trait_growth_duration", "Growth Duration", "Days from planting to maturity", "phenology", "days", 60.0, 365.0),
            CropTrait("trait_yield", "Yield", "Grain or biomass yield per unit area", "productivity", "t/ha", 0.5, 15.0),
            CropTrait("trait_drought_tolerance", "Drought Tolerance", "Ability to withstand water stress", "stress_tolerance", "index", 0.0, 1.0),
            CropTrait("trait_salt_tolerance", "Salt Tolerance", "Ability to withstand soil salinity", "stress_tolerance", "dS/m", 0.0, 20.0),
            CropTrait("trait_nutrient_use_efficiency", "Nutrient Use Efficiency", "Biomass produced per unit nutrient", "nutrition", "kg/kg", 10.0, 100.0),
            CropTrait("trait_lai", "Leaf Area Index", "Total leaf area per unit ground area", "morphology", "m2/m2", 0.5, 8.0),
            CropTrait("trait_harvest_index", "Harvest Index", "Ratio of grain yield to total biomass", "productivity", "ratio", 0.2, 0.6),
        ]
        for trait in traits:
            self.traits[trait.trait_id] = trait

    def get_trait(self, trait_id: str) -> CropTrait | None:
        """Get a trait by ID."""
        return self.traits.get(trait_id)

    def search_traits(self, query: str) -> list[CropTrait]:
        """Search traits by name or description."""
        query_lower = query.lower()
        return [t for t in self.traits.values() if query_lower in t.name.lower() or query_lower in t.description.lower()]

    def get_traits_by_category(self, category: str) -> list[CropTrait]:
        """Get traits by category."""
        return [t for t in self.traits.values() if t.category == category]

    def get_categories(self) -> list[str]:
        """Get all trait categories."""
        return list(set(t.category for t in self.traits.values()))

    def list_traits(self) -> list[CropTrait]:
        """List all traits."""
        return list(self.traits.values())


class SoilGrids:
    """
    SoilGrids: global soil property mappings.
    """

    def __init__(self):
        self.properties: dict[str, SoilProperty] = {}
        self._load_default_properties()

    def _load_default_properties(self):
        """Load default soil properties."""
        properties = [
            SoilProperty("soil_ph", "Soil pH", "Soil pH measured in water", "pH", "0-5cm", (3.5, 9.5)),
            SoilProperty("soil_organic_carbon", "Soil Organic Carbon", "Organic carbon content", "g/kg", "0-5cm", (0.0, 100.0)),
            SoilProperty("soil_clay", "Clay Content", "Percentage of clay particles", "%", "0-5cm", (0.0, 80.0)),
            SoilProperty("soil_silt", "Silt Content", "Percentage of silt particles", "%", "0-5cm", (0.0, 80.0)),
            SoilProperty("soil_sand", "Sand Content", "Percentage of sand particles", "%", "0-5cm", (0.0, 100.0)),
            SoilProperty("soil_bulk_density", "Bulk Density", "Soil bulk density", "kg/m3", "0-5cm", (800.0, 1800.0)),
            SoilProperty("soil_cec", "Cation Exchange Capacity", "Ability to hold cations", "cmolc/kg", "0-5cm", (0.0, 100.0)),
            SoilProperty("soil_water_capacity", "Water Holding Capacity", "Available water capacity", "mm/m", "0-5cm", (50.0, 300.0)),
            SoilProperty("soil_electrical_conductivity", "Electrical Conductivity", "Soil salinity indicator", "dS/m", "0-5cm", (0.0, 16.0)),
            SoilProperty("soil_nitrogen", "Nitrogen Content", "Total nitrogen content", "g/kg", "0-5cm", (0.0, 10.0)),
        ]
        for prop in properties:
            self.properties[prop.property_id] = prop

    def get_property(self, property_id: str) -> SoilProperty | None:
        """Get a soil property by ID."""
        return self.properties.get(property_id)

    def search_properties(self, query: str) -> list[SoilProperty]:
        """Search properties by name or description."""
        query_lower = query.lower()
        return [p for p in self.properties.values() if query_lower in p.name.lower() or query_lower in p.description.lower()]

    def get_properties_by_depth(self, depth: str) -> list[SoilProperty]:
        """Get properties by soil depth."""
        return [p for p in self.properties.values() if p.depth == depth]

    def list_properties(self) -> list[SoilProperty]:
        """List all properties."""
        return list(self.properties.values())


class OntologyIntegrator:
    """
    Integrates Crop Ontology and SoilGrids with the Agriculture KG.
    """

    def __init__(self, agri_graph: Any = None):
        self.crop_ontology = CropOntology()
        self.soil_grids = SoilGrids()
        self.agri_graph = agri_graph

    def get_crop_traits_for_crop(self, crop_id: str) -> list[CropTrait]:
        """Get relevant traits for a specific crop."""
        # Return all traits as defaults
        return self.crop_ontology.list_traits()

    def get_soil_properties_for_soil(self, soil_id: str) -> list[SoilProperty]:
        """Get relevant properties for a specific soil type."""
        return self.soil_grids.list_properties()

    def standardize_crop_name(self, name: str) -> str:
        """Standardize crop name using ontology."""
        # Simple standardization
        name_lower = name.lower().strip()
        # Common mappings
        mappings = {
            "wheat": "Triticum aestivum",
            "rice": "Oryza sativa",
            "maize": "Zea mays",
            "corn": "Zea mays",
            "soybean": "Glycine max",
            "cotton": "Gossypium hirsutum",
            "potato": "Solanum tuberosum",
            "tomato": "Solanum lycopersicum",
            "groundnut": "Arachis hypogaea",
        }
        return mappings.get(name_lower, name)

    def standardize_soil_name(self, name: str) -> str:
        """Standardize soil name using SoilGrids taxonomy."""
        name_lower = name.lower().strip()
        mappings = {
            "loam": "Loam",
            "clay": "Clay",
            "sandy": "Sand",
            "silt": "Silt",
            "peat": "Peat",
            "chalk": "Chalk",
        }
        return mappings.get(name_lower, name)

    def map_crop_to_soil_requirements(self, crop_id: str) -> dict[str, Any]:
        """Map crop to soil requirements using ontology."""
        return {
            "ph_range": (5.5, 7.5),
            "drainage": "good",
            "organic_matter": "medium",
            "texture": "loam",
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get integrator statistics."""
        return {
            "total_traits": len(self.crop_ontology.traits),
            "total_soil_properties": len(self.soil_grids.properties),
            "trait_categories": self.crop_ontology.get_categories(),
        }
