"""Reasoning engine for Manufacturing Supply Chain optimization."""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import heapq

from ..graph.knowledge_graph import KnowledgeGraph
from ..extractors.entity_extractor import Entity, EntityType
from ..extractors.relation_extractor import Relation, RelationType


@dataclass
class SupplyChainPath:
    """Represents a path through the supply chain."""
    steps: List[Entity]
    relations: List[Relation]
    total_cost: float = 0.0
    risk_score: float = 0.0

    @property
    def length(self) -> int:
        return len(self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [e.to_dict() for e in self.steps],
            "relations": [r.to_dict() for r in self.relations],
            "total_cost": self.total_cost,
            "risk_score": self.risk_score,
            "length": self.length,
        }


class SupplyChainReasoningEngine:
    """Reasoning engine for supply chain optimization and analysis."""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def find_supply_chain(self, part_name: str) -> Dict[str, Any]:
        """Find complete supply chain for a part."""
        result = {
            "part": part_name,
            "suppliers": [],
            "manufacturing_facilities": [],
            "shipment_destinations": [],
            "dependencies": [],
        }

        entities = self.graph.find_entities_by_name(part_name)
        for entity in entities:
            for rel in self.graph.get_relations_from(entity.id):
                if rel.relation_type == RelationType.SUPPLIED_BY:
                    result["suppliers"].append({
                        "name": rel.target.name,
                        "confidence": rel.confidence,
                    })
                elif rel.relation_type == RelationType.MANUFACTURED_AT:
                    result["manufacturing_facilities"].append({
                        "name": rel.target.name,
                        "confidence": rel.confidence,
                    })
                elif rel.relation_type == RelationType.SHIPPED_TO:
                    result["shipment_destinations"].append({
                        "name": rel.target.name,
                        "confidence": rel.confidence,
                    })
                elif rel.relation_type == RelationType.DEPENDS_ON:
                    result["dependencies"].append({
                        "name": rel.target.name,
                        "confidence": rel.confidence,
                    })

        return result

    def identify_single_source_risks(self) -> List[Dict[str, Any]]:
        """Identify parts that have only a single supplier (risk factor)."""
        risks = []
        parts = self.graph.find_entities_by_type(EntityType.PART)

        for part in parts:
            suppliers = []
            for rel in self.graph.get_relations_from(part.id):
                if rel.relation_type == RelationType.SUPPLIED_BY:
                    suppliers.append(rel.target.name)

            if len(suppliers) == 1:
                risks.append({
                    "part": part.name,
                    "risk": "single_source",
                    "supplier": suppliers[0],
                    "severity": "high",
                    "recommendation": f"Find alternative suppliers for {part.name}",
                })
            elif len(suppliers) == 0:
                risks.append({
                    "part": part.name,
                    "risk": "no_supplier",
                    "supplier": None,
                    "severity": "critical",
                    "recommendation": f"Add supplier information for {part.name}",
                })

        return risks

    def find_alternative_suppliers(self, part_name: str) -> List[Dict[str, Any]]:
        """Find alternative suppliers for a part based on graph topology."""
        alternatives = []
        entities = self.graph.find_entities_by_name(part_name)

        for entity in entities:
            current_suppliers = set()
            for rel in self.graph.get_relations_to(entity.id):
                if rel.relation_type == RelationType.SUPPLIED_BY:
                    current_suppliers.add(rel.source.name)

            all_suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
            for supplier in all_suppliers:
                if supplier.name in current_suppliers:
                    continue
                supplied_parts = self.graph.get_parts_from_supplier(supplier.name)
                if supplied_parts:
                    alternatives.append({
                        "supplier": supplier.name,
                        "similar_parts": [p.name for p in supplied_parts[:5]],
                        "relevance": len(supplied_parts),
                    })

        return alternatives

    def optimize_supply_chain(self, part_name: str) -> Dict[str, Any]:
        """Generate optimization recommendations for a part's supply chain."""
        supply_chain = self.find_supply_chain(part_name)
        risks = self.identify_single_source_risks()
        alternatives = self.find_alternative_suppliers(part_name)

        part_risks = [r for r in risks if r["part"] == part_name]

        recommendations = []
        if part_risks:
            for risk in part_risks:
                if risk["risk"] == "single_source":
                    recommendations.append({
                        "type": "diversify_suppliers",
                        "priority": "high",
                        "detail": risk["recommendation"],
                        "alternatives": alternatives[:3],
                    })
                elif risk["risk"] == "no_supplier":
                    recommendations.append({
                        "type": "add_supplier",
                        "priority": "critical",
                        "detail": risk["recommendation"],
                    })

        if not supply_chain["manufacturing_facilities"]:
            recommendations.append({
                "type": "add_manufacturing_info",
                "priority": "medium",
                "detail": f"Add manufacturing facility information for {part_name}",
            })

        if not supply_chain["shipment_destinations"]:
            recommendations.append({
                "type": "add_logistics_info",
                "priority": "low",
                "detail": f"Add shipment/delivery information for {part_name}",
            })

        return {
            "part": part_name,
            "current_supply_chain": supply_chain,
            "risks": part_risks,
            "recommendations": recommendations,
            "alternative_suppliers": alternatives[:5],
        }

    def analyze_supplier_criticality(self, supplier_name: str) -> Dict[str, Any]:
        """Analyze how critical a supplier is to the supply chain."""
        entities = self.graph.find_entities_by_name(supplier_name)
        if not entities:
            return {"error": f"Supplier '{supplier_name}' not found"}

        supplier_entity = entities[0]
        supplied_parts = self.graph.get_parts_from_supplier(supplier_name)

        criticality_score = 0
        single_source_parts = []

        for part in supplied_parts:
            suppliers = self.graph.get_suppliers_for_part(part.name)
            if len(suppliers) == 1:
                criticality_score += 2
                single_source_parts.append(part.name)
            else:
                criticality_score += 1

        return {
            "supplier": supplier_name,
            "total_parts_supplied": len(supplied_parts),
            "parts": [p.name for p in supplied_parts],
            "criticality_score": criticality_score,
            "single_source_parts": single_source_parts,
            "risk_level": "high" if len(single_source_parts) > 2 else "medium" if single_source_parts else "low",
        }

    def find_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottleneck suppliers and facilities in the supply chain."""
        bottlenecks = []

        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        for supplier in suppliers:
            analysis = self.analyze_supplier_criticality(supplier.name)
            if analysis.get("criticality_score", 0) > 3:
                bottlenecks.append({
                    "entity": supplier.name,
                    "type": "supplier",
                    "criticality_score": analysis["criticality_score"],
                    "single_source_count": len(analysis.get("single_source_parts", [])),
                })

        facilities = self.graph.find_entities_by_type(EntityType.FACILITY)
        for facility in facilities:
            manufactured_parts = []
            for rel in self.graph.get_relations_from(facility.id):
                if rel.relation_type == RelationType.MANUFACTURED_AT:
                    manufactured_parts.append(rel.target.name)

            if len(manufactured_parts) > 3:
                bottlenecks.append({
                    "entity": facility.name,
                    "type": "facility",
                    "parts_count": len(manufactured_parts),
                    "parts": manufactured_parts,
                })

        return sorted(bottlenecks, key=lambda x: x.get("criticality_score", x.get("parts_count", 0)), reverse=True)

    def get_supply_chain_report(self) -> Dict[str, Any]:
        """Generate a comprehensive supply chain report."""
        stats = self.graph.get_statistics()
        risks = self.identify_single_source_risks()
        bottlenecks = self.find_bottlenecks()

        critical_risks = [r for r in risks if r["severity"] == "critical"]
        high_risks = [r for r in risks if r["severity"] == "high"]

        return {
            "summary": stats,
            "risk_assessment": {
                "total_risks": len(risks),
                "critical": len(critical_risks),
                "high": len(high_risks),
                "details": risks,
            },
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_overall_recommendations(risks, bottlenecks),
        }

    def _generate_overall_recommendations(self, risks: List[Dict], bottlenecks: List[Dict]) -> List[Dict]:
        """Generate overall supply chain recommendations."""
        recommendations = []

        critical_count = sum(1 for r in risks if r["severity"] == "critical")
        if critical_count > 0:
            recommendations.append({
                "type": "urgent_action",
                "priority": "critical",
                "detail": f"{critical_count} parts have no supplier information",
            })

        high_risk_count = sum(1 for r in risks if r["severity"] == "high")
        if high_risk_count > 0:
            recommendations.append({
                "type": "diversify",
                "priority": "high",
                "detail": f"{high_risk_count} parts rely on single suppliers",
            })

        if bottlenecks:
            recommendations.append({
                "type": "address_bottlenecks",
                "priority": "medium",
                "detail": f"{len(bottlenecks)} bottlenecks identified in the supply chain",
            })

        return recommendations

    def cost_optimization(self, part_name: str) -> Dict[str, Any]:
        """Analyze cost optimization opportunities for a part."""
        supply_chain = self.find_supply_chain(part_name)
        suppliers = supply_chain["suppliers"]
        facilities = supply_chain["manufacturing_facilities"]

        # Simulate cost analysis based on supplier count and facility utilization
        num_suppliers = len(suppliers)
        num_facilities = len(facilities)

        cost_score = 0
        recommendations = []

        if num_suppliers == 0:
            cost_score = 0
            recommendations.append({
                "type": "add_suppliers",
                "priority": "critical",
                "detail": f"No suppliers found for {part_name}. Add suppliers to enable cost comparison.",
            })
        elif num_suppliers == 1:
            cost_score = 30
            recommendations.append({
                "type": "increase_competition",
                "priority": "high",
                "detail": f"Only one supplier for {part_name}. Add 2-3 alternative suppliers to reduce costs by 15-25%.",
            })
        elif num_suppliers <= 3:
            cost_score = 60
            recommendations.append({
                "type": "optimize_mix",
                "priority": "medium",
                "detail": f"Good supplier base ({num_suppliers} suppliers). Negotiate volume discounts.",
            })
        else:
            cost_score = 85
            recommendations.append({
                "type": "consolidate",
                "priority": "low",
                "detail": f"Strong supplier competition ({num_suppliers} suppliers). Consider consolidating for volume pricing.",
            })

        if num_facilities == 0:
            recommendations.append({
                "type": "add_facilities",
                "priority": "medium",
                "detail": f"No manufacturing facilities linked to {part_name}.",
            })
        elif num_facilities > 5:
            recommendations.append({
                "type": "optimize_production",
                "priority": "low",
                "detail": f"Production spread across {num_facilities} facilities. Consider consolidating for efficiency.",
            })

        return {
            "part": part_name,
            "cost_optimization_score": cost_score,
            "num_suppliers": num_suppliers,
            "num_facilities": num_facilities,
            "recommendations": recommendations,
        }

    def risk_analysis(self, part_name: str) -> Dict[str, Any]:
        """Comprehensive risk analysis for a part's supply chain."""
        supply_chain = self.find_supply_chain(part_name)
        risks = self.identify_single_source_risks()
        part_risks = [r for r in risks if r["part"] == part_name]

        # Calculate overall risk score
        risk_score = 0
        risk_factors = []

        suppliers = supply_chain["suppliers"]
        if len(suppliers) == 0:
            risk_score += 50
            risk_factors.append("no_suppliers")
        elif len(suppliers) == 1:
            risk_score += 30
            risk_factors.append("single_source")
        elif len(suppliers) <= 3:
            risk_score += 10
            risk_factors.append("limited_suppliers")

        facilities = supply_chain["manufacturing_facilities"]
        if len(facilities) == 0:
            risk_score += 20
            risk_factors.append("no_facilities")
        elif len(facilities) == 1:
            risk_score += 10
            risk_factors.append("single_facility")

        dependencies = supply_chain["dependencies"]
        if len(dependencies) > 5:
            risk_score += 15
            risk_factors.append("high_dependency_count")

        # Cap at 100
        risk_score = min(risk_score, 100)

        risk_level = "critical" if risk_score >= 70 else "high" if risk_score >= 50 else "medium" if risk_score >= 30 else "low"

        return {
            "part": part_name,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "supply_chain": supply_chain,
            "recommendations": self.optimize_supply_chain(part_name)["recommendations"],
        }
