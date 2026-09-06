"""
Manufacturing Risk Extension — Risk Scoring Module.

Provides risk scoring, rating, and threshold logic for manufacturing risk assessment.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RiskRating(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class RiskScore:
    """A risk score with likelihood and impact dimensions."""
    likelihood: int  # 1-5
    impact: int  # 1-5
    score: int = 0  # likelihood * impact
    rating: RiskRating = RiskRating.LOW
    risk_id: str = ""
    category: str = ""
    description: str = ""

    def __post_init__(self):
        self.score = self.likelihood * self.impact
        self.rating = self._calculate_rating()

    def _calculate_rating(self) -> RiskRating:
        """Calculate risk rating from score."""
        if self.score >= 17:
            return RiskRating.CRITICAL
        elif self.score >= 10:
            return RiskRating.HIGH
        elif self.score >= 5:
            return RiskRating.MEDIUM
        return RiskRating.LOW

    def to_dict(self) -> dict:
        return {
            "risk_id": self.risk_id,
            "category": self.category,
            "description": self.description,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "score": self.score,
            "rating": self.rating.value,
        }


class RiskScoring:
    """Risk scoring engine for manufacturing risk assessment."""

    @staticmethod
    def calculate_score(likelihood: int, impact: int) -> int:
        """Calculate risk score from likelihood and impact."""
        return likelihood * impact

    @staticmethod
    def get_rating(score: int) -> RiskRating:
        """Get risk rating from score."""
        if score >= 17:
            return RiskRating.CRITICAL
        elif score >= 10:
            return RiskRating.HIGH
        elif score >= 5:
            return RiskRating.MEDIUM
        return RiskRating.LOW

    @staticmethod
    def get_action(rating: RiskRating) -> str:
        """Get recommended action for a risk rating."""
        actions = {
            RiskRating.LOW: "Monitor — review quarterly",
            RiskRating.MEDIUM: "Mitigate within 90 days",
            RiskRating.HIGH: "Immediate mitigation required",
            RiskRating.CRITICAL: "Executive escalation — stop-work authority",
        }
        return actions[rating]

    @staticmethod
    def assess_risk(
        likelihood: int,
        impact: int,
        risk_id: str = "",
        category: str = "",
        description: str = "",
    ) -> RiskScore:
        """Assess a risk and return a RiskScore."""
        if not 1 <= likelihood <= 5:
            raise ValueError("Likelihood must be between 1 and 5")
        if not 1 <= impact <= 5:
            raise ValueError("Impact must be between 1 and 5")

        return RiskScore(
            likelihood=likelihood,
            impact=impact,
            risk_id=risk_id,
            category=category,
            description=description,
        )

    @staticmethod
    def prioritize_risks(risks: list[RiskScore]) -> list[RiskScore]:
        """Prioritize risks by score (highest first)."""
        return sorted(risks, key=lambda r: r.score, reverse=True)

    @staticmethod
    def get_risk_distribution(risks: list[RiskScore]) -> dict[str, int]:
        """Get distribution of risk ratings."""
        distribution = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for risk in risks:
            distribution[risk.rating.value] += 1
        return distribution
