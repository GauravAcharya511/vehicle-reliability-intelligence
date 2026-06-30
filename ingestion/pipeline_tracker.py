"""
Pipeline run tracking for observability and SLA monitoring.

Why this exists:
- Every production data pipeline needs an audit trail
- Lets you answer: did yesterday's job run? How long? Did it fail?
- Powers dashboards that show pipeline health over time
- Industry standard in Airflow, Prefect, Dagster - we replicate the pattern here
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.logger import get_logger

logger = get_logger(__name__)


class PipelineRunTracker:
    """Tracks pipeline execution lifecycle in the bronze.pipeline_runs table."""

    def __init__(self, engine: Engine, pipeline_name: str):
        self.engine = engine
        self.pipeline_name = pipeline_name
        self.run_id: Optional[int] = None
        self.records_processed: int = 0
        self.records_failed: int = 0

    def start(self) -> int:
        """Insert a STARTED row and return the run_id."""
        with self.engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO bronze.pipeline_runs
                        (pipeline_name, status, started_at)
                    VALUES
                        (:pipeline_name, 'STARTED', :started_at)
                    RETURNING run_id
                """),
                {
                    "pipeline_name": self.pipeline_name,
                    "started_at": datetime.utcnow(),
                },
            )
            self.run_id = result.scalar()
        logger.info(f"Pipeline run started: id={self.run_id} name={self.pipeline_name}")
        return self.run_id

    def succeed(self, records_processed: int) -> None:
        """Mark the run as SUCCESS with final counts."""
        self._finalize(status="SUCCESS", records_processed=records_processed)

    def fail(self, error_message: str, records_processed: int = 0) -> None:
        """Mark the run as FAILED with an error message."""
        self._finalize(
            status="FAILED",
            records_processed=records_processed,
            error_message=error_message,
        )

    def _finalize(
        self,
        status: str,
        records_processed: int,
        error_message: Optional[str] = None,
    ) -> None:
        if self.run_id is None:
            logger.warning("Cannot finalize: pipeline run was never started")
            return

        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE bronze.pipeline_runs
                    SET status = :status,
                        completed_at = :completed_at,
                        records_processed = :records_processed,
                        records_failed = :records_failed,
                        error_message = :error_message
                    WHERE run_id = :run_id
                """),
                {
                    "status": status,
                    "completed_at": datetime.utcnow(),
                    "records_processed": records_processed,
                    "records_failed": self.records_failed,
                    "error_message": error_message,
                    "run_id": self.run_id,
                },
            )
        logger.info(
            f"Pipeline run finalized: id={self.run_id} status={status} "
            f"processed={records_processed} failed={self.records_failed}"
        )


@contextmanager
def track_pipeline_run(engine: Engine, pipeline_name: str):
    """
    Context manager that auto-tracks pipeline lifecycle.

    Usage:
        with track_pipeline_run(engine, "my_pipeline") as tracker:
            # do work
            tracker.records_processed = 1000

    Automatically marks SUCCESS on clean exit, FAILED on exception.
    """
    tracker = PipelineRunTracker(engine, pipeline_name)
    tracker.start()
    try:
        yield tracker
        tracker.succeed(records_processed=tracker.records_processed)
    except Exception as exc:
        tracker.fail(error_message=str(exc), records_processed=tracker.records_processed)
        raise
