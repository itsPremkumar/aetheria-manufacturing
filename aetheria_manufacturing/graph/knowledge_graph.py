"""Knowledge graph for Manufacturing Supply Chain."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from collections import defaultdict
import json
import random

from ..extractors.entity_extractor import Entity, EntityType
from ..extractors.relation_extractor import Relation, RelationType


@dataclass
class KnowledgeGraph:
    """In-memory knowledge graph for manufacturing supply chain data."""

    name: str = "manufacturing_supply_chain"
    entities: Dict[str, Entity] = field(default_factory=dict)
    relations: List[Relation] = field(default_factory=list)
    _adjacency: Dict[str, List[Relation]] = field(default_factory=lambda: defaultdict(list))
    _reverse_adjacency: Dict[str, List[Relation]] = field(default_factory=lambda: defaultdict(list))

    def add_entity(self, entity: Entity) -> str:
        self.entities[entity.id] = entity
        return entity.id

    def add_relation(self, relation: Relation) -> str:
        if relation.source.id not in self.entities:
            self.add_entity(relation.source)
        if relation.target.id not in self.entities:
            self.add_entity(relation.target)
        self.relations.append(relation)
        self._adjacency[relation.source.id].append(relation)
        self._reverse_adjacency[relation.target.id].append(relation)
        return relation.id

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def find_entities_by_name(self, name: str) -> List[Entity]:
        name_lower = name.lower()
        return [e for e in self.entities.values() if name_lower in e.name.lower()]

    def find_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        return [e for e in self.entities.values() if e.entity_type == entity_type]

    def get_relations_from(self, entity_id: str) -> List[Relation]:
        return self._adjacency.get(entity_id, [])

    def get_relations_to(self, entity_id: str) -> List[Relation]:
        return self._reverse_adjacency.get(entity_id, [])

    def get_all_relations(self, entity_id: str) -> List[Relation]:
        return self.get_relations_from(entity_id) + self.get_relations_to(entity_id)

    def get_neighbors(self, entity_id: str) -> List[Entity]:
        relations = self.get_all_relations(entity_id)
        neighbors = []
        for rel in relations:
            if rel.source.id == entity_id:
                neighbors.append(rel.target)
            else:
                neighbors.append(rel.source)
        return neighbors

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[str]]:
        if source_id not in self.entities or target_id not in self.entities:
            return None
        visited = {source_id}
        queue = [(source_id, [source_id])]
        while queue:
            current, path = queue.pop(0)
            if current == target_id:
                return path
            if len(path) >= max_depth:
                continue
            for rel in self._adjacency.get(current, []):
                next_id = rel.target.id
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        return None

    def get_suppliers_for_part(self, part_name: str) -> List[Entity]:
        results = []
        for entity in self.find_entities_by_name(part_name):
            for rel in self.get_relations_from(entity.id):
                if rel.relation_type == RelationType.SUPPLIED_BY:
                    results.append(rel.target)
        return results

    def get_parts_from_supplier(self, supplier_name: str) -> List[Entity]:
        results = []
        for entity in self.find_entities_by_name(supplier_name):
            for rel in self.get_relations_to(entity.id):
                if rel.relation_type == RelationType.SUPPLIED_BY:
                    results.append(rel.source)
        return results

    def get_facilities_for_part(self, part_name: str) -> List[Entity]:
        results = []
        for entity in self.find_entities_by_name(part_name):
            for rel in self.get_relations_from(entity.id):
                if rel.relation_type == RelationType.MANUFACTURED_AT:
                    results.append(rel.target)
        return results

    def get_shipment_destinations(self, part_name: str) -> List[Entity]:
        results = []
        for entity in self.find_entities_by_name(part_name):
            for rel in self.get_relations_from(entity.id):
                if rel.relation_type == RelationType.SHIPPED_TO:
                    results.append(rel.target)
        return results

    def get_requirements_for_part(self, part_name: str) -> List[Entity]:
        results = []
        for entity in self.find_entities_by_name(part_name):
            for rel in self.get_relations_from(entity.id):
                if rel.relation_type == RelationType.REQUIRES:
                    results.append(rel.target)
        return results

    def query(self, entity_type: Optional[EntityType] = None,
              relation_type: Optional[RelationType] = None,
              name_contains: Optional[str] = None) -> Dict[str, Any]:
        result = {"entities": [], "relations": []}
        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if name_contains and name_contains.lower() not in entity.name.lower():
                continue
            result["entities"].append(entity.to_dict())
        for relation in self.relations:
            if relation_type and relation.relation_type != relation_type:
                continue
            if entity_type:
                if relation.source.entity_type != entity_type and relation.target.entity_type != entity_type:
                    continue
            result["relations"].append(relation.to_dict())
        return result

    def get_statistics(self) -> Dict[str, Any]:
        type_counts = defaultdict(int)
        for entity in self.entities.values():
            type_counts[entity.entity_type.value] += 1
        relation_counts = defaultdict(int)
        for relation in self.relations:
            relation_counts[relation.relation_type.value] += 1
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "entity_types": dict(type_counts),
            "relation_types": dict(relation_counts),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entities": {eid: e.to_dict() for eid, e in self.entities.items()},
            "relations": [r.to_dict() for r in self.relations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        graph = cls(name=data.get("name", "manufacturing_supply_chain"))
        return graph

    def merge(self, other: 'KnowledgeGraph') -> 'KnowledgeGraph':
        for entity in other.entities.values():
            if entity.id not in self.entities:
                self.add_entity(entity)
        for relation in other.relations:
            self.add_relation(relation)
        return self

    @staticmethod
    def generate_sample_data(num_entities: int = 500) -> 'KnowledgeGraph':
        """Generate sample manufacturing data with 500+ entities."""
        graph = KnowledgeGraph()

        suppliers = [
            "Acme Corp", "Global Supplies", "TechCorp Industries", "Prime Parts",
            "Alpha Manufacturing", "Beta Solutions", "Gamma Supply", "Delta Components",
            "Epsilon Materials", "Zeta Industries", "Eta Corporation", "Theta Holdings",
            "Iota Industries", "Kappa Supply", "Lambda Corp", "Mu Technologies",
            "Nu Industries", "Xi Manufacturing", "Omicron Supply", "Pi Corporation"
        ]

        facilities = [
            "Plant Detroit", "Plant Chicago", "Plant Cleveland", "Plant Atlanta",
            "Plant Houston", "Plant Phoenix", "Plant Seattle", "Plant Denver",
            "Plant Boston", "Plant Portland", "Warehouse East", "Warehouse West",
            "Warehouse Central", "Distribution Center North", "Distribution Center South",
            "Factory Alpha", "Factory Beta", "Factory Gamma", "Factory Delta"
        ]

        processes = [
            "CNC Machining", "Injection Molding", "Die Casting", "Stamping",
            "Welding", "Assembly Line", "Heat Treatment", "Surface Finishing",
            "Quality Control", "Packaging", "Painting", "Plating",
            "Extrusion", "Forging", "Bending", "Cutting"
        ]

        materials = [
            "Steel Alloy", "Aluminum 6061", "Carbon Fiber", "Titanium Grade 5",
            "ABS Plastic", "Polycarbonate", "Stainless Steel", "Copper C110",
            "Brass C360", "Inconel 718", "Polypropylene", "Nylon 6/6",
            "Fiberglass", "Ceramic Composite", "Rubber Silicone", "PVC"
        ]

        product_lines = [
            "Engine-Module-A", "Engine-Module-B", "Engine-Module-C",
            "Brake-Assembly", "Brake-Assembly-X", "Brake-Assembly-Pro",
            "Transmission-Unit", "Transmission-Unit-AWD", "Transmission-Unit-4x4",
            "Suspension-System", "Suspension-System-Sport", "Suspension-System-Comfort",
            "Electrical-Harness", "Electrical-Harness-Main", "Electrical-Harness-Aux",
            "Chassis-Frame", "Chassis-Frame-Light", "Chassis-Frame-Heavy",
            "Body-Panel-Set", "Body-Panel-Set-Std", "Body-Panel-Set-Premium"
        ]

        # Add suppliers
        for name in suppliers:
            graph.add_entity(Entity(name=name, entity_type=EntityType.SUPPLIER, confidence=0.95))

        # Add facilities
        for name in facilities:
            graph.add_entity(Entity(name=name, entity_type=EntityType.FACILITY, confidence=0.95))

        # Add processes
        for name in processes:
            graph.add_entity(Entity(name=name, entity_type=EntityType.PROCESS, confidence=0.90))

        # Add materials
        for name in materials:
            graph.add_entity(Entity(name=name, entity_type=EntityType.MATERIAL, confidence=0.90))

        # Add products
        for name in product_lines:
            graph.add_entity(Entity(name=name, entity_type=EntityType.PRODUCT, confidence=0.90))

        # Generate parts to reach num_entities
        fixed_entities = len(suppliers) + len(facilities) + len(processes) + len(materials) + len(product_lines)
        num_parts = max(num_entities - fixed_entities, 100)

        part_prefixes = ["Gear", "Bolt", "Nut", "Washer", "Bearing", "Shaft", "Housing",
                         "Bracket", "Flange", "Seal", "Gasket", "Spring", "Valve", "Pump",
                         "Cylinder", "Piston", "Cam", "Rod", "Link", "Arm"]
        part_suffixes = list(range(1, 100))

        for prefix in part_prefixes:
            for suffix in part_suffixes:
                if len(graph.find_entities_by_type(EntityType.PART)) >= num_parts:
                    break
                name = f"{prefix}-{suffix:03d}"
                graph.add_entity(Entity(name=name, entity_type=EntityType.PART, confidence=0.85))
            if len(graph.find_entities_by_type(EntityType.PART)) >= num_parts:
                break

        # Add relations
        all_suppliers = graph.find_entities_by_type(EntityType.SUPPLIER)
        all_facilities = graph.find_entities_by_type(EntityType.FACILITY)
        all_processes = graph.find_entities_by_type(EntityType.PROCESS)
        all_materials = graph.find_entities_by_type(EntityType.MATERIAL)
        all_products = graph.find_entities_by_type(EntityType.PRODUCT)
        all_parts = graph.find_entities_by_type(EntityType.PART)

        random.seed(42)

        # supplied_by: parts -> suppliers
        for part in all_parts:
            if random.random() < 0.7:
                supplier = random.choice(all_suppliers)
                graph.add_relation(Relation(source=part, target=supplier, relation_type=RelationType.SUPPLIED_BY))

        # manufactured_at: parts -> facilities
        for part in all_parts:
            if random.random() < 0.6:
                facility = random.choice(all_facilities)
                graph.add_relation(Relation(source=part, target=facility, relation_type=RelationType.MANUFACTURED_AT))

        # shipped_to: parts -> facilities
        for part in all_parts:
            if random.random() < 0.4:
                facility = random.choice(all_facilities)
                graph.add_relation(Relation(source=part, target=facility, relation_type=RelationType.SHIPPED_TO))

        # requires: parts -> parts (dependencies)
        for part in all_parts:
            if random.random() < 0.3:
                other = random.choice(all_parts)
                if other.id != part.id:
                    graph.add_relation(Relation(source=part, target=other, relation_type=RelationType.REQUIRES))

        # uses_material: parts -> materials
        for part in all_parts:
            if random.random() < 0.5:
                material = random.choice(all_materials)
                graph.add_relation(Relation(source=part, target=material, relation_type=RelationType.USES_MATERIAL))

        # uses_process: parts -> processes
        for part in all_parts:
            if random.random() < 0.4:
                process = random.choice(all_processes)
                graph.add_relation(Relation(source=part, target=process, relation_type=RelationType.USES_PROCESS))

        # contains: products -> parts
        for product in all_products:
            num_parts = random.randint(3, 8)
            for _ in range(num_parts):
                part = random.choice(all_parts)
                graph.add_relation(Relation(source=product, target=part, relation_type=RelationType.CONTAINS))

        # produced_by: products -> suppliers
        for product in all_products:
            if random.random() < 0.5:
                supplier = random.choice(all_suppliers)
                graph.add_relation(Relation(source=product, target=supplier, relation_type=RelationType.PRODUCED_BY))

        # located_at: suppliers -> facilities
        for supplier in all_suppliers:
            if random.random() < 0.3:
                facility = random.choice(all_facilities)
                graph.add_relation(Relation(source=supplier, target=facility, relation_type=RelationType.LOCATED_AT))

        return graph
