"""
Bronze layer ingestion pipeline.

Why this exists:
- Loads raw repair records from CSV into bronze.repair_records_raw
- Handles idempotency via record_hash deduplication
- Uses transactions for atomic batch loads
- Tracks pipeline execution in bronze.pipeline_runs

Usage:
    python -m ingestion.ingest --input data_generator/output/repair_records.csv --batch-size 1000
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.database import get_engine
from ingestion.pipeline_tracker import track_pipeline_run
from utils.logger import get_logger

logger = get_logger(__name__)

PIPELINE_NAME = "bronze_repair_records_ingestion"


def get_existing_hashes(engine) -> set:
    """
    Fetch existing record hashes from bronze for idempotent ingestion.

    Why this matters:
    - Prevents duplicate ingestion on pipeline re-runs
    - Far cheaper than enforcing uniqueness at the DB level for billions of rows
    - Industry pattern: hash-based deduplication in bronze layer
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT record_hash FROM bronze.repair_records_raw WHERE record_hash IS NOT NULL")
        )
        return {row[0] for row in result}


def ingest_batch(df_batch: pd.DataFrame, engine) -> int:
    """
    Ingest a single batch within a transaction.

    Args:
        df_batch: DataFrame chunk to load
        engine: SQLAlchemy engine

    Returns:
        Number of records inserted
    """
    df_batch.to_sql(
        name="repair_records_raw",
        schema="bronze",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
    )
    return len(df_batch)


def ingest(input_path: str, batch_size: int = 1000) -> None:
    """
    Main ingestion entrypoint with full observability.

    Args:
        input_path: Path to CSV file to ingest
        batch_size: Rows per transaction (controls memory + transaction size)
    """
    engine = get_engine()
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info(f"Reading source data from {input_path}")
    df = pd.read_csv(input_file, parse_dates=["repair_date"])
    logger.info(f"Loaded {len(df)} rows from CSV")

    with track_pipeline_run(engine, PIPELINE_NAME) as tracker:
        existing_hashes = get_existing_hashes(engine)
        logger.info(f"Found {len(existing_hashes)} existing records in bronze")

        df_new = df[~df["record_hash"].isin(existing_hashes)]
        skipped = len(df) - len(df_new)

        if skipped > 0:
            logger.info(f"Skipping {skipped} records already in bronze (idempotency)")

        if df_new.empty:
            logger.info("No new records to ingest")
            tracker.records_processed = 0
            return

        logger.info(f"Ingesting {len(df_new)} new records in batches of {batch_size}")

        total_inserted = 0
        for batch_start in range(0, len(df_new), batch_size):
            batch_end = min(batch_start + batch_size, len(df_new))
            df_batch = df_new.iloc[batch_start:batch_end]

            try:
                inserted = ingest_batch(df_batch, engine)
                total_inserted += inserted
                logger.info(
                    f"Batch {batch_start // batch_size + 1}: "
                    f"inserted {inserted} rows (cumulative: {total_inserted})"
                )
            except Exception as exc:
                tracker.records_failed += len(df_batch)
                logger.error(f"Batch failed: {exc}")
                raise

        tracker.records_processed = total_inserted
        logger.info(f"Ingestion complete: {total_inserted} records inserted")


def main():
    parser = argparse.ArgumentParser(description="Ingest repair records into bronze layer")
    parser.add_argument(
        "--input",
        type=str,
        default="data_generator/output/repair_records.csv",
        help="Path to input CSV file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of rows per transaction batch",
    )
    args = parser.parse_args()

    ingest(input_path=args.input, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
