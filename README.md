# Aetheria Manufacturing — Supply Chain Knowledge Graph

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/Tests-74%20passing-brightgreen.svg)](tests/)
[![Offline-First](https://img.shields.io/badge/Mode-100%25%20Offline-green.svg)]()
[![Model](https://img.shields.io/badge/Model-inclusionai%2Fling--3.0--flash--sante-blue)]()

A production-quality Python system for extracting, modeling, querying, and reasoning
about manufacturing supply chain data. Fully offline-first — no external API calls
required at runtime.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [CLI Commands](#cli-commands)
6. [REST API](#rest-api)
7. [Risk Analysis Module](#risk-analysis-module)
8. [Entity & Relation Types](#entity--relation-types)
9. [Testing](#testing)
10. [Project Structure](#project-structure)
11. [License](#license)

---

## Features

| Module | Capabilities |
|--------|-------------|
| **Entity Extractor** | Identifies parts, suppliers, facilities, materials, products from text |
| **Relation Extractor** | Discovers `supplied_by`, `manufactured_at`, `shipped_to`, `contains`, `depends_on`, `produced_by`, `located_at`, `uses_material` |
| **Knowledge Graph** | In-memory graph with BFS pathfinding, adjacency queries, merge support |
| **Reasoning Engine** | Cost optimization, bottleneck detection, single-source risk, alternative suppliers |
| **Risk Analysis** | Risk scoring (0–100), supplier reliability metrics, disruption prediction |
| **CLI** | Full `mfg-kg` command-line interface |
| **REST API** | HTTP API with JSON endpoints |
| **Sample Data** | 500+ entity generator for testing |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CLI / REST API Layer                   │
│              (aetheria_manufacturing/cli/                │
│               aetheria_manufacturing/api/)               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Orchestrator Layer                     │
│             (aetheria_manufacturing/__init__.py)          │
└──────────────────────┬──────────────────────────────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
┌────▼────┐    ┌──────▼──────┐    ┌─────▼─────┐
│Extractors│    │  Knowledge  │    │ Reasoning │
│(entity/  │    │   Graph     │    │  Engine   │
│relation) │    │(BFS, adj., │    │(cost opt, │
│          │    │ merge)      │    │ bottlenecks)│
└────┬─────┘    └──────┬──────┘    └─────┬─────┘
     │                 │                 │
     │            ┌────▼─────┐    ┌──────▼──────┐
     │            │   Risk    │    │  Data Model │
     │            │  Analysis │    │ (Entity,    │
     │            │(scoring,  │    │  Relation,  │
     │            │ reliability│    │  EntityType)│
     │            │ disrupt.) │    │             │
     │            └───────────┘    └─────────────┘
```

---

## Installation

```bash
pip install -e .
```

---

## Quick Start

```bash
# Load sample data (500+ entities)
mfg-kg load --num-entities 500

# Extract entities from text
mfg-kg extract "Part #123 is supplied by Acme Corp and manufactured at Plant Detroit."

# Query the graph
mfg-kg query "What supplies Engine-Module-A?"

# Analyze supply chain
mfg-kg supply-chain "Engine-Module-A"
mfg-kg optimize "Engine-Module-A"

# Risk analysis
mfg-kg risk "Engine-Module-A"
mfg-kg reliability "Acme Corp"
mfg-kg disruptions
mfg-kg risk-report

# Start API server
mfg-kg server --port 8080

# Run tests
pytest tests/ -v
```

---

## CLI Commands

| Command | Description | Arguments |
|---------|-------------|-----------|
| `extract` | Extract entities/relations from text | `--text` or positional text |
| `query` | Query the knowledge graph | Query string |
| `supply-chain` | Analyze supply chain for a part | Part name |
| `optimize` | Optimize supply chain costs | Part name |
| `cost-optimize` | Cost optimization analysis | Part name |
| `analyze` | Analyze a supplier | Supplier name |
| `risk` | Risk analysis for a part | Part name |
| `reliability` | Supplier reliability metrics | Supplier name |
| `disruptions` | Predict supply chain disruptions | (none) |
| `risk-report` | Comprehensive risk report | (none) |
| `load` | Load sample data | `--num-entities` (default: 500) |
| `stats` | Graph statistics | (none) |
| `server` | Start REST API server | `--port` (default: 8080) |

---

## REST API

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/entities` | List all entities |
| `GET` | `/api/v1/relations` | List all relations |
| `GET` | `/api/v1/statistics` | Graph statistics |
| `POST` | `/api/v1/extract` | Extract entities/relations from text |
| `POST` | `/api/v1/query` | Query the knowledge graph |
| `POST` | `/api/v1/optimize` | Optimize supply chain costs |
| `POST` | `/api/v1/analyze` | Analyze a supplier |
| `POST` | `/api/v1/risk-report` | Generate comprehensive risk report |
| `GET` | `/api/v1/health` | Health check |

### Example Requests

```bash
# Extract from text
curl -X POST http://localhost:8080/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Part #123 is supplied by Acme Corp"}'

# Query the graph
curl -X POST http://localhost:8080/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What supplies Engine-Module-A?"}'

# Get risk report
curl http://localhost:8080/api/v1/risk-report
```

---

## Risk Analysis Module

The Risk Analysis module provides three core capabilities:

### 1. Risk Scoring

Calculates a risk score (0–100) for any part/entity in the supply chain.

**Risk factors detected:**
- Single-source dependency
- No supplier assigned
- Facility-related risks
- Dependency chain risks

**Risk levels:** `low` | `medium` | `high` | `critical` | `unknown`

```bash
mfg-kg risk "Engine-Module-A"
```

### 2. Supplier Reliability

Metrics for any supplier:

| Metric | Description |
|--------|-------------|
| `on_time_delivery_rate` | Percentage of on-time deliveries |
| `quality_score` | Quality rating (0–100) |
| `avg_lead_time` | Average delivery lead time |
| `lead_time_std` | Standard deviation of lead time |
| `fulfillment_rate` | Order fulfillment percentage |
| `overall_reliability` | Weighted composite score |

```bash
mfg-kg reliability "Acme Corp"
```

### 3. Disruption Prediction

Predicts potential supply chain disruptions with probability and impact scores.

```bash
mfg-kg disruptions
mfg-kg disruptions --entity "Supplier-Name"
```

### Risk Report API

```bash
curl http://localhost:8080/api/v1/risk-report
```

Returns:
```json
{
  "summary": {
    "total_entities_analyzed": 500,
    "total_suppliers_analyzed": 50,
    "average_reliability_score": 85.3,
    "average_risk_score": 22.1
  },
  "risk_distribution": {"low": 300, "medium": 150, "high": 40, "critical": 10},
  "reliability_distribution": {...},
  "top_risks": [...],
  "top_disruptions": [...],
  "supplier_reliability": [...]
}
```

---

## Entity & Relation Types

### Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `part` | Manufacturing components | Part #123, SKU: ABC-456 |
| `supplier` | Vendors and manufacturers | Acme Corp, Global Supplies |
| `facility` | Plants, warehouses, DCs | Plant Detroit, Warehouse East |
| `material` | Raw materials | Carbon-fiber, Steel alloy |
| `product` | Finished products | Model X-200, Series 500 |

### Relation Types

| Relation | Description |
|----------|-------------|
| `supplied_by` | Supplier relationship |
| `manufactured_at` | Production location |
| `shipped_to` | Logistics/delivery |
| `contains` | Component inclusion |
| `depends_on` | Dependencies |
| `produced_by` | Production relationship |
| `located_at` | Location relationship |
| `uses_material` | Material usage |

---

## Testing

```bash
pytest tests/ -v
```

**Test Results:** 74 passed (54 core + 20 risk module)

| Test Suite | Count |
|------------|-------|
| Core Manufacturing KG | 54 |
| Risk Analysis Module | 20 |
| **Total** | **74** |

### Running Specific Tests

```bash
# Core tests only
pytest tests/test_aetheria_manufacturing.py -v

# Risk module only
pytest tests/test_risk_module.py -v

# With coverage
pytest tests/ --cov=aetheria_manufacturing --cov-report=html
```

---

## Project Structure

```
aetheria_manufacturing/
├── __init__.py              # Package exports
├── api/
│   └── api.py               # REST API server (FastAPI/uvicorn)
├── cli/
│   └── cli.py               # CLI entry point (mfg-kg)
├── extractors/
│   ├── entity_extractor.py  # Entity extraction logic
│   └── relation_extractor.py # Relation extraction logic
├── graph/
│   └── knowledge_graph.py   # In-memory graph + BFS + merge
├── reasoning/
│   └── reasoning_engine.py  # Cost optimization, bottlenecks
├── risk/
│   ├── __init__.py          # Risk module exports
│   └── risk_analyzer.py     # Risk scoring, reliability, disruptions
└── ...

tests/
├── test_aetheria_manufacturing.py  # Core tests (54)
└── test_risk_module.py            # Risk tests (20)
```

---

## License

MIT © 2025
