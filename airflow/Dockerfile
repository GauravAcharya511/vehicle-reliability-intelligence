FROM apache/airflow:2.9.0-python3.10

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

RUN pip install --no-cache-dir \
    dbt-core==1.7.9 \
    dbt-postgres==1.7.9 \
    astronomer-cosmos==1.4.0 \
    psycopg2-binary==2.9.9 \
    pyspark==3.5.1
