# Open-Source Agriculture Data Sources — Research Notes

## 1. Crop Ontology (CO)

**Provider:** CGIAR / Bioversity International / Crop Trust  
**URL:** https://www.cropontology.org/  
**Format:** RDF/OWL, CSV, JSON  
**License:** CC-BY / Open Access

### What It Provides
- Standardized trait ontologies for 30+ crops (wheat, rice, maize, sorghum, cassava, etc.)
- Variables, methods, and scales for phenotyping
- Crop-specific trait dictionaries
- Germplasm-to-trait mappings

### Key Concepts
- **Trait:** Measurable characteristic (e.g., `plant_height`, `grain_yield`)
- **Variable:** Trait + Method + Scale combination
- **Ontology Term:** URI-identified concept in the crop trait ontology

### Offline Integration Strategy
1. Download crop-specific trait ontology files (RDF/OWL or CSV) for target crops
2. Store locally in `data/crop_ontology/`
3. Parse with `rdflib` or pandas for offline querying
4. Use to populate KG entities: traits, measurement methods, crop characteristics

### Files to Download (Bulk)
- `co_wheat.csv`, `co_rice.csv`, `co_maize.csv` — per-crop trait summaries
- Full RDF dump: `cropontology.rdf` (available via GitHub mirror)
- GitHub: https://github.com/Agricultural-Ontology/cropontology

---

## 2. SoilGrids

**Provider:** ISRIC — World Soil Information  
**URL:** https://soilgrids.org/  
**Format:** GeoTIFF (rder), WCS (Web Coverage Service)  
**License:** CC-BY-4.0

### What It Provides
- Global soil property estimates at 250m resolution
- Properties: pH, organic carbon, clay/sand/silt content, CEC, bulk depth, etc.
- Depth intervals: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm

### Key Properties for Crop Matching
| Property | Crop Relevance |
|----------|---------------|
| pH (water) | Nutrient availability, crop suitability |
| Organic carbon | Soil fertility, water retention |
| Clay content | Water holding, drainage |
| Sand content | Drainage, aeration |
| Cation exchange capacity (CEC) | Nutrient retention |
| Bulk density | Root penetration |
| Soil water capacity | Irrigation needs |

### Offline Integration Strategy
1. Download regional GeoTIFF tiles for target regions (not global — too large)
2. Store locally in `data/soilgrids/`
3. Query with `rasterio` for lat/lon → soil properties
4. Use for crop-soil matching: crop pH range vs. actual soil pH

### Data Access Notes
- REST API: `https://rest.soilgrids.org/soilgrids/v2.0/`
- WCS endpoint for bulk GeoTIFF download
- Can query by lat/lon or by bounding box
- Recommended: pre-download tiles for project regions

---

## 3. Additional Sources (Supplementary)

### FAO EcoCrop
- Crop environmental ranges (temp, pH, rainfall)
- Ideal for crop-soil-climate matching
- Available as CSV dump

### USDA Plants Database
- US-native crop/soil relationships
- State-level soil survey data

### Sentinel/Landsat (via Google Earth Engine)
- Seasonal vegetation indices
- Not used in this PoC (requires auth)

---

## 4. Integration Architecture Summary

```
┌─────────────────────────────────────────────┐
│           Agriculture Knowledge Graph         │
├─────────────────────────────────────────────┤
│  Entities: Crops, Soils, Pests, Nutrients    │
│  Relations: grows_in, requires, susceptible_to│
│  Reasoning: Crop recommendation engine        │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────────┐    ┌──────────────┐
│ Crop Ontology│    │   SoilGrids  │
│  (RDF/CSV)  │    │  (GeoTIFF)   │
│  Local cache │    │  Local tiles │
└─────────────┘    └──────────────┘
```

### Data Flow (Offline)
1. **Ingest:** Download source files → `data/raw/`
2. **Parse:** Transform to KG triples → `data/processed/`
3. **Load:** Build in-memory or SQLite KG
4. **Query:** Reasoning engine queries local KG
5. **Serve:** CLI + API for farmers/researchers
