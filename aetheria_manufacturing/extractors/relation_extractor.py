"""Relation extractor for Manufacturing Supply Chain."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from .entity_extractor import Entity, EntityType


class RelationType(Enum):
    SUPPLIED_BY = "supplied_by"
    MANUFACTURED_AT = "manufactured_at"
    SHIPPED_TO = "shipped_to"
    REQUIRES = "requires"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    PRODUCED_BY = "produced_by"
    LOCATED_AT = "located_at"
    USES_MATERIAL = "uses_material"
    USES_PROCESS = "uses_process"


@dataclass
class Relation:
    source: Entity
    target: Entity
    relation_type: RelationType
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"rel_{hash(self.source.name + self.target.name + self.relation_type.value) % 10000:04d}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "relation": self.relation_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class ManufacturingRelationExtractor:
    """Extracts manufacturing relations between entities from text."""

    RELATION_PATTERNS: List[Tuple[RelationType, str]] = [
        (RelationType.SUPPLIED_BY, r'(?P<part>[\w\s#-]+?)\s+is\s+supplied\s+by\s+(?P<supplier>[\w\s&.,]+?)(?:\.|,|;|$|\band\b)'),
        (RelationType.SUPPLIED_BY, r'(?P<supplier>[\w\s&.,]+?)\s+supplies\s+(?P<part>[\w\s#-]+?)(?:\.|,|;|$|\bto\b)'),
        (RelationType.MANUFACTURED_AT, r'(?P<part>[\w\s#-]+?)\s+is\s+manufactured\s+(?:at|in)\s+(?P<facility>[\w\s,.-]+?)(?:\.|,|;|$|\bby\b)'),
        (RelationType.MANUFACTURED_AT, r'(?P<facility>[\w\s,.-]+?)\s+manufactures\s+(?P<part>[\w\s#-]+?)(?:\.|,|;|$|\bfor\b)'),
        (RelationType.SHIPPED_TO, r'(?P<part>[\w\s#-]+?)\s+is\s+shipped\s+to\s+(?P<destination>[\w\s,.-]+?)(?:\.|,|;|$|\bfrom\b)'),
        (RelationType.SHIPPED_TO, r'(?P<part>[\w\s#-]+?)\s+ships\s+to\s+(?P<destination>[\w\s,.-]+?)(?:\.|,|;|$|\bfrom\b)'),
        (RelationType.REQUIRES, r'(?P<part>[\w\s#-]+?)\s+requires\s+(?P<requirement>[\w\s#-]+?)(?:\.|,|;|$|\bfor\b)'),
        (RelationType.REQUIRES, r'(?P<process>[\w\s#-]+?)\s+requires\s+(?P<resource>[\w\s#-]+?)(?:\.|,|;|$|\bfor\b)'),
        (RelationType.CONTAINS, r'(?P<product>[\w\s#-]+?)\s+contains\s+(?P<component>[\w\s#-]+?)(?:\.|,|;|$|\bwhich\b)'),
        (RelationType.DEPENDS_ON, r'(?P<part>[\w\s#-]+?)\s+depends?\s+on\s+(?P<dependency>[\w\s#-]+?)(?:\.|,|;|$|\bfor\b)'),
        (RelationType.PRODUCED_BY, r'(?P<product>[\w\s#-]+?)\s+is\s+produced\s+by\s+(?P<producer>[\w\s&.,]+?)(?:\.|,|;|$|\bat\b)'),
        (RelationType.LOCATED_AT, r'(?P<entity>[\w\s#-]+?)\s+is\s+located\s+(?:at|in)\s+(?P<location>[\w\s,.-]+?)(?:\.|,|;|$|\bnear\b)'),
        (RelationType.USES_MATERIAL, r'(?P<part>[\w\s#-]+?)\s+uses\s+(?P<material>[\w\s]+?)(?:\.|,|;|$|\bfor\b)'),
        (RelationType.USES_PROCESS, r'(?P<part>[\w\s#-]+?)\s+uses\s+(?P<process>[\w\s]+?)(?:\.|,|;|$|\bfor\b)'),
    ]

    def __init__(self):
        self._compiled_patterns = []
        for rel_type, pattern in self.RELATION_PATTERNS:
            self._compiled_patterns.append(
                (rel_type, re.compile(pattern, re.IGNORECASE))
            )

    def extract_relations(self, text: str, entities: Optional[List[Entity]] = None) -> List[Relation]:
        relations = []
        for rel_type, regex in self._compiled_patterns:
            for match in regex.finditer(text):
                relation = self._build_relation_from_match(rel_type, match, entities)
                if relation:
                    relations.append(relation)
        return relations

    def _build_relation_from_match(
        self, rel_type: RelationType, match: re.Match, entities: Optional[List[Entity]]
    ) -> Optional[Relation]:
        groups = match.groupdict()
        source_name = None
        target_name = None

        if rel_type == RelationType.SUPPLIED_BY:
            if "part" in groups and "supplier" in groups:
                source_name = groups["part"].strip()
                target_name = groups["supplier"].strip()
            elif "supplier" in groups and "part" in groups:
                source_name = groups["supplier"].strip()
                target_name = groups["part"].strip()
        elif rel_type == RelationType.MANUFACTURED_AT:
            if "part" in groups and "facility" in groups:
                source_name = groups["part"].strip()
                target_name = groups["facility"].strip()
            elif "facility" in groups and "part" in groups:
                source_name = groups["facility"].strip()
                target_name = groups["part"].strip()
        elif rel_type == RelationType.SHIPPED_TO:
            source_name = groups.get("part", "").strip()
            target_name = groups.get("destination", "").strip()
        elif rel_type == RelationType.REQUIRES:
            source_name = groups.get("part", groups.get("process", "")).strip()
            target_name = groups.get("requirement", groups.get("resource", "")).strip()
        elif rel_type == RelationType.CONTAINS:
            source_name = groups.get("product", "").strip()
            target_name = groups.get("component", "").strip()
        elif rel_type == RelationType.DEPENDS_ON:
            source_name = groups.get("part", "").strip()
            target_name = groups.get("dependency", "").strip()
        elif rel_type == RelationType.PRODUCED_BY:
            source_name = groups.get("product", "").strip()
            target_name = groups.get("producer", "").strip()
        elif rel_type == RelationType.LOCATED_AT:
            source_name = groups.get("entity", "").strip()
            target_name = groups.get("location", "").strip()
        elif rel_type == RelationType.USES_MATERIAL:
            source_name = groups.get("part", "").strip()
            target_name = groups.get("material", "").strip()
        elif rel_type == RelationType.USES_PROCESS:
            source_name = groups.get("part", "").strip()
            target_name = groups.get("process", "").strip()

        if not source_name or not target_name:
            return None

        source_name = self._clean_entity_name(source_name)
        target_name = self._clean_entity_name(target_name)

        if len(source_name) < 2 or len(target_name) < 2:
            return None

        source_entity = self._find_or_create_entity(source_name, entities)
        target_entity = self._find_or_create_entity(target_name, entities)

        return Relation(
            source=source_entity,
            target=target_entity,
            relation_type=rel_type,
            confidence=0.80,
            metadata={"source": "pattern_match", "span": match.span()}
        )

    def _clean_entity_name(self, name: str) -> str:
        name = re.sub(r'\s+(is|are|was|were|has|have|and|or|the|a|an)\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(the|a|an)\s+', '', name, flags=re.IGNORECASE)
        return name.strip()

    def _find_or_create_entity(self, name: str, entities: Optional[List[Entity]]) -> Entity:
        if entities:
            for entity in entities:
                if entity.name.lower() == name.lower():
                    return entity
        entity_type = self._infer_entity_type(name)
        return Entity(name=name, entity_type=entity_type, confidence=0.70)

    def _infer_entity_type(self, name: str) -> EntityType:
        name_lower = name.lower()
        if any(kw in name_lower for kw in ['part', 'component', 'assembly', 'sku']):
            return EntityType.PART
        elif any(kw in name_lower for kw in ['supplier', 'vendor', 'manufacturer', 'corp', 'inc', 'ltd']):
            return EntityType.SUPPLIER
        elif any(kw in name_lower for kw in ['plant', 'factory', 'facility', 'warehouse', 'center']):
            return EntityType.FACILITY
        elif any(kw in name_lower for kw in ['process', 'machining', 'line', 'cnc']):
            return EntityType.PROCESS
        elif any(kw in name_lower for kw in ['material', 'alloy', 'steel', 'polymer', 'composite']):
            return EntityType.MATERIAL
        elif any(kw in name_lower for kw in ['product', 'model', 'series']):
            return EntityType.PRODUCT
        return EntityType.PART

    def extract_with_entity_linking(self, text: str) -> Tuple[List[Entity], List[Relation]]:
        from .entity_extractor import ManufacturingEntityExtractor
        extractor = ManufacturingEntityExtractor()
        entities = extractor.extract_all(text)
        relations = self.extract_relations(text, entities)
        return entities, relations
