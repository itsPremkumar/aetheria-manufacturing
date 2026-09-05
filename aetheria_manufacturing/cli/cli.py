"""CLI for Manufacturing Supply Chain Knowledge Graph."""

import argparse
import json
import sys

from ..graph.knowledge_graph import KnowledgeGraph
from ..extractors.entity_extractor import ManufacturingEntityExtractor, EntityType
from ..extractors.relation_extractor import ManufacturingRelationExtractor
from ..reasoning.reasoning_engine import SupplyChainReasoningEngine
from ..api.api import KnowledgeGraphAPI


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mfg-kg",
        description="Manufacturing Supply Chain Knowledge Graph CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    extract_parser = subparsers.add_parser("extract", help="Extract entities and relations from text")
    extract_parser.add_argument("text", help="Text to extract from")

    query_parser = subparsers.add_parser("query", help="Query the knowledge graph")
    query_parser.add_argument("--type", choices=["part", "supplier", "facility", "process", "material", "product"])
    query_parser.add_argument("--name", help="Filter by name")

    sc_parser = subparsers.add_parser("supply-chain", help="Analyze supply chain for a part")
    sc_parser.add_argument("part_name", help="Part name to analyze")

    opt_parser = subparsers.add_parser("optimize", help="Optimize supply chain for a part")
    opt_parser.add_argument("part_name", help="Part name to optimize")

    sup_parser = subparsers.add_parser("analyze-supplier", help="Analyze supplier criticality")
    sup_parser.add_argument("supplier_name", help="Supplier name to analyze")

    cost_parser = subparsers.add_parser("cost-optimize", help="Cost optimization analysis")
    cost_parser.add_argument("part_name", help="Part name to analyze")

    risk_parser = subparsers.add_parser("risk-analyze", help="Risk analysis for a part")
    risk_parser.add_argument("part_name", help="Part name to analyze")

    report_parser = subparsers.add_parser("report", help="Generate supply chain report")

    stats_parser = subparsers.add_parser("stats", help="Show graph statistics")

    server_parser = subparsers.add_parser("server", help="Start API server")
    server_parser.add_argument("--host", default="localhost")
    server_parser.add_argument("--port", type=int, default=8080)

    load_parser = subparsers.add_parser("load", help="Load sample data")
    load_parser.add_argument("--num-entities", type=int, default=500, help="Number of entities to generate")

    return parser


def format_output(data: dict) -> str:
    return json.dumps(data, indent=2)


def handle_command(args, graph: KnowledgeGraph) -> str:
    entity_extractor = ManufacturingEntityExtractor()
    relation_extractor = ManufacturingRelationExtractor()
    reasoning = SupplyChainReasoningEngine(graph)

    if args.command == "extract":
        entities, relations = relation_extractor.extract_with_entity_linking(args.text)
        for entity in entities:
            graph.add_entity(entity)
        for relation in relations:
            graph.add_relation(relation)
        return format_output({
            "entities": [e.to_dict() for e in entities],
            "relations": [r.to_dict() for r in relations],
        })

    elif args.command == "query":
        et = EntityType(args.type) if args.type else None
        result = graph.query(entity_type=et, name_contains=args.name)
        return format_output(result)

    elif args.command == "supply-chain":
        return format_output(reasoning.find_supply_chain(args.part_name))

    elif args.command == "optimize":
        return format_output(reasoning.optimize_supply_chain(args.part_name))

    elif args.command == "analyze-supplier":
        return format_output(reasoning.analyze_supplier_criticality(args.supplier_name))

    elif args.command == "cost-optimize":
        return format_output(reasoning.cost_optimization(args.part_name))

    elif args.command == "risk-analyze":
        return format_output(reasoning.risk_analysis(args.part_name))

    elif args.command == "report":
        return format_output(reasoning.get_supply_chain_report())

    elif args.command == "stats":
        return format_output(graph.get_statistics())

    elif args.command == "server":
        api = KnowledgeGraphAPI(graph, host=args.host, port=args.port)
        print(f"Starting server at http://{args.host}:{args.port}")
        try:
            api.start()
        except KeyboardInterrupt:
            api.stop()
        return ""

    elif args.command == "load":
        new_graph = KnowledgeGraph.generate_sample_data(args.num_entities)
        graph.merge(new_graph)
        return format_output({"status": "loaded", "entities": len(graph.entities), "relations": len(graph.relations)})

    return "Unknown command"


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    graph = KnowledgeGraph()
    output = handle_command(args, graph)
    if output:
        print(output)


if __name__ == "__main__":
    main()
