"""
Manufacturing Risk Extension — Production Risk Module.

Analyzes production risks including capacity utilization, equipment failure,
quality defects, labor disputes, and technology obsolescence.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from .risk_scoring import RiskScoring, RiskScore, RiskRating


class ProductionRisk:
    """Production risk assessment."""

    def __init__(self, graph=None):
        self.graph = graph
        self.scoring = RiskScoring()

    def analyze_capacity_utilization(self, plant_id: str) -> dict[str, Any]:
        """Assess capacity utilization risk for a plant."""
        # Mock utilization data
        utilization_pct = 85.0
        risk_level = RiskRating.MEDIUM
        bottleneck = "assembly_line_3"

        if utilization_pct > 90:
            risk_level = RiskRating.HIGH
        elif utilization_pct < 50:
            risk_level = RiskRating.HIGH
        elif utilization_pct > 80:
            risk_level = RiskRating.MEDIUM
        else:
            risk_level = RiskRating.LOW

        return {
            "plant_id": plant_id,
            "utilization_pct": utilization_pct,
            "risk_level": risk_level.value,
            "bottleneck": bottleneck,
            "recommendations": self._get_capacity_recommendations(utilization_pct),
        }

    def assess_equipment_failure_risk(self, equipment: dict) -> dict[str, Any]:
        """Assess equipment failure risk."""
        mtbf = equipment.get("mtbf_hours", 1000)  # Mean Time Between Failures
        age_years = equipment.get("age_years", 5)
        last_maintenance = equipment.get("last_maintenance_days_ago", 30)

        # Calculate failure likelihood
        likelihood = 2  # Default: Unlikely
        if mtbf < 500 or age_years > 10:
            likelihood = 4
        elif mtbf < 1000 or age_years > 7:
            likelihood = 3

        if last_maintenance > 180:
            likelihood += 1

        risk = self.scoring.assess_risk(
            likelihood=min(5, likelihood),
            impact=4,
            risk_id="PR-02",
            category="Equipment Failure",
            description=f"Equipment failure risk for {equipment.get('name', 'unknown')}",
        )

        return {
            "equipment": equipment.get("name", "unknown"),
            "risk_score": risk.to_dict(),
            "mtbf_hours": mtbf,
            "age_years": age_years,
            "last_maintenance_days": last_maintenance,
            "recommendations": [
                "Implement predictive maintenance",
                "Schedule equipment replacement planning",
                "Maintain critical spare parts inventory",
            ],
        }

    def assess_quality_risk(self, product_line: str, defect_rate: float, recall_count: int) -> dict[str, Any]:
        """Assess quality risk for a product line."""
        # Calculate risk based on defect rate and recall history
        likelihood = 2
        if defect_rate > 0.05:
            likelihood = 5
        elif defect_rate > 0.03:
            likelihood = 4
        elif defect_rate > 0.01:
            likelihood = 3

        impact = 3
        if recall_count > 3:
            impact = 5
        elif recall_count > 1:
            impact = 4

        risk = self.scoring.assess_risk(
            likelihood=likelihood,
            impact=impact,
            risk_id="PR-03",
            category="Quality Defects",
            description=f"Quality risk for {product_line}: {defect_rate:.1%} defect rate, {recall_count} recalls",
        )

        return {
            "product_line": product_line,
            "defect_rate": defect_rate,
            "recall_count": recall_count,
            "risk_score": risk.to_dict(),
            "recommendations": self._get_quality_recommendations(defect_rate, recall_count),
        }

    def assess_labor_risk(self, facility_id: str) -> dict[str, Any]:
        """Assess labor dispute risk."""
        risk = self.scoring.assess_risk(
            likelihood=2,
            impact=3,
            risk_id="PR-04",
            category="Labor Dispute",
            description=f"Labor dispute risk at facility {facility_id}",
        )

        return {
            "facility_id": facility_id,
            "risk_score": risk.to_dict(),
            "union_activity": "moderate",
            "turnover_rate": 0.12,
            "recommendations": [
                "Engage in proactive labor relations",
                "Review compensation competitiveness",
                "Implement employee retention programs",
            ],
        }

    def _get_capacity_recommendations(self, utilization_pct: float) -> list[str]:
        """Get capacity-related recommendations."""
        if utilization_pct > 90:
            return [
                "Urgent: Expand capacity or outsource",
                "Implement overtime management",
                "Optimize production scheduling",
                "Consider second-shift operations",
            ]
        elif utilization_pct < 50:
            return [
                "Review product mix and demand",
                "Seek new customers or markets",
                "Consider temporary plant closure",
                "Implement workforce retraining",
            ]
        return [
            "Monitor demand forecasts",
            "Maintain flexible workforce",
            "Optimize maintenance windows",
        ]

    def _get_quality_recommendations(self, defect_rate: float, recall_count: int) -> list[str]:
        """Get quality-related recommendations."""
        if defect_rate > 0.03 or recall_count > 1:
            return [
                "Implement SPC (Statistical Process Control)",
                "Conduct root cause analysis",
                "Enhance incoming material inspection",
                "Review supplier quality agreements",
                "Consider product recall insurance",
            ]
        return [
            "Continue statistical quality monitoring",
            "Maintain ISO 9001 compliance",
            "Implement continuous improvement programs",
        ]
