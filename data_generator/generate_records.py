"""
Synthetic vehicle repair record generator.

Why this exists:
- Produces realistic, reproducible repair data for the analytics pipeline
- Mirrors real-world fleet data: skewed distributions, free-text descriptions,
  regional variance, warranty claim patterns
- Deterministic (seeded) so test results are reproducible

Usage:
    python -m data_generator.generate_records --rows 10000 --seed 42
"""
import argparse
import hashlib
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_generator.config import (
    VEHICLE_MODELS, MODEL_WEIGHTS, REGIONS, COMPONENTS,
    COMPONENT_FAILURE_WEIGHTS, FAILURE_DESCRIPTIONS,
    REPAIR_COST_RANGES_USD, VEHICLE_YEARS, YEAR_WEIGHTS,
    VIN_CHARSET, WARRANTY_CLAIM_PROBABILITY,
)
from utils.logger import get_logger

logger = get_logger(__name__)


# Injected regional skew: specific components fail disproportionately in specific
# regions, so the clustering job has real geographic signal to detect. Any
# (component, region) pair listed here gets a higher selection weight for that
# region; everything else stays uniform. This is what turns the regional
# clustering output from a flat ~1.0x wall into genuine 2-3x hotspots.
REGIONAL_HOTSPOTS = {
    "Drive Unit": {"EMEA-East": 3.0},
    "Battery Pack": {"NA-West": 3.0},
    "Thermal Management": {"NA-Central": 2.5},
    "Autopilot Sensors": {"EMEA-West": 2.5},
    "Charging Port": {"NA-East": 2.2},
}


def pick_region(component: str) -> str:
    """Weighted region choice: hotspot pairs are over-represented for their
    component, all other (component, region) pairs stay uniform."""
    boosts = REGIONAL_HOTSPOTS.get(component, {})
    weights = [boosts.get(region, 1.0) for region in REGIONS]
    return random.choices(REGIONS, weights=weights)[0]


def generate_vin() -> str:
    """Generate a 17-character VIN-like identifier."""
    return "".join(random.choices(VIN_CHARSET, k=17))


def compute_record_hash(record: Dict) -> str:
    """
    Compute SHA-256 hash of a record for idempotent ingestion.

    Why this matters:
    - Enables deduplication on re-runs
    - Allows change detection without comparing all columns
    - Industry standard for CDC (change data capture) pipelines
    """
    canonical = (
        f"{record['vin']}|{record['repair_date']}|{record['component']}"
        f"|{record['repair_description']}|{record['mileage']}"
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def generate_records(num_rows: int, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic repair records with realistic distributions.

    Args:
        num_rows: Number of records to generate
        seed: Random seed for reproducibility

    Returns:
        DataFrame with repair records ready for ingestion
    """
    random.seed(seed)
    np.random.seed(seed)

    logger.info(f"Generating {num_rows} repair records (seed={seed})")

    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range_days = (end_date - start_date).days

    fleet_size = max(num_rows // 5, 100)
    vin_pool: List[str] = [generate_vin() for _ in range(fleet_size)]
    logger.info(f"Generated VIN pool of {fleet_size} vehicles")

    records = []
    for _ in range(num_rows):
        component = random.choices(COMPONENTS, weights=COMPONENT_FAILURE_WEIGHTS)[0]
        description = random.choice(FAILURE_DESCRIPTIONS[component])
        cost_min, cost_max = REPAIR_COST_RANGES_USD[component]

        repair_date = start_date + timedelta(days=random.randint(0, date_range_days))
        vehicle_year = random.choices(VEHICLE_YEARS, weights=YEAR_WEIGHTS)[0]

        years_in_service = max(1, 2024 - vehicle_year)
        base_mileage = years_in_service * 12000
        mileage = max(100, int(np.random.normal(base_mileage, base_mileage * 0.25)))

        record = {
            "vin": random.choice(vin_pool),
            "repair_date": repair_date.date(),
            "component": component,
            "failure_mode": " ".join(description.split(" ")[:4]),
            "repair_description": description,
            "mileage": mileage,
            "repair_cost_usd": round(random.uniform(cost_min, cost_max), 2),
            "region": pick_region(component),
            "dealer_id": f"DLR-{random.randint(1000, 9999)}",
            "vehicle_model": random.choices(VEHICLE_MODELS, weights=MODEL_WEIGHTS)[0],
            "vehicle_year": vehicle_year,
            "warranty_claim": random.random() < WARRANTY_CLAIM_PROBABILITY,
            "source_system": "simulated_fleet_v1",
        }
        record["record_hash"] = compute_record_hash(record)
        records.append(record)

    df = pd.DataFrame(records)
    logger.info(f"Generated DataFrame with shape {df.shape}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic vehicle repair records")
    parser.add_argument("--rows", type=int, default=10000, help="Number of records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--output",
        type=str,
        default="data_generator/output/repair_records.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    df = generate_records(num_rows=args.rows, seed=args.seed)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Wrote {len(df)} records to {output_path}")

    print("\nSample records:")
    print(df.head(3).to_string())
    print(f"\nDistribution by component:")
    print(df["component"].value_counts().to_string())

    print(f"\nDistribution by region:")
    print(df["region"].value_counts().to_string())

    print(f"\nInjected hotspot pairs (component x region share):")
    for comp, boosts in REGIONAL_HOTSPOTS.items():
        for region in boosts:
            subset = df[df["component"] == comp]
            if len(subset):
                share = (subset["region"] == region).mean()
                print(f"  {comp} in {region}: {share:.1%} of that component's failures")


if __name__ == "__main__":
    main()
