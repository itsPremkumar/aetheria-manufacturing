# Agriculture KG — Integration Architecture

## Design Principles
1. **Offline-first:** All data cached locally; no runtime API calls
2. **Modular:** Each data source has its own adapter
3. **Extensible:** New crops/soil types plug in without code changes
4. **Testable:** All components unit-testable with mock data

## Component Architecture

```
src/
├── __init__.py
├── config.py              # Paths, constants, crop/soil parameters
├── models.py              # Pydantic/dataclass entity models
├── adapters/
│   ├── __init__.py
│   ├── base.py            # Abstract adapter interface
│   ├── crop_ontology.py   # Crop Ontology local data adapter
│   └── soilgrids.py       # SoilGrids local raster adapter
├── kg/
│   ├── __init__.py
│   ├── builder.py         # Build KG from adapter outputs
│   ├── store.py           # SQLite-backed triple store
│   └── query.py           # SPARQL-like query engine (simplified)
├── reasoning/
│   ├── __init__.py
│   ├── matcher.py         # Crop-soil matching algorithm
│   ├── pest.py            # Pest/disease identification
│   └── seasonal.py        # Seasonal pattern reasoning
├── cli.py                 # Command-line interface
└── api.py                 # REST API (FastAPI)
```

## Data Model

### Entities
```python
@dataclass
class Crop:
    id: str           # e.g., "wheat"
    name: str         # e.g., "Wheat (Triticum aestivum)"
    ph_min: float     # Minimum soil pH
    ph_max: float     # Maximum soil pH
    rainfall_min: int # mm/year minimum
    rainfall_max: int # mm/year maximum
    temp_min: float   # °C minimum growing temp
    temp_max: float   # °C maximum growing temp
    soil_texture: list # Preferred textures: ["loam", "clay_loam"]
    nutrients: list   # Key nutrients: ["N", "P", "K"]
    traits: dict      # Crop Ontology traits

@dataclass
class Soil:
    id: str
    latitude: float
    longitude: float
    ph: float
    organic_carbon: float  # g/kg
    clay_percent: float
    sand_percent: float
    silt_percent: float
    cec: float            # cmolc/kg
    bulk_density: float   # kg/m³
    texture_class: str    # USDA texture class

@dataclass
class Pest:
    id: str
    name: str
    affected_crops: list
    symptoms: list
    conditions: dict      # Favoring conditions (temp, humidity)

@dataclass
class Nutrient:
    id: str
    name: str
    function: str
    deficiency_symptoms: list
    sources: list
```

### Relations
- `(Crop)-[GROWS_IN]->(Soil)` — compatibility score 0-1
- `(Crop)-[REQUIRES]->(Nutrient)` — essential nutrient
- `(Crop)-[SUSCEPTIBLE_TO]->(Pest)` — pest vulnerability
- `(Crop)-[OPTIMAL_SEASON]->(Season)` — planting/harvest window
- `(Pest)-[FAVOURS]->(Condition)` — environmental triggers

## Crop-Soil Matching Algorithm

```
score = weighted_sum(
    ph_compatibility(crop, soil) * 0.25,
    texture_compatibility(crop, soil) * 0.20,
    drainage_compatibility(crop, soil) * 0.15,
    cec_compatibility(crop, soil) * 0.15,
    organic_carbon_score(soil) * 0.15,
    depth_score(soil) * 0.10
)
```

Each sub-score is normalized 0-1. Final score ≥ 0.7 = "suitable",
≥ 0.5 = "marginal", < 0.5 = "unsuitable".

## Offline Data Pipeline

```
[Raw Files] → [Parse] → [Validate] → [Triples] → [SQLite KG]

data/
├── raw/
│   ├── crop_ontology/
│   │   ├── wheat_traits.csv
│   │   ├── rice_traits.csv
│   │   └── maize_traits.csv
│   ├── soilgrids/
│   │   ├── region_1_ph.tif
│   │   ├── region_1_clay.tif
│   │   └── ...
│   └── pests/
│       └── pest_database.json
└── processed/
    ├── kg_triples.jsonl
    └── kg.db  (SQLite)
```

## Technology Stack
- **Language:** Python 3.11+
- **Storage:** SQLite (triple store + property tables)
- **Raster I/O:** rasterio (for GeoTIFF) — optional, mockable
- **Ontology Parsing:** pandas (CSV), rdflib (RDF) — optional
- **API:** FastAPI (optional, for serving)
- **CLI:** Click
- **Testing:** pytest

## Constraints Addressed
| Constraint | Implementation |
|-----------|----------------|
| 100% offline-first | All data cached; no runtime HTTP |
| Crop-soil matching | Weighted scoring algorithm |
| Pest/disease identification | Pest DB + symptom matching |
| Seasonal pattern reasoning | Seasonal rules engine |
| Weather interaction mapping | Crop weather preferences in entity model |
