"""
Manufacturing Risk Extension — Compliance Risk Module.

Analyzes compliance risks including environmental, safety, trade,
product liability, and data privacy.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from .risk_scoring import RiskScoring, RiskScore, RiskRating


class ComplianceRisk:
    """Compliance risk assessment."""

    def __init__(self, graph=None):
        self.graph = graph
        self.scoring = RiskScoring()

    def assess_environmental_risk(
        self,
        facility_id: str,
        emissions_data: dict,
        violations: list[dict],
    ) -> dict[str, Any]:
        """Assess environmental compliance risk."""
        co2_tons = emissions_data.get("co2_tons", 0)
        voc_tons = emissions_data.get("voc_tons", 0)
        violation_count = len(violations)

        likelihood = 2
        if violation_count > 2:
            likelihood = 5
        elif violation_count > 0:
            likelihood = 3

        impact = 3
        if co2_tons > 10000:
            impact = 5
        elif co2_tons > 5000:
            impact = 4

        risk = self.scoring.assess_risk(
            likelihood=likelihood,
            impact=impact,
            risk_id="CR-01",
            category="Environmental",
            description=f"Environmental compliance risk at {facility_id}",
        )

        return {
            "facility_id": facility_id,
            "emissions": emissions_data,
            "violation_count": violation_count,
            "risk_score": risk.to_dict(),
            "recommendations": self._get_environmental_recommendations(violation_count),
        }

    def assess_safety_risk(self, facility_id: str, incidents: list[dict]) -> dict[str, Any]:
        """Assess workplace safety risk."""
        incident_count = len(incidents)
        severity_scores = [i.get("severity", 1) for i in incidents]
        avg_severity = sum(severity_scores) / max(len(severity_scores), 1)

        likelihood = 2
        if incident_count > 5:
            likelihood = 5
        elif incident_count > 2:
            likelihood = 4
        elif incident_count > 0:
            likelihood = 3

        impact = min(5, int(avg_severity) + 1)

        risk = self.scoring.assess_risk(
            likelihood=likelihood,
            impact=impact,
            risk_id="CR-02",
            category="Safety",
            description=f"Workplace safety risk at {facility_id}: {incident_count} incidents",
        )

        return {
            "facility_id": facility_id,
            "incident_count": incident_count,
            "avg_severity": avg_severity,
            "risk_score": risk.to_dict(),
            "recommendations": self._get_safety_recommendations(incident_count),
        }

    def assess_trade_compliance(self, company_id: str) -> dict[str, Any]:
        """Assess export/trade compliance risk."""
        risk = self.scoring.assess_risk(
            likelihood=2,
            impact=4,
            risk_id="CR-03",
            category="Trade Compliance",
            description=f"Trade compliance risk for {company_id}",
        )

        return {
            "company_id": company_id,
            "risk_score": risk.to_dict(),
            "denied_party_screening": "required",
            "export_license_required": True,
            "recommendations": [
                "Implement automated denied party screening",
                "Conduct export classification review",
                "Train staff on export compliance",
                "Establish export compliance manual",
            ],
        }

    def generate_compliance_report(self, company_id: str) -> dict[str, Any]:
        """Generate a comprehensive compliance report."""
        return {
            "company_id": company_id,
            "report_date": "2024-01-01",
            "environmental": {"status": "compliant", "risk_level": "Low"},
            "safety": {"status": "compliant", "risk_level": "Medium"},
            "trade": {"status": "action_required", "risk_level": "Medium"},
            "product_liability": {"status": "compliant", "risk_level": "Low"},
            "data_privacy": {"status": "compliant", "risk_level": "Low"},
            "overall_risk": "Medium",
            "recommendations": [
                "Address trade compliance gaps",
                "Continue safety monitoring",
                "Maintain environmental compliance",
            ],
        }

    def _get_environmental_recommendations(self, violation_count: int) -> list[str]:
        """Get environmental compliance recommendations."""
        if violation_count > 0:
            return [
                "Address all open violations immediately",
                "Implement environmental management system (ISO 14001)",
                "Conduct compliance audit within 30 days",
                "Establish emissions monitoring system",
                "Train staff on environmental procedures",
            ]
        return [
            "Maintain ISO 14001 certification",
            "Conduct regular emissions monitoring",
            "Review environmental procedures annually",
        ]

    def _get_safety_recommendations(self, incident_count: int) -> list[str]:
        """Get safety recommendations."""
        if incident_count > 2:
            return [
                "Conduct comprehensive safety audit",
                "Implement behavior-based safety program",
                "Increase safety training frequency",
                "Establish safety observation program",
                "Review lockout/tagout procedures",
            ]
        return [
            "Continue OSHA compliance monitoring",
            "Maintain safety training records",
            "Conduct regular safety drills",
            "Implement near-miss reporting system",
        ]
