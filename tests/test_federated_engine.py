"""Tests for Aetheria Cross-KG Federated Query Engine."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aetheria_federated.engine import (
    FederatedQueryEngine,
    QueryParser,
    QueryType,
    ManufacturingKGBackend,
    HealthcareKGBackend,
    FinanceKGBackend,
    EducationKGBackend,
    AgricultureKGBackend,
    LegalKGBackend,
    CustomerServiceKGBackend,
)
from aetheria_federated import federated_query, get_kg_statistics


class TestQueryParser:
    def test_parse_supply_chain_query(self):
        parser = QueryParser()
        qt = parser.parse("supply chain for Engine-Module-A")
        assert qt == QueryType.SUPPLY_CHAIN

    def test_parse_risk_query(self):
        parser = QueryParser()
        qt = parser.parse("What are the risks for Acme Corp?")
        assert qt == QueryType.RISK_ANALYSIS

    def test_parse_cross_domain_query(self):
        parser = QueryParser()
        qt = parser.parse("Compare across all KGs")
        assert qt == QueryType.CROSS_DOMAIN

    def test_parse_entity_lookup(self):
        parser = QueryParser()
        qt = parser.parse("What is Engine-Module-A?")
        assert qt == QueryType.ENTITY_LOOKUP

    def test_parse_relation_query(self):
        parser = QueryParser()
        # "related to" matches RELATION_QUERY keywords
        qt = parser.parse("related to manufacturing")
        assert qt == QueryType.RELATION_QUERY

    def test_detect_manufacturing_domain(self):
        parser = QueryParser()
        domains = parser.detect_domains("Part supplied by Acme Corp")
        assert "manufacturing" in domains

    def test_detect_healthcare_domain(self):
        parser = QueryParser()
        domains = parser.detect_domains("Patient with pneumonia")
        assert "healthcare" in domains

    def test_detect_finance_domain(self):
        parser = QueryParser()
        domains = parser.detect_domains("SEC filing for Acme Corp")
        assert "finance" in domains

    def test_is_cross_domain(self):
        parser = QueryParser()
        assert parser.is_cross_domain("Compare healthcare and manufacturing") is True

    def test_is_not_cross_domain(self):
        parser = QueryParser()
        assert parser.is_cross_domain("What supplies Engine-Module-A") is False


class TestManufacturingKGBackend:
    def test_name(self):
        backend = ManufacturingKGBackend()
        assert backend.name == "manufacturing"

    def test_query(self):
        backend = ManufacturingKGBackend()
        results = backend.query("What supplies Engine-Module-A?", QueryType.SUPPLY_CHAIN)
        assert len(results) > 0
        assert results[0]["type"] == "part"

    def test_get_entities(self):
        backend = ManufacturingKGBackend()
        entities = backend.get_entities()
        assert len(entities) > 0

    def test_get_statistics(self):
        backend = ManufacturingKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 500


class TestHealthcareKGBackend:
    def test_name(self):
        backend = HealthcareKGBackend()
        assert backend.name == "healthcare"

    def test_query(self):
        backend = HealthcareKGBackend()
        results = backend.query("Patient with pneumonia", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "disease"

    def test_get_statistics(self):
        backend = HealthcareKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 300


class TestFinanceKGBackend:
    def test_name(self):
        backend = FinanceKGBackend()
        assert backend.name == "finance"

    def test_query(self):
        backend = FinanceKGBackend()
        results = backend.query("SEC filing for Acme Corp", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "company"

    def test_get_statistics(self):
        backend = FinanceKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 200


class TestEducationKGBackend:
    def test_name(self):
        backend = EducationKGBackend()
        assert backend.name == "education"

    def test_query(self):
        backend = EducationKGBackend()
        results = backend.query("Mathematics curriculum", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "subject"

    def test_get_statistics(self):
        backend = EducationKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 150


class TestAgricultureKGBackend:
    def test_name(self):
        backend = AgricultureKGBackend()
        assert backend.name == "agriculture"

    def test_query(self):
        backend = AgricultureKGBackend()
        results = backend.query("Corn crop yield", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "crop"

    def test_get_statistics(self):
        backend = AgricultureKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 250


class TestLegalKGBackend:
    def test_name(self):
        backend = LegalKGBackend()
        assert backend.name == "legal"

    def test_query(self):
        backend = LegalKGBackend()
        results = backend.query("Contract law regulation", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "legal_area"

    def test_get_statistics(self):
        backend = LegalKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 180


class TestCustomerServiceKGBackend:
    def test_name(self):
        backend = CustomerServiceKGBackend()
        assert backend.name == "customer_service"

    def test_query(self):
        backend = CustomerServiceKGBackend()
        results = backend.query("Ticket resolution process", QueryType.ENTITY_LOOKUP)
        assert len(results) > 0
        assert results[0]["type"] == "process"

    def test_get_statistics(self):
        backend = CustomerServiceKGBackend()
        stats = backend.get_statistics()
        assert stats["entities"] == 120


class TestFederatedQueryEngine:
    def test_engine_initializes(self):
        engine = FederatedQueryEngine()
        assert len(engine.backends) == 7

    def test_route_manufacturing(self):
        engine = FederatedQueryEngine()
        kgs = engine.route("What supplies Engine-Module-A?", QueryType.SUPPLY_CHAIN)
        assert "manufacturing" in kgs

    def test_route_healthcare(self):
        engine = FederatedQueryEngine()
        kgs = engine.route("Patient with pneumonia", QueryType.ENTITY_LOOKUP)
        assert "healthcare" in kgs

    def test_route_cross_domain(self):
        engine = FederatedQueryEngine()
        kgs = engine.route("Compare across all KGs", QueryType.CROSS_DOMAIN)
        assert len(kgs) == 7

    def test_execute_query(self):
        engine = FederatedQueryEngine()
        results = engine.execute("test", QueryType.ENTITY_LOOKUP, ["manufacturing"])
        assert len(results) == 1
        assert results[0].kg_name == "manufacturing"
        assert results[0].error is None

    def test_aggregate_results(self):
        engine = FederatedQueryEngine()
        results = engine.execute("test", QueryType.ENTITY_LOOKUP, ["manufacturing", "healthcare"])
        aggregated = engine.aggregate(results, QueryType.ENTITY_LOOKUP)
        assert len(aggregated) > 0

    def test_federated_query(self):
        response = federated_query("risk for Engine-Module-A")
        assert response["query_type"] == "risk_analysis"
        assert response["total_results"] > 0
        assert response["errors"] == []

    def test_federated_query_cross_domain(self):
        response = federated_query("Compare healthcare and manufacturing")
        assert response["query_type"] == "cross_domain"
        assert len(response["results_by_kg"]) == 7

    def test_get_all_statistics(self):
        stats = get_kg_statistics()
        assert len(stats) == 7
        for kg_name in ["manufacturing", "healthcare", "finance", "education", "agriculture", "legal", "customer_service"]:
            assert kg_name in stats

    def test_federated_query_with_error(self):
        engine = FederatedQueryEngine(backends=[])
        # With empty backends, route returns empty list, execute produces no results
        response = engine.query("test")
        assert response.total_results == 0

    def test_aggregated_results_deduplicated(self):
        engine = FederatedQueryEngine()
        results = engine.execute("test", QueryType.ENTITY_LOOKUP, ["manufacturing", "healthcare"])
        aggregated = engine.aggregate(results, QueryType.ENTITY_LOOKUP)
        keys = [r.get("entity", r.get("name")) for r in aggregated]
        assert len(keys) == len(set(keys))


class TestQueryResult:
    def test_to_dict(self):
        from aetheria_federated.engine import QueryResult
        result = QueryResult(
            kg_name="manufacturing",
            query_type=QueryType.SUPPLY_CHAIN,
            results=[{"entity": "test", "type": "part"}],
            execution_time_ms=1.5,
        )
        d = result.to_dict()
        assert d["kg_name"] == "manufacturing"
        assert d["query_type"] == "supply_chain"
        assert d["results"] == [{"entity": "test", "type": "part"}]
        assert d["execution_time_ms"] == 1.5
        assert d["error"] is None


class TestFederatedQueryResponse:
    def test_to_dict(self):
        from aetheria_federated.engine import FederatedQueryResponse, QueryType
        response = FederatedQueryResponse(
            query="test",
            query_type=QueryType.ENTITY_LOOKUP,
            total_results=2,
            results_by_kg={"manufacturing": []},
            aggregated_results=[{"entity": "test", "type": "part"}],
            errors=[],
            execution_time_ms=1.0,
        )
        d = response.to_dict()
        assert d["query"] == "test"
        assert d["total_results"] == 2
        assert d["errors"] == []