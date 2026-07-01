"""
Zero-shot NLP classifier for repair descriptions.

Uses BART-MNLI to categorize unstructured repair text into structured
failure categories, severity levels, and root cause types. No fine-tuning
needed - the model's pre-trained NLI knowledge handles it.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Dict

import pandas as pd
from sqlalchemy import text
from transformers import pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.database import get_engine
from nlp.taxonomy import (
    FAILURE_CATEGORIES,
    SEVERITY_LEVELS,
    ROOT_CAUSE_TYPES,
    ZERO_SHOT_MODEL,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def get_classifier():
    logger.info(f"Loading zero-shot classifier: {ZERO_SHOT_MODEL}")
    logger.info("First run will download ~1.6GB model - subsequent runs use cache")
    return pipeline(
        "zero-shot-classification",
        model=ZERO_SHOT_MODEL,
        device=-1,  # CPU
    )


def classify_batch(classifier, texts: List[str], labels: List[str]) -> List[Dict]:
    results = classifier(texts, candidate_labels=labels, multi_label=False)
    if isinstance(results, dict):
        results = [results]
    return [
        {"label": r["labels"][0], "score": round(r["scores"][0], 4)}
        for r in results
    ]


def enrich_repair_records(engine, classifier, sample_size: int = None) -> pd.DataFrame:
    query = """
        SELECT
            record_id,
            component,
            repair_description,
            mileage,
            repair_cost_usd,
            region
        FROM silver.stg_repair_records
    """
    if sample_size:
        query += f" LIMIT {sample_size}"

    logger.info(f"Reading repair records from silver layer")
    df = pd.read_sql(query, engine)
    logger.info(f"Loaded {len(df)} records for NLP enrichment")

    descriptions = df["repair_description"].tolist()

    logger.info("Stage 1: Classifying failure categories...")
    category_results = classify_batch(classifier, descriptions, FAILURE_CATEGORIES)
    df["nlp_failure_category"] = [r["label"] for r in category_results]
    df["nlp_failure_category_confidence"] = [r["score"] for r in category_results]

    logger.info("Stage 2: Classifying severity levels...")
    severity_results = classify_batch(classifier, descriptions, SEVERITY_LEVELS)
    df["nlp_severity"] = [r["label"] for r in severity_results]
    df["nlp_severity_confidence"] = [r["score"] for r in severity_results]

    logger.info("Stage 3: Classifying root cause types...")
    cause_results = classify_batch(classifier, descriptions, ROOT_CAUSE_TYPES)
    df["nlp_root_cause"] = [r["label"] for r in cause_results]
    df["nlp_root_cause_confidence"] = [r["score"] for r in cause_results]

    return df


def write_to_gold(df: pd.DataFrame, engine):
    logger.info("Writing NLP-enriched data to gold.fct_repair_nlp_enriched")
    df.to_sql(
        name="fct_repair_nlp_enriched",
        schema="gold",
        con=engine,
        if_exists="replace",
        index=False,
    )
    logger.info(f"Wrote {len(df)} enriched records to gold")


def main():
    parser = argparse.ArgumentParser(description="NLP enrichment for repair records")
    parser.add_argument(
        "--sample",
        type=int,
        default=200,
        help="Sample size (use small for testing, 0 for full dataset)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't write to gold")
    args = parser.parse_args()

    engine = get_engine()
    classifier = get_classifier()

    sample = args.sample if args.sample > 0 else None
    enriched_df = enrich_repair_records(engine, classifier, sample_size=sample)

    logger.info("Sample of enriched records:")
    print(enriched_df[[
        "component",
        "repair_description",
        "nlp_failure_category",
        "nlp_severity",
        "nlp_root_cause"
    ]].head(10).to_string())

    if not args.dry_run:
        write_to_gold(enriched_df, engine)
    else:
        logger.info("Dry run - skipping write")


if __name__ == "__main__":
    main()
