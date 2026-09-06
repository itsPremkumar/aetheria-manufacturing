"""CLI for Aetheria Cross-KG Federated Query Engine."""

import argparse
import json
import sys

from .engine import federated_query, get_kg_statistics, FederatedQueryEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aetheria Cross-KG Federated Query Engine",
        prog="aetheria-query",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Query command
    query_parser = subparsers.add_parser("query", help="Federated query across all KGs")
    query_parser.add_argument("text", help="Query text")

    # Stats command
    subparsers.add_parser("stats", help="Show KG statistics")

    # List KGs
    subparsers.add_parser("list-kgs", help="List available knowledge graphs")

    args = parser.parse_args()

    if args.command == "query":
        result = federated_query(args.text)
        print(json.dumps(result, indent=2))
    elif args.command == "stats":
        stats = get_kg_statistics()
        print(json.dumps(stats, indent=2))
    elif args.command == "list-kgs":
        engine = FederatedQueryEngine()
        print("Available Knowledge Graphs:")
        for name in engine.backends:
            print(f"  - {name}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
