"""
Manufacturing Risk Extension — Supply Chain Risk Module.

Analyzes supply chain risks including supplier concentration,
logistics disruption, raw material scarcity, and supplier financial health.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from .risk_scoring import RiskScoring, RiskScore, RiskRating


@dataclass
class SupplierInfo:
    """Information about a supplier."""
    supplier_id: str
    name: str
    spend_pct: float  # Percentage of total spend
    country: str = ""
    credit_rating: str = ""
    payment_delays: int = 0  # Days past due


class SupplyChainRisk:
    """Supply chain risk assessment."""

    def __init__(self, graph=None):
        self.graph = graph
        self.scoring = RiskScoring()

    def analyze_supplier_concentration(self, company_id: str) -> dict[str, Any]:
        """Analyze supplier spend concentration risk."""
        # Mock analysis based on typical concentration patterns
        concentration_score = 0.0
        risk_level = RiskRating.LOW

        # This would use actual supplier data from the graph in production
        if self.graph:
            # Analyze supplier relationships
            relations = self.graph.get_relations(company_id)
            supplier_count = len([r for r in relations if r.relation_type.value == "SUPPLIES"])
            if supplier_count == 0:
                concentration_score = 0.85  # High concentration (no suppliers = captive)
                risk_level = RiskRating.HIGH
            elif supplier_count < 3:
                concentration_score = 0.65
                risk_level = RiskRating.MEDIUM
            else:
                concentration_score = 0.25
                risk_level = RiskRating.LOW

        return {
            "company_id": company_id,
            "concentration_score": concentration_score,
            "risk_level": risk_level.value,
            "recommendations": self._get_recommendations(risk_level),
        }

    def map_supply_chain(self, company_id: str, depth: int = 3) -> dict[str, Any]:
        """Map multi-tier supply chain."""
        if not self.graph:
            return {"company_id": company_id, "tiers": [], "depth": depth}

        tiers = []
        visited = set()

        def _map_tier(eid: str, current_depth: int):
            if current_depth > depth or eid in visited:
                return
            visited.add(eid)

            entity = self.graph.get_entity(eid)
            if not entity:
                return

            tier_info = {
                "entity": entity.to_dict() if hasattr(entity, 'to_dict') else {"id": eid},
                "tier": current_depth,
            }

            if len(tiers) < current_depth:
                tiers.append([])
            tiers[current_depth - 1].append(tier_info)

            relations = self.graph.get_relations(eid)
            for relation in relations:
                next_id = relation.target_id if relation.source_id == eid else relation.source_id
                _map_tier(next_id, current_depth + 1)

        _map_tier(company_id, 1)

        return {
            "company_id": company_id,
            "depth": depth,
            "tiers": tiers,
            "total_suppliers": sum(len(tier) for tier in tiers),
        }

    def assess_logistics_risk(self, route: dict) -> dict[str, Any]:
        """Assess transportation/logistics risk for a route."""
        origin = route.get("origin", "")
        destination = route.get("destination", "")
        transport_mode = route.get("mode", "sea")

        # Assess based on route characteristics
        risk_factors = []
        likelihood = 2  # Default: Unlikely
        impact = 2  # Default: Minor

        # High-risk routes
        if route.get("conflict_zone"):
            risk_factors.append("Route passes through conflict zone")
            likelihood = max(likelihood, 4)
            impact = max(impact, 4)

        if route.get("weather_disruption"):
            risk_factors.append("Weather disruption expected")
            likelihood = max(likelihood, 3)
            impact = max(impact, 3)

        if transport_mode == "sea" and route.get("congestion"):
            risk_factors.append("Port congestion risk")
            likelihood = max(likelihood, 3)

        risk = self.scoring.assess_risk(
            likelihood=likelihood,
            impact=impact,
            risk_id="SR-02",
            category="Logistics Disruption",
            description=f"Logistics risk for {origin} → {destination}",
        )

        return {
            "route": f"{origin} → {destination}",
            "risk_score": risk.to_dict(),
            "risk_factors": risk_factors,
            "transport_mode": transport_mode,
        }

    def get_supplier_financial_health(self, supplier_id: str) -> dict[str, Any]:
        """Assess supplier financial health risk."""
        # Mock assessment
        risk = self.scoring.assess_risk(
            likelihood=2,
            impact=4,
            risk_id="SR-05",
            category="Supplier Financial Health",
            description=f"Financial health risk for supplier {supplier_id}",
        )

        return {
            "supplier_id": supplier_id,
            "credit_rating": "BB",
            "risk_score": risk.to_dict(),
            "payment_delays_days": 15,
            "recommendations": [
                "Monitor payment behavior monthly",
                "Diversify supplier base",
                "Establish backup suppliers",
            ],
        }

    def _get_recommendations(self, risk_level: RiskRating) -> list[str]:
        """Get recommendations based on risk level."""
        recommendations = {
            RiskRating.LOW: [
                "Continue monitoring supplier concentration",
                "Maintain supplier relationships",
            ],
            RiskRating.MEDIUM: [
                "Identify alternative suppliers",
                "Negotiate long-term contracts with key suppliers",
                "Establish safety stock for critical materials",
            ],
            RiskRating.HIGH: [
                "Urgent: Diversify supplier base",
                "Establish dual-sourcing for critical components",
                "Implement supplier risk monitoring system",
                "Consider vertical integration for critical supplies",
            ],
            RiskRating.CRITICAL: [
                "CRITICAL: Immediate supplier diversification required",
                "Engage procurement team for emergency sourcing",
                "Activate business continuity plans",
                "Escalate to C-suite for strategic sourcing decisions",
            ],
        }
        return recommendations.get(risk_level, [])
