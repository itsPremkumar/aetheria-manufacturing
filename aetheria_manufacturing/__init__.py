"""Aetheria Manufacturing — Manufacturing Supply Chain Knowledge Graph."""

from .extractors.entity_extractor import ManufacturingEntityExtractor, Entity, EntityType
from .extractors.relation_extractor import ManufacturingRelationExtractor, Relation, RelationType
from .graph.knowledge_graph import KnowledgeGraph
from .reasoning.reasoning_engine import SupplyChainReasoningEngine
from .api.api import KnowledgeGraphAPI
from .cli.cli import main as cli_main

__version__ = "1.0.0"
from .risk.risk_analyzer import SupplyChainRiskAnalyzer, RiskScore, SupplierReliability, DisruptionPrediction

__all__ = [
    "ManufacturingEntityExtractor",
    "ManufacturingRelationExtractor",
    "KnowledgeGraph",
    "SupplyChainReasoningEngine",
    "SupplyChainRiskAnalyzer",
    "KnowledgeGraphAPI",
    "Entity",
    "EntityType",
    "Relation",
    "RelationType",
    "RiskScore",
    "SupplierReliability",
    "DisruptionPrediction",
    "cli_main",
]
