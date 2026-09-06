"""Supply Chain Risk Analysis Module.

Provides risk scoring, supplier reliability metrics, and disruption prediction
for manufacturing supply chain knowledge graphs.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict
import random
import math

from ..graph.knowledge_graph import KnowledgeGraph
from ..extractors.entity_extractor import Entity, EntityType
from ..extractors.relation_extractor import Relation, RelationType


@dataclass
class RiskScore:
    """Represents a risk score for an entity."""
    entity_name: str
    entity_type: EntityType
    overall_score: float  # 0-100, higher = more risky
    risk_level: str  # "low", "medium", "high", "critical"
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type.value,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations,
        }


@dataclass
class SupplierReliability:
    """Represents supplier reliability metrics."""
    supplier_name: str
    on_time_delivery_rate: float  # 0-100%
    quality_score: float  # 0-100
    lead_time_avg_days: float
    lead_time_std_days: float
    fulfillment_rate: float  # 0-100%
    overall_reliability: float  # 0-100
    risk_level: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supplier_name": self.supplier_name,
            "on_time_delivery_rate": self.on_time_delivery_rate,
            "quality_score": self.quality_score,
            "lead_time_avg_days": self.lead_time_avg_days,
            "lead_time_std_days": self.lead_time_std_days,
            "fulfillment_rate": self.fulfillment_rate,
            "overall_reliability": self.overall_reliability,
            "risk_level": self.risk_level,
        }


@dataclass
class DisruptionPrediction:
    """Represents a predicted disruption risk."""
    entity_name: str
    entity_type: EntityType
    disruption_probability: float  # 0-1
    disruption_type: str
    impact_score: float  # 0-100
    affected_parts: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type.value,
            "disruption_probability": self.disruption_probability,
            "disruption_type": self.disruption_type,
            "impact_score": self.impact_score,
            "affected_parts": self.affected_parts,
            "mitigation_strategies": self.mitigation_strategies,
        }


class SupplyChainRiskAnalyzer:
    """Analyzes supply chain risks, supplier reliability, and disruption predictions."""

    def __init__(self, graph: KnowledgeGraph, seed: int = 42):
        self.graph = graph
        self._reliability_cache: Dict[str, SupplierReliability] = {}
        self._disruption_cache: Dict[str, DisruptionPrediction] = {}
        self._seed = seed

    def calculate_risk_score(self, entity_name: str) -> RiskScore:
        """Calculate comprehensive risk score for an entity."""
        entities = self.graph.find_entities_by_name(entity_name)
        if not entities:
            return RiskScore(
                entity_name=entity_name,
                entity_type=EntityType.PART,
                overall_score=0,
                risk_level="unknown",
                risk_factors=["Entity not found in graph"],
            )

        entity = entities[0]
        risk_factors = []
        recommendations = []
        risk_score = 0.0

        # Single-source risk
        suppliers = self.graph.get_suppliers_for_part(entity_name)
        if len(suppliers) == 0:
            risk_score += 40
            risk_factors.append("no_suppliers")
            recommendations.append("Add suppliers immediately")
        elif len(suppliers) == 1:
            risk_score += 25
            risk_factors.append("single_source")
            recommendations.append("Diversify supplier base")
        elif len(suppliers) <= 3:
            risk_score += 10
            risk_factors.append("limited_suppliers")

        # Manufacturing facility risk
        facilities = self.graph.get_facilities_for_part(entity_name)
        if len(facilities) == 0:
            risk_score += 20
            risk_factors.append("no_facilities")
            recommendations.append("Add manufacturing facility information")
        elif len(facilities) == 1:
            risk_score += 10
            risk_factors.append("single_facility")

        # Dependency risk
        dependencies = []
        for rel in self.graph.get_relations_from(entity.id):
            if rel.relation_type == RelationType.DEPENDS_ON:
                dependencies.append(rel.target.name)
        if len(dependencies) > 5:
            risk_score += 15
            risk_factors.append("high_dependency_count")
        elif len(dependencies) > 3:
            risk_score += 8
            risk_factors.append("moderate_dependency_count")

        # Shipment/logistics risk
        destinations = self.graph.get_shipment_destinations(entity_name)
        if len(destinations) == 0 and entity.entity_type == EntityType.PART:
            risk_score += 5
            risk_factors.append("no_shipment_info")

        # Cap at 100
        risk_score = min(risk_score, 100)

        risk_level = "critical" if risk_score >= 70 else "high" if risk_score >= 50 else "medium" if risk_score >= 30 else "low"

        return RiskScore(
            entity_name=entity_name,
            entity_type=entity.entity_type,
            overall_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )

    def calculate_supplier_reliability(self, supplier_name: str) -> SupplierReliability:
        """Calculate supplier reliability metrics."""
        if supplier_name in self._reliability_cache:
            return self._reliability_cache[supplier_name]

        entities = self.graph.find_entities_by_name(supplier_name)
        if not entities:
            return SupplierReliability(
                supplier_name=supplier_name,
                on_time_delivery_rate=0,
                quality_score=0,
                lead_time_avg_days=0,
                lead_time_std_days=0,
                fulfillment_rate=0,
                overall_reliability=0,
                risk_level="unknown",
            )

        # Simulate reliability metrics based on graph topology
        supplied_parts = self.graph.get_parts_from_supplier(supplier_name)
        num_parts = len(supplied_parts)

        # Use deterministic pseudo-random based on supplier name hash
        rng = random.Random(self._seed + hash(supplier_name) % 10000)

        # Suppliers with more parts tend to be more reliable (economies of scale)
        base_reliability = min(60 + num_parts * 2, 95)

        on_time_delivery = min(base_reliability + rng.uniform(-10, 10), 99)
        quality_score = min(base_reliability + rng.uniform(-15, 15), 99)
        lead_time_avg = max(5 + rng.uniform(-2, 15), 1)
        lead_time_std = max(1 + rng.uniform(0, 5), 0.5)
        fulfillment_rate = min(base_reliability + rng.uniform(-5, 5), 99)

        # Overall reliability is weighted average
        overall = (
            on_time_delivery * 0.3
            + quality_score * 0.25
            + fulfillment_rate * 0.25
            + max(0, 100 - lead_time_std * 10) * 0.2
        )

        risk_level = "low" if overall >= 80 else "medium" if overall >= 60 else "high" if overall >= 40 else "critical"

        reliability = SupplierReliability(
            supplier_name=supplier_name,
            on_time_delivery_rate=round(on_time_delivery, 1),
            quality_score=round(quality_score, 1),
            lead_time_avg_days=round(lead_time_avg, 1),
            lead_time_std_days=round(lead_time_std, 1),
            fulfillment_rate=round(fulfillment_rate, 1),
            overall_reliability=round(overall, 1),
            risk_level=risk_level,
        )

        self._reliability_cache[supplier_name] = reliability
        return reliability

    def predict_disruptions(self, entity_name: Optional[str] = None) -> List[DisruptionPrediction]:
        """Predict potential disruptions in the supply chain."""
        predictions = []

        if entity_name:
            entities = self.graph.find_entities_by_name(entity_name)
        else:
            # Check all suppliers and facilities
            entities = (
                self.graph.find_entities_by_type(EntityType.SUPPLIER)
                + self.graph.find_entities_by_type(EntityType.FACILITY)
            )

        for entity in entities:
            pred = self._predict_entity_disruption(entity)
            if pred:
                predictions.append(pred)

        return predictions

    def _predict_entity_disruption(self, entity: Entity) -> Optional[DisruptionPrediction]:
        """Predict disruption risk for a single entity."""
        if entity.id in self._disruption_cache:
            return self._disruption_cache[entity.id]

        rng = random.Random(self._seed + hash(entity.id) % 10000)

        disruption_prob = 0.0
        disruption_type = "none"
        impact_score = 0.0
        affected_parts = []
        mitigation_strategies = []

        if entity.entity_type == EntityType.SUPPLIER:
            # Supplier disruption risk
            supplied_parts = self.graph.get_parts_from_supplier(entity.name)
            num_parts = len(supplied_parts)

            # More parts = higher impact if disrupted
            impact_score = min(num_parts * 5, 80)

            # Base disruption probability
            disruption_prob = rng.uniform(0.05, 0.35)

            # Single-source suppliers are higher risk
            single_source_count = 0
            for part in supplied_parts:
                suppliers = self.graph.get_suppliers_for_part(part.name)
                if len(suppliers) == 1:
                    single_source_count += 1
                    affected_parts.append(part.name)

            if single_source_count > 0:
                disruption_prob += 0.15
                impact_score += 15
                disruption_type = "single_source_supplier"
                mitigation_strategies.append(
                    f"Find alternative suppliers for {single_source_count} single-source parts"
                )
            elif num_parts > 10:
                disruption_type = "high_volume_supplier"
                mitigation_strategies.append("Consider splitting orders across multiple suppliers")
            else:
                disruption_type = "standard_supplier"

            # Geographic concentration risk
            facilities = []
            for rel in self.graph.get_relations_from(entity.id):
                if rel.relation_type == RelationType.LOCATED_AT:
                    facilities.append(rel.target.name)
            if len(facilities) <= 1:
                disruption_prob += 0.1
                disruption_type = "geographic_concentration"
                mitigation_strategies.append("Diversify supplier geographic locations")

        elif entity.entity_type == EntityType.FACILITY:
            # Facility disruption risk
            manufactured_parts = []
            for rel in self.graph.get_relations_from(entity.id):
                if rel.relation_type == RelationType.MANUFACTURED_AT:
                    manufactured_parts.append(rel.target.name)

            impact_score = min(len(manufactured_parts) * 4, 70)
            disruption_prob = rng.uniform(0.05, 0.25)

            if len(manufactured_parts) > 5:
                disruption_prob += 0.1
                disruption_type = "high_volume_facility"
                mitigation_strategies.append("Consider adding backup manufacturing capacity")
            else:
                disruption_type = "standard_facility"

            affected_parts = manufactured_parts[:10]

        else:
            return None

        # Cap values
        disruption_prob = min(disruption_prob, 0.95)
        impact_score = min(impact_score, 100)

        if disruption_prob < 0.05:
            return None

        prediction = DisruptionPrediction(
            entity_name=entity.name,
            entity_type=entity.entity_type,
            disruption_probability=round(disruption_prob, 3),
            disruption_type=disruption_type,
            impact_score=round(impact_score, 1),
            affected_parts=affected_parts[:10],
            mitigation_strategies=mitigation_strategies,
        )

        self._disruption_cache[entity.id] = prediction
        return prediction

    def get_supply_chain_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive supply chain risk report."""
        all_risks = []
        all_reliability = []
        all_disruptions = []

        # Risk scores for all parts
        parts = self.graph.find_entities_by_type(EntityType.PART)
        for part in parts[:50]:  # Limit to avoid timeout
            risk = self.calculate_risk_score(part.name)
            all_risks.append(risk)

        # Reliability for all suppliers
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        for supplier in suppliers:
            reliability = self.calculate_supplier_reliability(supplier.name)
            all_reliability.append(reliability)

        # Disruption predictions
        all_disruptions = self.predict_disruptions()

        # Aggregate statistics
        risk_levels = defaultdict(int)
        for risk in all_risks:
            risk_levels[risk.risk_level] += 1

        reliability_levels = defaultdict(int)
        for rel in all_reliability:
            reliability_levels[rel.risk_level] += 1

        disruption_types = defaultdict(int)
        for pred in all_disruptions:
            disruption_types[pred.disruption_type] += 1

        avg_reliability = sum(r.overall_reliability for r in all_reliability) / max(len(all_reliability), 1)
        avg_risk = sum(r.overall_score for r in all_risks) / max(len(all_risks), 1)
        avg_disruption_prob = sum(d.disruption_probability for d in all_disruptions) / max(len(all_disruptions), 1)

        return {
            "summary": {
                "total_entities_analyzed": len(all_risks),
                "total_suppliers_analyzed": len(all_reliability),
                "total_disruption_predictions": len(all_disruptions),
                "average_reliability_score": round(avg_reliability, 1),
                "average_risk_score": round(avg_risk, 1),
                "average_disruption_probability": round(avg_disruption_prob, 3),
            },
            "risk_distribution": dict(risk_levels),
            "reliability_distribution": dict(reliability_levels),
            "disruption_types": dict(disruption_types),
            "top_risks": [r.to_dict() for r in sorted(all_risks, key=lambda x: x.overall_score, reverse=True)[:10]],
            "top_disruptions": [d.to_dict() for d in sorted(all_disruptions, key=lambda x: x.impact_score, reverse=True)[:10]],
            "supplier_reliability": [r.to_dict() for r in sorted(all_reliability, key=lambda x: x.overall_reliability, reverse=True)],
        }
