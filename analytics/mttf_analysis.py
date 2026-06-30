"""
Mean Time To Failure (MTTF) analysis per component and vehicle model.

MTTF is computed as the average mileage at which a given component fails,
grouped by component + vehicle_model. Lower MTTF = component fails earlier
in the vehicle's life = higher reliability concern.
"""
import argparse
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from analytics.spark_session import get_spark, get_jdbc_props
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_mttf(spark):
    jdbc = get_jdbc_props()

    logger.info("Reading silver.stg_repair_records via JDBC")
    df = (
        spark.read.jdbc(
            url=jdbc["url"],
            table="silver.stg_repair_records",
            properties=jdbc["properties"],
        )
    )

    logger.info(f"Loaded {df.count()} silver records")

    # MTTF per component + model
    mttf = (
        df.groupBy("component", "vehicle_model")
        .agg(
            F.avg("mileage").alias("mttf_miles"),
            F.expr("percentile_approx(mileage, 0.5)").alias("median_failure_mileage"),
            F.stddev("mileage").alias("stddev_failure_mileage"),
            F.count("*").alias("failure_count"),
            F.countDistinct("vin").alias("unique_vehicles_affected"),
            F.avg("repair_cost_usd").alias("avg_repair_cost_usd"),
        )
        .withColumn("mttf_miles", F.round("mttf_miles", 0))
        .withColumn("median_failure_mileage", F.round("median_failure_mileage", 0))
        .withColumn("stddev_failure_mileage", F.round("stddev_failure_mileage", 0))
        .withColumn("avg_repair_cost_usd", F.round("avg_repair_cost_usd", 2))
    )

    # Rank components by reliability concern within each model
    window = Window.partitionBy("vehicle_model").orderBy("mttf_miles")
    mttf = mttf.withColumn("reliability_rank_within_model", F.rank().over(window))

    return mttf


def write_to_gold(df, jdbc, table_name):
    logger.info(f"Writing {df.count()} rows to gold.{table_name}")
    (
        df.write.jdbc(
            url=jdbc["url"],
            table=f"gold.{table_name}",
            mode="overwrite",
            properties=jdbc["properties"],
        )
    )
    logger.info(f"Write complete: gold.{table_name}")


def main():
    parser = argparse.ArgumentParser(description="Compute MTTF analytics from silver layer")
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write to gold")
    args = parser.parse_args()

    spark = get_spark("mttf_analysis")
    jdbc = get_jdbc_props()

    try:
        mttf_df = compute_mttf(spark)

        logger.info("Top 10 reliability concerns by component + model:")
        mttf_df.orderBy("mttf_miles").show(10, truncate=False)

        if not args.dry_run:
            write_to_gold(mttf_df, jdbc, "fct_component_mttf")
        else:
            logger.info("Dry run mode - skipping write to gold")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
