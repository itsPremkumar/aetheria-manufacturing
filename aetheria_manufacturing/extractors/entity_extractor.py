"""Entity extractor for Manufacturing Supply Chain."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class EntityType(Enum):
    PART = "part"
    SUPPLIER = "supplier"
    FACILITY = "facility"
    PROCESS = "process"
    MATERIAL = "material"
    PRODUCT = "product"


@dataclass
class Entity:
    name: str
    entity_type: EntityType
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.entity_type.value}_{hash(self.name) % 10000:04d}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class ManufacturingEntityExtractor:
    """Extracts manufacturing entities from text using regex patterns."""

    PART_PATTERNS = [
        r'\b(part\s+(?:#|number|no\.?)?\s*[\w-]+)\b',
        r'\b(component\s+[\w-]+)\b',
        r'\b([\w-]+\s+assembly)\b',
        r'\b(sku[:\s]*[\w-]+)\b',
        r'\b(p/n[:\s]*[\w-]+)\b',
    ]

    SUPPLIER_PATTERNS = [
        r'\b(supplied\s+by\s+[\w\s&.,]+?)(?:\.|,|;|$|\band\b)',
        r'\b(supplier[:\s]+[\w\s&.,]+?)(?:\.|,|;|$|\bis\b)',
        r'\b(vendor[:\s]+[\w\s&.,]+?)(?:\.|,|;|$|\bis\b)',
        r'\b(manufactured\s+by\s+[\w\s&.,]+?)(?:\.|,|;|$|\bat\b)',
    ]

    FACILITY_PATTERNS = [
        r'\b(plant\s+[\w-]+)\b',
        r'\b(facility\s+[\w-]+)\b',
        r'\b(factory\s+(?:in\s+|at\s+)?[\w\s,]+?)(?:\.|,|;|$|\bproduces\b)',
        r'\b(warehouse\s+[\w-]+)\b',
        r'\b(distribution\s+center\s+[\w-]+)\b',
    ]

    PROCESS_PATTERNS = [
        r'\b(process[:\s]+[\w\s-]+?)(?:\.|,|;|$|\bused\b)',
        r'\b([\w-]+\s+machining)\b',
        r'\b([\w-]+\s+assembly\s+line)\b',
        r'\b([\w-]+\s+production\s+process)\b',
        r'\b(cnc\s+[\w-]+)\b',
    ]

    MATERIAL_PATTERNS = [
        r'\b(material[:\s]+[\w\s-]+?)(?:\.|,|;|$|\bis\b)',
        r'\b([\w-]+\s+alloy)\b',
        r'\b([\w-]+\s+steel)\b',
        r'\b([\w-]+\s+polymer)\b',
        r'\b([\w-]+\s+composite)\b',
    ]

    PRODUCT_PATTERNS = [
        r'\b(product\s+(?:line\s+)?[\w-]+)\b',
        r'\b(model\s+[\w-]+)\b',
        r'\b(series\s+[\w-]+)\b',
    ]

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        self._part_regex = [re.compile(p, re.IGNORECASE) for p in self.PART_PATTERNS]
        self._supplier_regex = [re.compile(p, re.IGNORECASE) for p in self.SUPPLIER_PATTERNS]
        self._facility_regex = [re.compile(p, re.IGNORECASE) for p in self.FACILITY_PATTERNS]
        self._process_regex = [re.compile(p, re.IGNORECASE) for p in self.PROCESS_PATTERNS]
        self._material_regex = [re.compile(p, re.IGNORECASE) for p in self.MATERIAL_PATTERNS]
        self._product_regex = [re.compile(p, re.IGNORECASE) for p in self.PRODUCT_PATTERNS]

    def extract_parts(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._part_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.PART, confidence=0.85))
        return entities

    def extract_suppliers(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._supplier_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                name = re.sub(r'\s+(is|are|was|were|has|have)\s*$', '', name, flags=re.IGNORECASE)
                if name.lower() not in seen and len(name) > 2:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.SUPPLIER, confidence=0.80))
        return entities

    def extract_facilities(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._facility_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.FACILITY, confidence=0.82))
        return entities

    def extract_processes(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._process_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.PROCESS, confidence=0.78))
        return entities

    def extract_materials(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._material_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.MATERIAL, confidence=0.75))
        return entities

    def extract_products(self, text: str) -> List[Entity]:
        entities = []
        seen = set()
        for regex in self._product_regex:
            for match in regex.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(Entity(name=name, entity_type=EntityType.PRODUCT, confidence=0.78))
        return entities

    def extract_all(self, text: str) -> List[Entity]:
        all_entities = []
        all_entities.extend(self.extract_parts(text))
        all_entities.extend(self.extract_suppliers(text))
        all_entities.extend(self.extract_facilities(text))
        all_entities.extend(self.extract_processes(text))
        all_entities.extend(self.extract_materials(text))
        all_entities.extend(self.extract_products(text))
        return all_entities
