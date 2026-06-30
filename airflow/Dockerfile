FROM apache/airflow:2.9.0-python3.10

USER airflow

RUN pip install --no-cache-dir \
    dbt-core==1.7.9 \
    dbt-postgres==1.7.9 \
    astronomer-cosmos==1.4.0 \
    psycopg2-binary==2.9.9
