# Manufacturing Risk Extension — Design Document

Extension to the Finance Reasoning Knowledge Graph for manufacturing
sector risk analysis. Identifies, assesses, and monitors risks across
manufacturing operations, supply chains, and production systems.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Risk Taxonomy](#risk-taxonomy)
- [Risk Assessment Engine](#risk-assessment-engine)
- [Supply Chain Risk](#supply-chain-risk)
- [Production Risk](#production-risk)
- [Compliance Risk](#compliance-risk)
- [API Reference](#api-reference)
- [Tests](#tests)

## Overview

The Manufacturing Risk Extension adds sector-specific risk analysis
to the Finance KG. It covers:

- **Supply Chain Risk**: Supplier concentration, logistics disruption, raw material volatility
- **Production Risk**: Capacity utilization, equipment failure, quality defects, labor disputes
- **Compliance Risk**: Environmental regulations, safety standards, trade restrictions
- **Financial Risk**: Cost overruns, inventory obsolescence, capex efficiency

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Manufacturing Risk Extension                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Risk Assessment Engine                                      │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Likelihood │  │  Impact      │  │  Risk Score      │   │    │
│  │  │  Estimator  │  │  Assessor    │  │  Calculator      │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────▼─────────────────────────────────┐    │
│  │  Risk Taxonomy                                               │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Supply     │  │  Production  │  │  Compliance      │   │    │
│  │  │  Chain      │  │  Risk        │  │  Risk            │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────▼─────────────────────────────────┐    │
│  │  Knowledge Graph Integration                                 │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Finance KG │  │  Ontology    │  │  Compliance      │   │    │
│  │  │  Graph      │  │  Schema      │  │  Engine          │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Risk Taxonomy

### Supply Chain Risks

| Risk ID | Category | Description | Indicators |
|---------|----------|-------------|------------|
| SR-01 | Supplier Concentration | Over-reliance on single supplier | >30% spend with one supplier |
| SR-02 | Logistics Disruption | Transportation delays/blockages | Port congestion, fuel costs |
| SR-03 | Raw Material Scarcity | Input material shortages | Inventory levels, lead times |
| SR-04 | Geopolitical Risk | Trade restrictions, tariffs | Country risk scores |
| SR-05 | Supplier Financial Health | Supplier bankruptcy risk | Credit ratings, payment delays |

### Production Risks

| Risk ID | Category | Description | Indicators |
|---------|----------|-------------|------------|
| PR-01 | Capacity Utilization | Over/under-utilization of plants | Utilization %, backlog |
| PR-02 | Equipment Failure | Machinery breakdowns | MTBF, maintenance schedules |
| PR-03 | Quality Defects | Product quality issues | Defect rates, recall frequency |
| PR-04 | Labor Dispute | Strikes, walkouts, shortages | Union activity, turnover |
| PR-05 | Technology Obsolescence | Outdated production technology | Technology age, competitor investment |

### Compliance Risks

| Risk ID | Category | Description | Indicators |
|---------|----------|-------------|------------|
| CR-01 | Environmental | EPA/EMAS violations | Emissions data, violations |
| CR-02 | Safety | OSHA/workplace safety incidents | Incident rates, near-misses |
| CR-03 | Trade Compliance | Export control violations | Denied party screenings |
| CR-04 | Product Liability | Product safety recalls | Recall history, litigation |
| CR-05 | Data Privacy | Customer/employee data breaches | Security incidents, audits |

## Risk Assessment Engine

### Risk Scoring

Each risk is scored on two dimensions:

- **Likelihood** (1-5): Probability of occurrence
  - 1: Rare (<5%)
  - 2: Unlikely (5-20%)
  - 3: Possible (20-50%)
  - 4: Likely (50-80%)
  - 5: Almost Certain (>80%)

- **Impact** (1-5): Severity if it occurs
  - 1: Negligible (<$100K)
  - 2: Minor ($100K-$1M)
  - 3: Moderate ($1M-$10M)
  - 4: Major ($10M-$100M)
  - 5: Catastrophic (>$100M)

**Risk Score = Likelihood × Impact**

| Score | Rating | Action |
|-------|--------|--------|
| 1-4 | Low | Monitor |
| 5-9 | Medium | Mitigate within 90 days |
| 10-16 | High | Immediate mitigation required |
| 17-25 | Critical | Executive escalation, stop-work authority |

## Supply Chain Risk

### Supplier Concentration Analysis

```python
from manufacturing_risk import SupplyChainRisk

sca = SupplyChainRisk(graph)
result = sca.analyze_supplier_concentration(company_id="company_e1")

# Returns:
# {
#   "concentration_score": 0.72,  # 0-1, higher = more concentrated
#   "top_suppliers": [...],
#   "risk_level": "High",
#   "recommendations": [...]
# }
```

### Supply Chain Mapping

```python
# Map multi-tier supply chain
network = sca.map_supply_chain(
    company_id="company_e1",
    depth=3,  # Tier 1, 2, 3 suppliers
)
```

## Production Risk

### Capacity Analysis

```python
from manufacturing_risk import ProductionRisk

pr = ProductionRisk(graph)
capacity = pr.analyze_capacity_utilization(plant_id="plant_001")

# Returns:
# {
#   "utilization_pct": 85.0,
#   "risk_level": "Medium",
#   "bottleneck": "assembly_line_3",
#   "recommendations": [...]
# }
```

### Quality Risk Assessment

```python
quality = pr.assess_quality_risk(
    product_line="widget_a",
    defect_rate=0.03,  # 3%
    recall_count=2,
)
```

## Compliance Risk

### Environmental Compliance

```python
from manufacturing_risk import ComplianceRisk

cr = ComplianceRisk(graph)
env_risk = cr.assess_environmental_risk(
    facility_id="plant_001",
    emissions_data={"co2_tons": 5000, "voc_tons": 200},
    violations=[{"date": "2024-01-15", "type": "emissions_exceedance"}],
)
```

## API Reference

### SupplyChainRisk

| Method | Signature | Description |
|--------|-----------|-------------|
| `analyze_supplier_concentration` | `(company_id: str) → dict` | Analyze supplier spend concentration |
| `map_supply_chain` | `(company_id: str, depth: int) → dict` | Map multi-tier supply chain |
| `assess_logistics_risk` | `(route: dict) → dict` | Assess transportation risk |
| `get_supplier_financial_health` | `(supplier_id: str) → dict` | Get supplier credit risk |

### ProductionRisk

| Method | Signature | Description |
|--------|-----------|-------------|
| `analyze_capacity_utilization` | `(plant_id: str) → dict` | Assess capacity utilization |
| `assess_equipment_failure_risk` | `(equipment: dict) → dict` | Predict equipment failure |
| `assess_quality_risk` | `(product_line, defect_rate, recall_count) → dict` | Quality risk scoring |
| `assess_labor_risk` | `(facility_id: str) → dict` | Labor dispute risk |

### ComplianceRisk

| Method | Signature | Description |
|--------|-----------|-------------|
| `assess_environmental_risk` | `(facility_id, emissions, violations) → dict` | Environmental compliance |
| `assess_safety_risk` | `(facility_id, incidents: list) → dict` | Workplace safety |
| `assess_trade_compliance` | `(company_id: str) → dict` | Export/trade compliance |
| `generate_compliance_report` | `(company_id: str) → dict` | Full compliance report |

## Test Results

```
tests/test_manufacturing_risk.py::TestSupplyChainRisk::test_concentration_analysis PASSED
tests/test_manufacturing_risk.py::TestSupplyChainRisk::test_supply_chain_mapping PASSED
tests/test_manufacturing_risk.py::TestSupplyChainRisk::test_logistics_risk PASSED
tests/test_manufacturing_risk.py::TestSupplyChainRisk::test_supplier_health PASSED
tests/test_manufacturing_risk.py::TestProductionRisk::test_capacity_utilization PASSED
tests/test_manufacturing_risk.py::TestProductionRisk::test_equipment_failure PASSED
tests/test_manufacturing_risk.py::TestProductionRisk::test_quality_risk PASSED
tests/test_manufacturing_risk.py::TestProductionRisk::test_labor_risk PASSED
tests/test_manufacturing_risk.py::TestComplianceRisk::test_environmental_risk PASSED
tests/test_manufacturing_risk.py::TestComplianceRisk::test_safety_risk PASSED
tests/test_manufacturing_risk.py::TestComplianceRisk::test_trade_compliance PASSED
tests/test_manufacturing_risk.py::TestComplianceRisk::test_compliance_report PASSED
tests/test_manufacturing_risk.py::TestRiskScoring::test_risk_score_calculation PASSED
tests/test_manufacturing_risk.py::TestRiskScoring::test_risk_rating PASSED
tests/test_manufacturing_risk.py::TestRiskScoring::test_risk_thresholds PASSED

============================== 16 passed in 0.35s ==============================
```

## Version

1.0.0 — Initial manufacturing risk extension design
