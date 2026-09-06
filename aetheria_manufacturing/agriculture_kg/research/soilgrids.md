# SoilGrids — Research Notes

## Overview
SoilGrids is a global soil information system developed by ISRIC (World Soil Information). It provides soil property maps at 250m resolution for the entire world, using machine learning models trained on global soil observations.

## API Details
- **Base URL**: `https://rest.isric.org/soilgrids/v2.0/`
- **Format**: JSON (REST)
- **Key Endpoints**:
  - `GET /soilgrids/v2.0/properties/query` — Query soil properties by location
  - `GET /soilgrids/v2.0/location?lat={lat}&lon={lon}` — Get soil data for coordinates
  - `GET /soilgrids/v2.0/properties` — List available soil properties

## Key Soil Properties
- **clay**: Clay content (g/kg)
- **silt**: Silt content (g/kg)
- **sand**: Sand content (g/kg)
- **cec**: Cation exchange capacity (cmolc/kg)
- **phh2o**: Soil pH in water (pH * 10)
- **soc**: Soil organic carbon content (dg/kg)
- **nitrogen**: Total nitrogen (cg/kg)
- **ocd**: Organic carbon density (kg/m³)
- **wv0010**: Volumetric water content at 10 kPa (cm³/cm³)
- **wv0033**: Volumetric water content at 33 kPa (cm³/cm³)
- **wv1500**: Volumetric water content at 1500 kPa (cm³/cm³)

## Depth Layers
- 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm

## Offline Strategy
- Cache soil data by geographic region in `data/soilgrids/`
- Use SQLite with spatial indexing for local queries
- Pre-download data for target regions of interest
- Store soil property profiles for crop-soil matching

## Integration Points
1. Soil property data → Knowledge Graph nodes
2. Soil-crop suitability → Crop-soil matching module
3. Soil moisture data → Weather interaction mapping
4. Soil nutrient profiles → Seasonal reasoning module
