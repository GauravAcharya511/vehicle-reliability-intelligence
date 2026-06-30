import os
from pyspark.sql import SparkSession
from dotenv import load_dotenv

load_dotenv(override=False)

POSTGRES_JAR = "org.postgresql:postgresql:42.7.3"


def get_spark(app_name: str = "vehicle_reliability_analytics") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", POSTGRES_JAR)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def get_jdbc_props():
    return {
        "url": (
            f"jdbc:postgresql://{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'vehicle_reliability')}"
        ),
        "properties": {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD", ""),
            "driver": "org.postgresql.Driver",
        }
    }
