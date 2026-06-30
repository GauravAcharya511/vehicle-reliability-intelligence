"""
Rolling failure rate analysis: tracks how failure counts evolve over time.

Computes 30/60/90-day rolling windows per component, surfacing emerging
trends (sudden spikes) and seasonal patterns. This is the metric that
catches "Drive Unit failures jumped 40% in the last 30 days" before
it becomes a fleet-wide problem.
"""
import argparse
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from analytics.spark_session import get_spark, get_jdbc_props
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_rolling_rates(spark):
    jdbc = get_jdbc_props()

    df = spark.read.jdbc(
        url=jdbc["url"],
        table="silver.stg_repair_records",
        properties=jdbc["properties"],
    )

    # Aggregate to daily counts per component
    daily = (
        df.groupBy("component", "repair_date")
        .agg(
            F.count("*").alias("daily_failures"),
            F.sum("repair_cost_usd").alias("daily_cost_usd"),
        )
    )

    # Rolling windows in days - approximated using row-based windows
    # since data has daily granularity per component
    window_30 = Window.partitionBy("component").orderBy("repair_date").rowsBetween(-29, 0)
    window_60 = Window.partitionBy("component").orderBy("repair_date").rowsBetween(-59, 0)
    window_90 = Window.partitionBy("component").orderBy("repair_date").rowsBetween(-89, 0)

    rolling = (
        daily
        .withColumn("rolling_30d_failures", F.sum("daily_failures").over(window_30))
        .withColumn("rolling_60d_failures", F.sum("daily_failures").over(window_60))
        .withColumn("rolling_90d_failures", F.sum("daily_failures").over(window_90))
        .withColumn("rolling_30d_cost_usd", F.round(F.sum("daily_cost_usd").over(window_30), 2))
        .withColumn("rolling_60d_cost_usd", F.round(F.sum("daily_cost_usd").over(window_60), 2))
        .withColumn("rolling_90d_cost_usd", F.round(F.sum("daily_cost_usd").over(window_90), 2))
    )

    # Trend indicator: is 30d rate accelerating vs 90d baseline?
    rolling = rolling.withColumn(
        "trend_30d_vs_90d_ratio",
        F.round(
            F.col("rolling_30d_failures") /
            (F.col("rolling_90d_failures") / 3.0),
            3
        )
    )

    return rolling


def write_to_gold(df, jdbc, table_name):
    logger.info(f"Writing rolling failure rates to gold.{table_name}")
    (
        df.write.jdbc(
            url=jdbc["url"],
            table=f"gold.{table_name}",
            mode="overwrite",
            properties=jdbc["properties"],
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    spark = get_spark("failure_rate_rolling")
    jdbc = get_jdbc_props()

    try:
        rolling_df = compute_rolling_rates(spark)

        logger.info("Recent rolling failure rates with trend indicator:")
        rolling_df.orderBy(F.desc("repair_date")).show(15, truncate=False)

        if not args.dry_run:
            write_to_gold(rolling_df, jdbc, "fct_failure_rate_rolling")
        else:
            logger.info("Dry run - skipping write")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
