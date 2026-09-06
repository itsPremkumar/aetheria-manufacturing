# Crop Ontology (CO) — Research Notes

## Overview
The Crop Ontology (CO) is a CGIAR-led initiative that provides standardized, structured trait data for crops. It enables interoperability between breeding, phenotyping, and agricultural knowledge systems.

## API Details
- **Base URL**: `https://cropontology.org/api/`
- **Format**: JSON (REST)
- **Key Endpoints**:
  - `GET /api/crops/` — List all crops
  - `GET /api/crops/{crop_id}/` — Get crop details
  - `GET /api/traits/` — List all traits
  - `GET /api/traits/{trait_id}/` — Get trait details
  - `GET /api/ontologies/` — List ontologies
  - `GET /api/ontologies/{ontology_id}/terms/` — Get ontology terms

## Key Concepts
- **Crop**: A cultivated plant (e.g., wheat, rice, maize)
- **Trait**: A measurable characteristic (e.g., plant height, yield, drought tolerance)
- **Ontology**: A controlled vocabulary of terms (e.g., Trait Ontology, Crop Ontology)
- **Variable**: A specific measurement of a trait under defined conditions

## Relevant Ontologies
- **Trait Ontology (TO)**: General plant traits
- **Crop Ontology (CO)**: Crop-specific traits
- **Pest Ontology**: Pest and disease classifications
- **Weather Ontology**: Weather and climate variables

## Offline Strategy
- Cache API responses as JSON files in `data/crop_ontology/`
- Use SQLite database for local querying
- Implement sync mechanism for periodic updates
- Store trait-crop relationships for offline matching

## Integration Points
1. Crop trait data → Knowledge Graph nodes
2. Trait relationships → Knowledge Graph edges
3. Pest/disease classifications → Pest identification module
4. Seasonal trait variations → Seasonal reasoning module
