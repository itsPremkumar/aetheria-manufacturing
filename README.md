# Aetheria Manufacturing — Supply Chain Knowledge Graph

A Python-based system for extracting, modeling, and reasoning about manufacturing supply chain data.

## Features

- **Entity Extraction**: Identify parts, suppliers, facilities, processes, materials, and products from text
- **Relation Extraction**: Discover relationships like `supplied_by`, `manufactured_at`, `shipped_to`, `requires`
- **Knowledge Graph**: Store and query supply chain entities with BFS pathfinding and adjacency queries
- **Reasoning Engine**: Cost optimization, bottleneck detection, risk analysis, and alternative supplier discovery
- **CLI**: Full command-line interface via `mfg-kg`
- **REST API**: HTTP API with JSON endpoints
- **500+ Entity Support**: Built-in sample data generator for testing

## Quick Start

```bash
pip install -e .
```

### Load Sample Data

```bash
mfg-kg load --num-entities 500
```

### Extract from Text

```bash
mfg-kg extract "Part #123 is supplied by Acme Corp and manufactured at Plant Detroit."
```

### Analyze Supply Chain

```bash
mfg-kg supply-chain "Engine-Module-A"
mfg-kg optimize "Engine-Module-A"
mfg-kg cost-optimize "Engine-Module-A"
mfg-kg risk-analyze "Engine-Module-A"
```

### Start API Server

```bash
mfg-kg server --port 8080
```

### Run Tests

```bash
pytest tests/ -v
```

## Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `part` | Manufacturing components | Part #123, SKU: ABC-456 |
| `supplier` | Vendors and manufacturers | Acme Corp, Global Supplies |
| `facility` | Plants, warehouses, DCs | Plant Detroit, Warehouse East |
| `process` | Manufacturing processes | CNC Machining, Assembly Line |
| `material` | Raw materials | Carbon-fiber, Steel alloy |
| `product` | Finished products | Model X-200, Series 500 |

## Relation Types

| Relation | Description |
|----------|-------------|
| `supplied_by` | Supplier relationship |
| `manufactured_at` | Production location |
| `shipped_to` | Logistics/delivery |
| `requires` | Part requirements |
| `contains` | Component inclusion |
| `depends_on` | Dependencies |
| `produced_by` | Production relationship |
| `located_at` | Location relationship |
| `uses_material` | Material usage |
| `uses_process` | Process usage |

## API Endpoints

- `GET /api/v1/entities` — List all entities
- `GET /api/v1/relations` — List all relations
- `GET /api/v1/statistics` — Graph statistics
- `POST /api/v1/extract` — Extract from text
- `POST /api/v1/query` — Query the graph
- `POST /api/v1/optimize` — Optimize supply chain
- `POST /api/v1/analyze` — Analyze supplier
- `POST /api/v1/cost-optimize` — Cost optimization
- `POST /api/v1/risk-analyze` — Risk analysis

## License

MIT
