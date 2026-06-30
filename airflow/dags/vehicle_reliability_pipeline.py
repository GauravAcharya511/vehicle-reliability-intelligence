"""
Vehicle Reliability Pipeline - End-to-end orchestration DAG

This DAG runs the complete medallion flow daily:
    generate_data -> ingest_bronze -> dbt_run -> dbt_test -> notify

Why this exists:
- Replaces manual script execution with automated, scheduled, observable runs
- Handles retries, failure alerts, and task dependencies automatically
- Demonstrates production-grade Airflow + dbt orchestration via Cosmos
"""
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default args applied to every task unless overridden
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["gauravacharya511@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}

PROJECT_ROOT = "/opt/airflow/project"


def task_success_callback(context):
    """Callback fired when a task succeeds. Useful for metrics."""
    task = context["task_instance"]
    print(
        f"Task succeeded: dag={task.dag_id} task={task.task_id} "
        f"run={task.run_id} duration={task.duration}s"
    )


with DAG(
    dag_id="vehicle_reliability_pipeline",
    description="End-to-end vehicle reliability data pipeline (medallion architecture)",
    default_args=default_args,
    start_date=datetime(2026, 6, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["vehicle-reliability", "medallion", "production"],
    doc_md=__doc__,
) as dag:

    generate_data = BashOperator(
        task_id="generate_repair_data",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"python -m data_generator.generate_records --rows 10000 --seed 42"
        ),
        on_success_callback=task_success_callback,
        doc_md="Generates 10,000 synthetic repair records into CSV",
    )

    ingest_bronze = BashOperator(
        task_id="ingest_to_bronze",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"python -m ingestion.ingest "
            f"--input data_generator/output/repair_records.csv "
            f"--batch-size 1000"
        ),
        on_success_callback=task_success_callback,
        doc_md="Idempotent ingestion into bronze.repair_records_raw",
    )

    dbt_run = BashOperator(
        task_id="dbt_run_silver_gold",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_project && "
            f"dbt run --profiles-dir /opt/airflow/dbt_profiles"
        ),
        on_success_callback=task_success_callback,
        doc_md="Builds silver staging + gold fact tables",
    )

    dbt_test = BashOperator(
        task_id="dbt_test_quality",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_project && "
            f"dbt test --profiles-dir /opt/airflow/dbt_profiles"
        ),
        on_success_callback=task_success_callback,
        doc_md="Runs all dbt data quality tests",
    )

    spark_mttf = BashOperator(
        task_id="spark_mttf_analysis",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"python -m analytics.mttf_analysis"
        ),
        on_success_callback=task_success_callback,
        doc_md="PySpark MTTF computation per component and model",
    )

    spark_rolling = BashOperator(
        task_id="spark_failure_rate_rolling",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"python -m analytics.failure_rate_rolling"
        ),
        on_success_callback=task_success_callback,
        doc_md="PySpark 30/60/90-day rolling failure rates",
    )

    spark_clusters = BashOperator(
        task_id="spark_failure_clusters",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"python -m analytics.failure_clusters"
        ),
        on_success_callback=task_success_callback,
        doc_md="PySpark regional + temporal failure clustering",
    )

    notify_success = BashOperator(
        task_id="notify_pipeline_success",
        bash_command='echo "Pipeline completed successfully at $(date)"',
        doc_md="Final success marker for SLA tracking",
    )

    generate_data >> ingest_bronze >> dbt_run >> dbt_test
    dbt_test >> [spark_mttf, spark_rolling, spark_clusters] >> notify_success
