"""Tests for Aetheria Manufacturing Supply Chain Knowledge Graph."""

import pytest
from aetheria_manufacturing import (
    ManufacturingEntityExtractor,
    ManufacturingRelationExtractor,
    KnowledgeGraph,
    SupplyChainReasoningEngine,
    Entity,
    EntityType,
    Relation,
    RelationType,
)


# =============================================================================
# Entity Extractor Tests
# =============================================================================

class TestManufacturingEntityExtractor:
    def setup_method(self):
        self.extractor = ManufacturingEntityExtractor()

    def test_extract_parts_basic(self):
        text = "We need part #12345 for the assembly."
        entities = self.extractor.extract_parts(text)
        assert len(entities) > 0

    def test_extract_parts_sku(self):
        text = "The SKU: ABC-123 is out of stock."
        entities = self.extractor.extract_parts(text)
        assert len(entities) > 0

    def test_extract_suppliers(self):
        text = "The widget is supplied by Acme Corp."
        entities = self.extractor.extract_suppliers(text)
        assert len(entities) > 0

    def test_extract_facilities(self):
        text = "The part is built at Plant Detroit-1."
        entities = self.extractor.extract_facilities(text)
        assert len(entities) > 0

    def test_extract_processes(self):
        text = "Process: CNC Machining is used for production."
        entities = self.extractor.extract_processes(text)
        assert len(entities) > 0

    def test_extract_materials(self):
        text = "Material: carbon-fiber is used in production."
        entities = self.extractor.extract_materials(text)
        assert len(entities) > 0

    def test_extract_products(self):
        text = "The product model X-200 is now available."
        entities = self.extractor.extract_products(text)
        assert len(entities) > 0

    def test_extract_all(self):
        text = "Part #123 is supplied by Acme Corp and manufactured at Plant A."
        entities = self.extractor.extract_all(text)
        assert len(entities) >= 2

    def test_entity_has_default_id(self):
        entity = Entity(name="test-part", entity_type=EntityType.PART)
        assert entity.id is not None

    def test_entity_to_dict(self):
        entity = Entity(name="test", entity_type=EntityType.SUPPLIER, confidence=0.9)
        d = entity.to_dict()
        assert d["name"] == "test"
        assert d["type"] == "supplier"


# =============================================================================
# Relation Extractor Tests
# =============================================================================

class TestManufacturingRelationExtractor:
    def setup_method(self):
        self.extractor = ManufacturingRelationExtractor()

    def test_extract_supplied_by(self):
        text = "The widget is supplied by Acme Corp."
        relations = self.extractor.extract_relations(text)
        assert len(relations) > 0

    def test_extract_manufactured_at(self):
        text = "The part is manufactured at Plant Detroit."
        relations = self.extractor.extract_relations(text)
        assert len(relations) > 0

    def test_extract_shipped_to(self):
        text = "The widget is shipped to Warehouse Chicago."
        relations = self.extractor.extract_relations(text)
        assert len(relations) > 0

    def test_extract_requires(self):
        text = "The assembly requires the motor unit."
        relations = self.extractor.extract_relations(text)
        assert len(relations) > 0

    def test_extract_with_entity_linking(self):
        text = "The widget is supplied by Acme Corp and manufactured at Plant A."
        entities, relations = self.extractor.extract_with_entity_linking(text)
        assert len(entities) > 0
        assert len(relations) > 0


# =============================================================================
# Knowledge Graph Tests
# =============================================================================

class TestKnowledgeGraph:
    def setup_method(self):
        self.graph = KnowledgeGraph()

    def test_add_entity(self):
        entity = Entity(name="test-part", entity_type=EntityType.PART)
        eid = self.graph.add_entity(entity)
        assert eid in self.graph.entities

    def test_add_relation(self):
        source = Entity(name="part-1", entity_type=EntityType.PART)
        target = Entity(name="supplier-1", entity_type=EntityType.SUPPLIER)
        relation = Relation(source=source, target=target, relation_type=RelationType.SUPPLIED_BY)
        rid = self.graph.add_relation(relation)
        assert len(self.graph.relations) == 1

    def test_find_entities_by_name(self):
        self.graph.add_entity(Entity(name="brake-pad", entity_type=EntityType.PART))
        self.graph.add_entity(Entity(name="brake-disc", entity_type=EntityType.PART))
        results = self.graph.find_entities_by_name("brake")
        assert len(results) == 2

    def test_find_entities_by_type(self):
        self.graph.add_entity(Entity(name="part-1", entity_type=EntityType.PART))
        self.graph.add_entity(Entity(name="supplier-1", entity_type=EntityType.SUPPLIER))
        results = self.graph.find_entities_by_type(EntityType.PART)
        assert len(results) == 1

    def test_find_path(self):
        e1 = Entity(name="part-1", entity_type=EntityType.PART)
        e2 = Entity(name="supplier-1", entity_type=EntityType.SUPPLIER)
        e3 = Entity(name="facility-1", entity_type=EntityType.FACILITY)
        r1 = Relation(source=e1, target=e2, relation_type=RelationType.SUPPLIED_BY)
        r2 = Relation(source=e2, target=e3, relation_type=RelationType.LOCATED_AT)
        self.graph.add_relation(r1)
        self.graph.add_relation(r2)
        path = self.graph.find_path(e1.id, e3.id)
        assert path is not None
        assert len(path) == 3

    def test_get_statistics(self):
        self.graph.add_entity(Entity(name="part-1", entity_type=EntityType.PART))
        self.graph.add_entity(Entity(name="supplier-1", entity_type=EntityType.SUPPLIER))
        stats = self.graph.get_statistics()
        assert stats["total_entities"] == 2

    def test_query_by_type(self):
        self.graph.add_entity(Entity(name="part-1", entity_type=EntityType.PART))
        self.graph.add_entity(Entity(name="supplier-1", entity_type=EntityType.SUPPLIER))
        result = self.graph.query(entity_type=EntityType.PART)
        assert len(result["entities"]) == 1

    def test_to_json(self):
        self.graph.add_entity(Entity(name="part-1", entity_type=EntityType.PART))
        json_str = self.graph.to_json()
        assert "part-1" in json_str

    def test_merge_graphs(self):
        g1 = KnowledgeGraph()
        g1.add_entity(Entity(name="part-1", entity_type=EntityType.PART))
        g2 = KnowledgeGraph()
        g2.add_entity(Entity(name="part-2", entity_type=EntityType.PART))
        g1.merge(g2)
        assert len(g1.entities) == 2

    def test_generate_sample_data_500(self):
        graph = KnowledgeGraph.generate_sample_data(500)
        stats = graph.get_statistics()
        assert stats["total_entities"] >= 500
        assert stats["total_relations"] > 0


# =============================================================================
# Reasoning Engine Tests
# =============================================================================

class TestSupplyChainReasoningEngine:
    def setup_method(self):
        self.graph = KnowledgeGraph.generate_sample_data(500)
        self.engine = SupplyChainReasoningEngine(self.graph)

    def test_find_supply_chain(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            result = self.engine.find_supply_chain(parts[0].name)
            assert result["part"] == parts[0].name

    def test_identify_single_source_risks(self):
        risks = self.engine.identify_single_source_risks()
        assert isinstance(risks, list)

    def test_optimize_supply_chain(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            result = self.engine.optimize_supply_chain(parts[0].name)
            assert "recommendations" in result

    def test_analyze_supplier_criticality(self):
        suppliers = self.graph.find_entities_by_type(EntityType.SUPPLIER)
        if suppliers:
            result = self.engine.analyze_supplier_criticality(suppliers[0].name)
            assert "supplier" in result

    def test_find_bottlenecks(self):
        bottlenecks = self.engine.find_bottlenecks()
        assert isinstance(bottlenecks, list)

    def test_get_supply_chain_report(self):
        report = self.engine.get_supply_chain_report()
        assert "summary" in report
        assert "risk_assessment" in report

    def test_cost_optimization(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            result = self.engine.cost_optimization(parts[0].name)
            assert "cost_optimization_score" in result
            assert "recommendations" in result

    def test_risk_analysis(self):
        parts = self.graph.find_entities_by_type(EntityType.PART)
        if parts:
            result = self.engine.risk_analysis(parts[0].name)
            assert "risk_score" in result
            assert "risk_level" in result


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    def test_full_extraction_to_graph(self):
        extractor = ManufacturingRelationExtractor()
        graph = KnowledgeGraph()
        text = "The Engine-Module is supplied by Acme Corp and manufactured at Plant Detroit."
        entities, relations = extractor.extract_with_entity_linking(text)
        for entity in entities:
            graph.add_entity(entity)
        for relation in relations:
            graph.add_relation(relation)
        assert len(graph.entities) > 0
        assert len(graph.relations) > 0

    def test_extraction_to_reasoning(self):
        extractor = ManufacturingRelationExtractor()
        graph = KnowledgeGraph()
        text = """
        The Engine-Module-A is supplied by Acme Corp.
        The Brake-Assembly is supplied by Global Supplies.
        Both parts are manufactured at Plant Detroit.
        """
        entities, relations = extractor.extract_with_entity_linking(text)
        for entity in entities:
            graph.add_entity(entity)
        for relation in relations:
            graph.add_relation(relation)
        engine = SupplyChainReasoningEngine(graph)
        report = engine.get_supply_chain_report()
        assert report["summary"]["total_entities"] >= 2

    def test_sample_data_reasoning(self):
        graph = KnowledgeGraph.generate_sample_data(500)
        engine = SupplyChainReasoningEngine(graph)
        report = engine.get_supply_chain_report()
        assert report["summary"]["total_entities"] >= 500
        assert report["risk_assessment"]["total_risks"] >= 0
