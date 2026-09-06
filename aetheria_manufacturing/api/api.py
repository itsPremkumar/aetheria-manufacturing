"""API for Manufacturing Supply Chain Knowledge Graph."""

from typing import Dict, Any, Optional, List
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

from ..graph.knowledge_graph import KnowledgeGraph
from ..extractors.entity_extractor import ManufacturingEntityExtractor, EntityType
from ..extractors.relation_extractor import ManufacturingRelationExtractor
from ..reasoning.reasoning_engine import SupplyChainReasoningEngine
from ..risk.risk_analyzer import SupplyChainRiskAnalyzer


class KnowledgeGraphAPI:
    """HTTP API for the Manufacturing Knowledge Graph."""

    def __init__(self, graph: Optional[KnowledgeGraph] = None, host: str = "localhost", port: int = 8080):
        self.graph = graph or KnowledgeGraph()
        self.entity_extractor = ManufacturingEntityExtractor()
        self.relation_extractor = ManufacturingRelationExtractor()
        self.reasoning = SupplyChainReasoningEngine(self.graph)
        self.risk_analyzer = SupplyChainRiskAnalyzer(self.graph)
        self.host = host
        self.port = port
        self._server = None

    def start(self):
        handler = self._create_handler()
        self._server = HTTPServer((self.host, self.port), handler)
        self._server.serve_forever()

    def start_background(self) -> threading.Thread:
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread

    def stop(self):
        if self._server:
            self._server.shutdown()

    def _create_handler(self):
        api = self

        class KGHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/api/v1/entities":
                    self._json_response(api._get_entities())
                elif self.path == "/api/v1/relations":
                    self._json_response(api._get_relations())
                elif self.path == "/api/v1/statistics":
                    self._json_response(api.graph.get_statistics())
                elif self.path == "/api/v1/supply-chain":
                    self._json_response(api._get_supply_chain())
                elif self.path == "/api/v1/risk-report":
                    self._json_response(api._get_risk_report())
                elif self.path == "/api/v1/health":
                    self._json_response({"status": "healthy"})
                elif self.path.startswith("/api/v1/entity/"):
                    entity_id = self.path.split("/")[-1]
                    entity = api.graph.get_entity(entity_id)
                    if entity:
                        self._json_response(entity.to_dict())
                    else:
                        self._json_response({"error": "Entity not found"}, status=404)
                else:
                    self._json_response({"error": "Not found"}, status=404)

            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")

                try:
                    data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    self._json_response({"error": "Invalid JSON"}, status=400)
                    return

                if self.path == "/api/v1/extract":
                    self._json_response(api._extract_from_text(data))
                elif self.path == "/api/v1/query":
                    self._json_response(api._query_graph(data))
                elif self.path == "/api/v1/optimize":
                    self._json_response(api._optimize_supply_chain(data))
                elif self.path == "/api/v1/analyze":
                    self._json_response(api._analyze_supplier(data))
                elif self.path == "/api/v1/cost-optimize":
                    self._json_response(api._cost_optimize(data))
                elif self.path == "/api/v1/risk-analyze":
                    self._json_response(api._risk_analyze(data))
                else:
                    self._json_response({"error": "Not found"}, status=404)

            def _json_response(self, data: Dict, status: int = 200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

            def log_message(self, format, *args):
                pass

        return KGHandler

    def _get_entities(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.graph.entities.values()],
            "count": len(self.graph.entities),
        }

    def _get_relations(self) -> Dict[str, Any]:
        return {
            "relations": [r.to_dict() for r in self.graph.relations],
            "count": len(self.graph.relations),
        }

    def _get_supply_chain(self) -> Dict[str, Any]:
        return self.reasoning.get_supply_chain_report()

    def _get_risk_report(self) -> Dict[str, Any]:
        return self.risk_analyzer.get_supply_chain_risk_report()

    def _extract_from_text(self, data: Dict) -> Dict[str, Any]:
        text = data.get("text", "")
        if not text:
            return {"error": "No text provided"}

        entities, relations = self.relation_extractor.extract_with_entity_linking(text)

        for entity in entities:
            self.graph.add_entity(entity)
        for relation in relations:
            self.graph.add_relation(relation)

        return {
            "entities": [e.to_dict() for e in entities],
            "relations": [r.to_dict() for r in relations],
            "entity_count": len(entities),
            "relation_count": len(relations),
        }

    def _query_graph(self, data: Dict) -> Dict[str, Any]:
        entity_type = data.get("entity_type")
        relation_type = data.get("relation_type")
        name_contains = data.get("name_contains")

        et = EntityType(entity_type) if entity_type else None
        rt = None

        return self.graph.query(
            entity_type=et,
            relation_type=rt,
            name_contains=name_contains,
        )

    def _optimize_supply_chain(self, data: Dict) -> Dict[str, Any]:
        part_name = data.get("part_name", "")
        if not part_name:
            return {"error": "No part_name provided"}
        return self.reasoning.optimize_supply_chain(part_name)

    def _analyze_supplier(self, data: Dict) -> Dict[str, Any]:
        supplier_name = data.get("supplier_name", "")
        if not supplier_name:
            return {"error": "No supplier_name provided"}
        return self.reasoning.analyze_supplier_criticality(supplier_name)

    def _cost_optimize(self, data: Dict) -> Dict[str, Any]:
        part_name = data.get("part_name", "")
        if not part_name:
            return {"error": "No part_name provided"}
        return self.reasoning.cost_optimization(part_name)

    def _risk_analyze(self, data: Dict) -> Dict[str, Any]:
        part_name = data.get("part_name", "")
        if not part_name:
            return {"error": "No part_name provided"}
        return self.reasoning.risk_analysis(part_name)
