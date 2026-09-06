"""
Manufacturing Risk Extension.

Provides risk assessment for manufacturing operations:
- Supply chain risk (supplier concentration, logistics, raw materials)
- Production risk (capacity, equipment, quality, labor)
- Compliance risk (environmental, safety, trade, product liability)
"""

from .risk_scoring import RiskScoring, RiskScore, RiskRating
from .supply_chain import SupplyChainRisk
from .production import ProductionRisk
from .compliance import ComplianceRisk

__all__ = [
    "RiskScoring",
    "RiskScore",
    "RiskRating",
    "SupplyChainRisk",
    "ProductionRisk",
    "ComplianceRisk",
]
