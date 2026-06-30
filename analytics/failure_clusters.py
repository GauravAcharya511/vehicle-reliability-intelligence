"""
Regional + temporal failure clustering.

Identifies geographic hotspots where failure rates deviate from the
global baseline. Surfaces patterns like "EMEA-East is showing 2.3x the
baseline for Drive Unit failures this quarter."
"""
import argparse
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from analytics.spark_session import get_spark, get_jdbc_props
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_clusters(spark):
    jdbc = get_jdbc_props()

    df = spark.read.jdbc(
        url=jdbc["url"],
        table="silver.stg_repair_records",
        properties=jdbc["properties"],
    )

    # Failures per component per region per quarter
    regional = (
        df.groupBy("component", "region", "continent", "repair_quarter")
        .agg(
            F.count("*").alias("regional_failure_count"),
            F.countDistinct("vin").alias("regional_vehicles_affected"),
            F.avg("repair_cost_usd").alias("regional_avg_cost"),
            F.sum("repair_cost_usd").alias("regional_total_cost"),
        )
    )

    # Global baseline per component per quarter (across all regions)
    global_baseline = (
        df.groupBy("component", "repair_quarter")
        .agg(
            F.count("*").alias("global_failure_count"),
            F.countDistinct("region").alias("region_count"),
        )
        .withColumn(
            "global_avg_per_region",
            F.col("global_failure_count") / F.col("region_count")
        )
    )

    # Join and compute deviation from baseline
    clustered = (
        regional
        .join(global_baseline, on=["component", "repair_quarter"])
        .withColumn(
            "regional_vs_baseline_ratio",
            F.round(
                F.col("regional_failure_count") / F.col("global_avg_per_region"),
                3
            )
        )
        .withColumn(
            "is_hotspot",
            F.when(F.col("regional_vs_baseline_ratio") >= 1.5, F.lit(True))
            .otherwise(F.lit(False))
        )
        .withColumn("regional_avg_cost", F.round("regional_avg_cost", 2))
        .withColumn("regional_total_cost", F.round("regional_total_cost", 2))
        .withColumn("global_avg_per_region", F.round("global_avg_per_region", 2))
    )

    return clustered


def write_to_gold(df, jdbc, table_name):
    logger.info(f"Writing failure clusters to gold.{table_name}")
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

    spark = get_spark("failure_clusters")
    jdbc = get_jdbc_props()

    try:
        clusters_df = compute_clusters(spark)

        logger.info("Top regional hotspots (ratio >= 1.5):")
        (
            clusters_df
            .filter(F.col("is_hotspot") == True)
            .orderBy(F.desc("regional_vs_baseline_ratio"))
            .show(15, truncate=False)
        )

        if not args.dry_run:
            write_to_gold(clusters_df, jdbc, "fct_failure_clusters")
        else:
            logger.info("Dry run - skipping write")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
