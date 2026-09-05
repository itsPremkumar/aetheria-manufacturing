"""Tests for Supply Chain Risk Analysis Module."""

import pytest
from aetheria_manufacturing import (
    KnowledgeGraph,
    SupplyChainRiskAnalyzer,
    EntityType,
    Entity,
    Relation,
    RelationType,
)


class TestSupplyChainRiskAnalyzer:
    def setup_method(self):
        self.graph = KnowledgeGraph.generate_sample_data(500)
        self.analyzer = SupplyChainRiskAnalyzer(self.graph)

    def test_calculate_risk_score_returns_valid_score(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            risk = self.analyzer.calculate_risk_score(parts[0].name)
            assert risk.overall_score >= 0
            assert risk.overall_score <= 100
            assert risk.risk_level in ("low", "medium", "high", "critical", "unknown")

    def test_calculate_risk_score_unknown_entity(self):
        risk = self.analyzer.calculate_risk_score("NonExistentEntity")
        assert risk.risk_level == "unknown"
        assert "Entity not found" in risk.risk_factors[0]

    def test_risk_score_has_recommendations(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            risk = self.analyzer.calculate_risk_score(parts[0].name)
            assert isinstance(risk.recommendations, list)

    def test_risk_score_single_source_has_high_risk(self):
        # Create a part with only one supplier
        graph = KnowledgeGraph()
        part = Entity(name="single-source-part", entity_type=EntityType.PART)
        supplier = Entity(name="only-supplier", entity_type=EntityType.SUPPLIER)
        graph.add_relation(Relation(source=part, target=supplier, relation_type=RelationType.SUPPLIED_BY))
        analyzer = SupplyChainRiskAnalyzer(graph)
        risk = analyzer.calculate_risk_score("single-source-part")
        assert risk.overall_score >= 25
        assert "single_source" in risk.risk_factors

    def test_risk_score_no_suppliers_critical(self):
        graph = KnowledgeGraph()
        part = Entity(name="orphan-part", entity_type=EntityType.PART)
        graph.add_entity(part)
        analyzer = SupplyChainRiskAnalyzer(graph)
        risk = analyzer.calculate_risk_score("orphan-part")
        assert risk.overall_score >= 40
        assert "no_suppliers" in risk.risk_factors

    def test_supplier_reliability_returns_valid_metrics(self):
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            reliability = self.analyzer.calculate_supplier_reliability(suppliers[0].name)
            assert reliability.overall_reliability >= 0
            assert reliability.overall_reliability <= 100
            assert reliability.risk_level in ("low", "medium", "high", "critical", "unknown")

    def test_supplier_reliability_unknown_supplier(self):
        reliability = self.analyzer.calculate_supplier_reliability("UnknownSupplier")
        assert reliability.overall_reliability == 0

    def test_supplier_reliability_caching(self):
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            r1 = self.analyzer.calculate_supplier_reliability(suppliers[0].name)
            r2 = self.analyzer.calculate_supplier_reliability(suppliers[0].name)
            assert r1.overall_reliability == r2.overall_reliability

    def test_predict_disruptions_returns_predictions(self):
        predictions = self.analyzer.predict_disruptions()
        assert isinstance(predictions, list)
        for pred in predictions:
            assert pred.disruption_probability >= 0
            assert pred.disruption_probability <= 1
            assert pred.impact_score >= 0
            assert pred.impact_score <= 100

    def test_predict_disruptions_for_specific_entity(self):
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            predictions = self.analyzer.predict_disruptions(suppliers[0].name)
            assert isinstance(predictions, list)

    def test_disruption_prediction_has_mitigation(self):
        predictions = self.analyzer.predict_disruptions()
        for pred in predictions:
            assert isinstance(pred.mitigation_strategies, list)

    def test_get_supply_chain_risk_report_structure(self):
        report = self.analyzer.get_supply_chain_risk_report()
        assert "summary" in report
        assert "risk_distribution" in report
        assert "reliability_distribution" in report
        assert "disruption_types" in report
        assert "top_risks" in report
        assert "top_disruptions" in report
        assert "supplier_reliability" in report

    def test_risk_report_summary_fields(self):
        report = self.analyzer.get_supply_chain_risk_report()
        summary = report["summary"]
        assert summary["total_entities_analyzed"] > 0
        assert summary["total_suppliers_analyzed"] > 0
        assert "average_reliability_score" in summary
        assert "average_risk_score" in summary

    def test_risk_level_classification(self):
        assert SupplyChainRiskAnalyzer(self.graph).calculate_risk_score("nonexistent").risk_level == "unknown"

    def test_risk_score_to_dict(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            risk = self.analyzer.calculate_risk_score(parts[0].name)
            d = risk.to_dict()
            assert "entity_name" in d
            assert "overall_score" in d
            assert "risk_level" in d
            assert "risk_factors" in d
            assert "recommendations" in d

    def test_supplier_reliability_to_dict(self):
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            rel = self.analyzer.calculate_supplier_reliability(suppliers[0].name)
            d = rel.to_dict()
            assert "supplier_name" in d
            assert "on_time_delivery_rate" in d
            assert "quality_score" in d
            assert "overall_reliability" in d

    def test_disruption_prediction_to_dict(self):
        predictions = self.analyzer.predict_disruptions()
        if predictions:
            d = predictions[0].to_dict()
            assert "entity_name" in d
            assert "disruption_probability" in d
            assert "disruption_type" in d
            assert "impact_score" in d


class TestRiskModuleIntegration:
    def test_full_pipeline_with_risk(self):
        graph = KnowledgeGraph.generate_sample_data(500)
        analyzer = SupplyChainRiskAnalyzer(graph)

        # Get risk report
        report = analyzer.get_supply_chain_risk_report()
        assert report["summary"]["total_entities_analyzed"] > 0

        # Get top risks
        top_risks = report["top_risks"]
        assert len(top_risks) > 0

        # Verify risk scores are sorted descending
        if len(top_risks) >= 2:
            assert top_risks[0]["overall_score"] >= top_risks[1]["overall_score"]

    def test_risk_analysis_with_small_graph(self):
        graph = KnowledgeGraph()
        part = Entity(name="test-part", entity_type=EntityType.PART)
        supplier = Entity(name="test-supplier", entity_type=EntityType.SUPPLIER)
        facility = Entity(name="test-facility", entity_type=EntityType.FACILITY)
        graph.add_relation(Relation(source=part, target=supplier, relation_type=RelationType.SUPPLIED_BY))
        graph.add_relation(Relation(source=part, target=facility, relation_type=RelationType.MANUFACTURED_AT))

        analyzer = SupplyChainRiskAnalyzer(graph)
        risk = analyzer.calculate_risk_score("test-part")
        assert risk.entity_name == "test-part"
        assert risk.overall_score < 50  # Low risk with supplier + facility

    def test_supplier_reliability_deterministic(self):
        graph = KnowledgeGraph.generate_sample_data(100)
        analyzer1 = SupplyChainRiskAnalyzer(graph, seed=42)
        analyzer2 = SupplyChainRiskAnalyzer(graph, seed=42)

        suppliers = graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            r1 = analyzer1.calculate_supplier_reliability(suppliers[0].name)
            r2 = analyzer2.calculate_supplier_reliability(suppliers[0].name)
            assert r1.overall_reliability == r2.overall_reliability
