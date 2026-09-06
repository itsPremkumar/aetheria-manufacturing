"""Command-line interface for the agriculture KG."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure src is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agri_kg.database import Database  # noqa: E402
from agri_kg.engine import (  # noqa: E402
    CropSoilMatcher,
    PestDiseaseIdentifier,
    SeasonalReasoner,
    WeatherMapper,
)
from agri_kg.seed_data import seed_database  # noqa: E402


def cmd_seed(args: argparse.Namespace) -> None:
    """Seed the database with sample data."""
    db = Database(args.db_path)
    seed_database(db)
    print(f"Database seeded at {args.db_path}")
    db.close()


def cmd_demo(args: argparse.Namespace) -> None:
    """Run a demonstration of the KG capabilities."""
    db = Database(args.db_path)
    seed_database(db)

    print("=" * 60)
    print("Agriculture Knowledge Graph — Demo")
    print("=" * 60)

    # Crop-soil matching
    print("\n--- Crop-Soil Matching ---")
    matcher = CropSoilMatcher(db)
    for crop_id in ["crop_wheat", "crop_soybean", "crop_potato"]:
        matches = matcher.match_all_soils(crop_id)
        crop = db.get_crop(crop_id)
        print(f"\n{crop['name']} ({crop['family']}):")
        for m in sorted(matches, key=lambda x: x["suitability_score"], reverse=True):
            soil = db.get_soil(m["soil_id"])
            print(
                f"  {m['soil_id']}: score={m['suitability_score']:.3f} "
                f"(lat={soil['latitude']}, lon={soil['longitude']})"
            )

    # Pest identification
    print("\n--- Pest/Disease Identification ---")
    identifier = PestDiseaseIdentifier(db)
    for crop_name in ["Wheat", "Soybean", "Potato"]:
        pests = identifier.identify(crop_name)
        print(f"\n{crop_name}:")
        for p in pests:
            print(f"  {p['name']} ({p['type']})")
            print(f"    Symptoms: {', '.join(p['symptoms'][:2])}")
            print(f"    Treatments: {', '.join(p['treatments'][:2])}")

    # Seasonal reasoning
    print("\n--- Seasonal Pattern Reasoning ---")
    reasoner = SeasonalReasoner(db)
    for crop_id in ["crop_wheat", "crop_soybean", "crop_potato"]:
        patterns = reasoner.get_planting_window(crop_id)
        crop = db.get_crop(crop_id)
        for p in patterns:
            print(
                f"  {crop['name']} ({p['region']}): "
                f"plant months={p['planting_months']}, "
                f"harvest months={p['harvest_months']}"
            )

    # Weather mapping
    print("\n--- Weather Interaction Mapping ---")
    mapper = WeatherMapper(db)
    test_conditions = [
        ("crop_wheat", 18.0, 600.0),
        ("crop_soybean", 25.0, 700.0),
        ("crop_potato", 18.0, 600.0),
    ]
    for crop_id, temp, rain in test_conditions:
        result = mapper.is_suitable_weather(crop_id, temp, rain)
        crop = db.get_crop(crop_id)
        status = "SUITABLE" if result["suitable"] else "UNSUITABLE"
        print(f"  {crop['name']} at {temp}°C, {rain}mm: {status}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agriculture KG CLI")
    parser.add_argument(
        "--db-path",
        default="agriculture_kg.db",
        help="Path to SQLite database (default: agriculture_kg.db)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("seed", help="Seed database with sample data")
    sub.add_parser("demo", help="Run demonstration")

    args = parser.parse_args()
    {"seed": cmd_seed, "demo": cmd_demo}[args.command](args)


if __name__ == "__main__":
    main()
