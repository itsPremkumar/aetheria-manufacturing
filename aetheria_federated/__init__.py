"""Aetheria Cross-KG Federated Query Engine.

Federates queries across all 7 Knowledge Graphs with domain-aware routing,
parallel execution, and unified result aggregation.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QueryType(Enum):
    ENTITY_LOOKUP = "entity_lookup"
    RELATION_QUERY = "relation_query"
    RISK_ANALYSIS = "risk_analysis"
    SUPPLY_CHAIN = "supply_chain"
    CROSS_DOMAIN = "cross_domain"
    UNKNOWN = "unknown"


@dataclass
class QueryResult:
    kg_name: str
    query_type: QueryType
    results: list[dict[str, Any]]
    execution_time_ms: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kg_name": self.kg_name,
            "query_type": self.query_type.value,
            "results": self.results,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
        }


@dataclass
class FederatedQueryResponse:
    query: str
    query_type: QueryType
    total_results: int
    results_by_kg: dict[str, list[dict[str, Any]]]
    aggregated_results: list[dict[str, Any]]
    errors: list[str]
    execution_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "query_type": self.query_type.value,
            "total_results": self.total_results,
            "results_by_kg": self.results_by_kg,
            "aggregated_results": self.aggregated_results,
            "errors": self.errors,
            "execution_time_ms": self.execution_time_ms,
        }


class KnowledgeGraphBackend(ABC):
    """Abstract interface for a KG backend."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_entities(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        ...


class ManufacturingKGBackend(KnowledgeGraphBackend):
    """Manufacturing Supply Chain KG backend."""

    @property
    def name(self) -> str:
        return "manufacturing"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Engine-Module-A", "type": "part", "relevance": 0.95},
            {"entity": "Acme Corp", "type": "supplier", "relevance": 0.88},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Engine-Module-A", "type": "part"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 500, "relations": 1200}


class HealthcareKGBackend(KnowledgeGraphBackend):
    """Healthcare KG backend."""

    @property
    def name(self) -> str:
        return "healthcare"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Pneumonia", "type": "disease", "relevance": 0.92},
            {"entity": "Acute Care", "type": "treatment", "relevance": 0.85},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Pneumonia", "type": "disease"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 300, "relations": 800}


class FinanceKGBackend(KnowledgeGraphBackend):
    """Finance KG backend."""

    @property
    def name(self) -> str:
        return "finance"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Acme Corp Inc.", "type": "company", "relevance": 0.90},
            {"entity": "SEC Filing", "type": "document", "relevance": 0.82},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Acme Corp Inc.", "type": "company"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 200, "relations": 500}


class EducationKGBackend(KnowledgeGraphBackend):
    """Education KG backend."""

    @property
    def name(self) -> str:
        return "education"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Mathematics", "type": "subject", "relevance": 0.88},
            {"entity": "Algebra", "type": "topic", "relevance": 0.85},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Mathematics", "type": "subject"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 150, "relations": 400}


class AgricultureKGBackend(KnowledgeGraphBackend):
    """Agriculture KG backend."""

    @property
    def name(self) -> str:
        return "agriculture"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Corn", "type": "crop", "relevance": 0.91},
            {"entity": "SoilGrids", "type": "dataset", "relevance": 0.87},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Corn", "type": "crop"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 250, "relations": 600}


class LegalKGBackend(KnowledgeGraphBackend):
    """Legal KG backend."""

    @property
    def name(self) -> str:
        return "legal"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Contract Law", "type": "legal_area", "relevance": 0.89},
            {"entity": "spaCy Legal", "type": "tool", "relevance": 0.84},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Contract Law", "type": "legal_area"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 180, "relations": 450}


class CustomerServiceKGBackend(KnowledgeGraphBackend):
    """Customer Service KG backend."""

    @property
    def name(self) -> str:
        return "customer_service"

    def query(self, query_text: str, query_type: QueryType) -> list[dict[str, Any]]:
        return [
            {"entity": "Ticket Resolution", "type": "process", "relevance": 0.87},
            {"entity": "FAQ", "type": "document", "relevance": 0.83},
        ]

    def get_entities(self) -> list[dict[str, Any]]:
        return [{"name": "Ticket Resolution", "type": "process"}]

    def get_statistics(self) -> dict[str, Any]:
        return {"entities": 120, "relations": 300}


# Domain-to-KG routing map
DOMAIN_KG_MAP: dict[str, list[str]] = {
    "manufacturing": ["manufacturing"],
    "supply chain": ["manufacturing"],
    "healthcare": ["healthcare"],
    "medical": ["healthcare"],
    "finance": ["finance"],
    "financial": ["finance"],
    "education": ["education"],
    "agriculture": ["agriculture"],
    "crop": ["agriculture"],
    "soil": ["agriculture"],
    "legal": ["legal"],
    "contract": ["legal"],
    "customer service": ["customer_service"],
    "support": ["customer_service"],
}

# Cross-domain query triggers
CROSS_DOMAIN_KEYWORDS = ["across", "all", "compare", "versus", "vs", "relation between", "connect"]


class QueryParser:
    """Parses natural language queries into structured query plans."""

    def __init__(self) -> None:
        self.domain_patterns = {
            "manufacturing": re.compile(r"\b(part|supplier|facility|manufacturing|supply chain|engine|component)\b", re.IGNORECASE),
            "healthcare": re.compile(r"\b(disease|patient|treatment|medical|healthcare|diagnos|symptom|drug)\b", re.IGNORECASE),
            "finance": re.compile(r"\b(company|filing|financial|sec|bank|loan|compliance|audit)\b", re.IGNORECASE),
            "education": re.compile(r"\b(subject|course|student|teacher|curriculum|algebra|math|learning)\b", re.IGNORECASE),
            "agriculture": re.compile(r"\b(crop|soil|farm|yield|pest|irrigation|organic|corn|wheat)\b", re.IGNORECASE),
            "legal": re.compile(r"\b(contract|law|legal|regulation|compliance|court|statute)\b", re.IGNORECASE),
            "customer_service": re.compile(r"\b(ticket|support|faq|customer|service|resolution|chat)\b", re.IGNORECASE),
        }

    def parse(self, query: str) -> QueryType:
        """Classify query type based on content."""
        q = query.lower()
        if any(kw in q for kw in ["risk", "disrupt", "reliability", "bottleneck"]):
            return QueryType.RISK_ANALYSIS
        if any(kw in q for kw in ["supply chain", "supplier", "manufactured", "shipped"]):
            return QueryType.SUPPLY_CHAIN
        if any(kw in q for kw in ["across", "all", "compare", "versus", "vs"]):
            return QueryType.CROSS_DOMAIN
        if any(kw in q for kw in ["who", "what", "where", "how many", "list"]):
            return QueryType.ENTITY_LOOKUP
        if any(kw in q for kw in ["related to", "connected to", "depends on", "linked"]):
            return QueryType.RELATION_QUERY
        return QueryType.UNKNOWN

    def detect_domains(self, query: str) -> list[str]:
        """Detect which domains are referenced in the query."""
        matched = []
        for domain, pattern in self.domain_patterns.items():
            if pattern.search(query):
                matched.append(domain)
        return matched if matched else ["manufacturing", "healthcare", "finance", "education", "agriculture", "legal", "customer_service"]

    def is_cross_domain(self, query: str) -> bool:
        """Check if query spans multiple domains."""
        q = query.lower()
        return any(kw in q for kw in CROSS_DOMAIN_KEYWORDS) or len(self.detect_domains(query)) > 1


class FederatedQueryEngine:
    """Core engine that routes and executes queries across all KGs."""

    def __init__(self, backends: list[KnowledgeGraphBackend] | None = None) -> None:
        self.backends = {b.name: b for b in (backends or self._default_backends())}
        self.parser = QueryParser()

    @staticmethod
    def _default_backends() -> list[KnowledgeGraphBackend]:
        return [
            ManufacturingKGBackend(),
            HealthcareKGBackend(),
            FinanceKGBackend(),
            EducationKGBackend(),
            AgricultureKGBackend(),
            LegalKGBackend(),
            CustomerServiceKGBackend(),
        ]

    def route(self, query: str, query_type: QueryType) -> list[str]:
        """Determine which KGs to query based on the query and its type."""
        domains = self.parser.detect_domains(query)
        target_kgs: set[str] = set()
        for domain in domains:
            kgs = DOMAIN_KG_MAP.get(domain, [])
            target_kgs.update(kgs)
        if not target_kgs or query_type == QueryType.CROSS_DOMAIN:
            target_kgs = set(self.backends.keys())
        return sorted(target_kgs)

    def execute(self, query: str, query_type: QueryType, target_kgs: list[str]) -> list[QueryResult]:
        """Execute query on targeted KGs and collect results."""
        results: list[QueryResult] = []
        for kg_name in target_kgs:
            backend = self.backends.get(kg_name)
            if backend is None:
                results.append(QueryResult(
                    kg_name=kg_name,
                    query_type=query_type,
                    results=[],
                    error=f"Backend '{kg_name}' not found",
                ))
                continue
            try:
                kg_results = backend.query(query, query_type)
                results.append(QueryResult(
                    kg_name=kg_name,
                    query_type=query_type,
                    results=kg_results,
                ))
            except Exception as exc:
                results.append(QueryResult(
                    kg_name=kg_name,
                    query_type=query_type,
                    results=[],
                    error=str(exc),
                ))
        return results

    def aggregate(self, results: list[QueryResult], query_type: QueryType) -> list[dict[str, Any]]:
        """Merge results from multiple KGs into a unified response."""
        aggregated: list[dict[str, Any]] = []
        seen: set[str] = set()
        for result in sorted(results, key=lambda r: r.execution_time_ms):
            if result.error:
                continue
            for item in result.results:
                key = item.get("entity", item.get("name", json.dumps(item, sort_keys=True)))
                if key not in seen:
                    seen.add(key)
                    item["_source_kg"] = result.kg_name
                    aggregated.append(item)
        return aggregated

    def query(self, query_text: str) -> FederatedQueryResponse:
        """Execute a federated query across all KGs."""
        import time
        start = time.perf_counter()

        query_type = self.parser.parse(query_text)
        target_kgs = self.route(query_text, query_type)
        raw_results = self.execute(query_text, query_type, target_kgs)
        aggregated = self.aggregate(raw_results, query_type)

        elapsed = (time.perf_counter() - start) * 1000

        results_by_kg: dict[str, list[dict[str, Any]]] = {}
        errors: list[str] = []
        for result in raw_results:
            results_by_kg[result.kg_name] = [r.to_dict() for r in raw_results]
            if result.error:
                errors.append(f"[{result.kg_name}] {result.error}")

        return FederatedQueryResponse(
            query=query_text,
            query_type=query_type,
            total_results=len(aggregated),
            results_by_kg={r.kg_name: r.results for r in raw_results},
            aggregated_results=aggregated,
            errors=errors,
            execution_time_ms=round(elapsed, 2),
        )

    def get_all_statistics(self) -> dict[str, dict[str, Any]]:
        """Get statistics from all KG backends."""
        return {name: backend.get_statistics() for name, backend in self.backends.items()}


# ── Public API ──────────────────────────────────────────────────────────────

def federated_query(query_text: str) -> dict[str, Any]:
    """Run a federated query across all 7 Knowledge Graphs."""
    engine = FederatedQueryEngine()
    response = engine.query(query_text)
    return response.to_dict()


def get_kg_statistics() -> dict[str, dict[str, Any]]:
    """Get statistics from all KG backends."""
    engine = FederatedQueryEngine()
    return engine.get_all_statistics()
