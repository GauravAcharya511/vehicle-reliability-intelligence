# Vehicle Field Reliability Intelligence System

An end-to-end data engineering platform that mirrors real-world vehicle fleet reliability operations, ingesting repair records, detecting failure trends, forecasting component failures, and surfacing insights via an interactive dashboard.

## Tech Stack

- Ingestion and Storage: Python, PostgreSQL, SQLAlchemy
- Transformation: dbt (bronze/silver/gold medallion), Great Expectations
- Orchestration: Apache Airflow (DAG-based ETL scheduling)
- Big Data: PySpark (time-series failure rate analysis, MTTF computation)
- NLP: HuggingFace Transformers, LangChain (repair description classification)
- Forecasting: Prophet, LSTM (30/60/90 day failure prediction)
- Visualization: Streamlit, Flask, Plotly, Matplotlib
- Cloud and DevOps: GCP, Docker, GitHub Actions CI/CD

## Status

In Progress - Active development. Days 1-6 being built iteratively.

Phase 1 - Data foundation + PostgreSQL + dbt 
Phase 2 - Airflow + dbt orchestration via Docker 
Phase 3 -  PySpark time-series + MTTF + clustering
Phase 4 - HuggingFace NLP classifier - Upcoming
Phase 5 -Prophet forecasting (30/60/90 day) - COMPLETE
Phase 6 - Streamlit dashboard + GCP deploy - Upcoming

## Setup

Clone the repo, install requirements, copy .env.example to .env and fill in your PostgreSQL credentials, then run python data_generator/generate_records.py followed by python ingestion/ingest.py and cd dbt_project && dbt run.
