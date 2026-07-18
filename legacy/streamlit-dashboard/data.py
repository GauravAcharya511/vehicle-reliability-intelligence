import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.database import get_engine


@st.cache_resource
def get_db_engine():
    return get_engine()


@st.cache_data(ttl=300)
def load_last_pipeline_run() -> str:
    engine = get_db_engine()
    df = pd.read_sql(
        "SELECT MAX(completed_at) as last_run FROM bronze.pipeline_runs WHERE status = 'SUCCESS'",
        engine
    )
    if df.empty or pd.isna(df["last_run"].iloc[0]):
        return "No successful runs yet"
    return df["last_run"].iloc[0].strftime("%Y-%m-%d %H:%M UTC")


@st.cache_data(ttl=300)
def load_fleet_overview(region_filter=None, model_filter=None, date_range=None) -> dict:
    engine = get_db_engine()

    where_clauses = ["1=1"]
    params = {}

    if region_filter and len(region_filter) > 0:
        where_clauses.append("region = ANY(%(regions)s)")
        params["regions"] = region_filter

    if model_filter and len(model_filter) > 0:
        where_clauses.append("vehicle_model = ANY(%(models)s)")
        params["models"] = model_filter

    if date_range:
        where_clauses.append("repair_date BETWEEN %(start_date)s AND %(end_date)s")
        params["start_date"] = date_range[0]
        params["end_date"] = date_range[1]

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT
            COUNT(*) as total_repairs,
            COUNT(DISTINCT vin) as unique_vehicles,
            SUM(repair_cost_usd) as total_cost,
            AVG(repair_cost_usd) as avg_cost,
            SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) as warranty_claims,
            ROUND(100.0 * SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) as warranty_rate
        FROM silver.stg_repair_records
        WHERE {where_sql}
    """
    df = pd.read_sql(query, engine, params=params)
    return df.iloc[0].to_dict()


@st.cache_data(ttl=300)
def load_top_reliability_concerns() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            component,
            vehicle_model,
            mttf_miles,
            failure_count,
            unique_vehicles_affected,
            avg_repair_cost_usd
        FROM gold.fct_component_mttf
        ORDER BY mttf_miles ASC
        LIMIT 15
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_component_distribution() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            component,
            COUNT(*) as failure_count,
            SUM(repair_cost_usd) as total_cost
        FROM silver.stg_repair_records
        GROUP BY component
        ORDER BY failure_count DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_regional_health() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            region,
            continent,
            COUNT(*) as total_repairs,
            COUNT(DISTINCT vin) as unique_vehicles,
            ROUND(AVG(repair_cost_usd)::numeric, 2) as avg_cost,
            SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) as warranty_claims
        FROM silver.stg_repair_records
        GROUP BY region, continent
        ORDER BY total_repairs DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_rolling_failure_rates(components: list) -> pd.DataFrame:
    engine = get_db_engine()
    if not components:
        return pd.DataFrame()
    query = """
        SELECT
            component,
            repair_date,
            daily_failures,
            rolling_30d_failures,
            rolling_60d_failures,
            rolling_90d_failures,
            trend_30d_vs_90d_ratio
        FROM gold.fct_failure_rate_rolling
        WHERE component = ANY(%(components)s)
        ORDER BY repair_date
    """
    return pd.read_sql(query, engine, params={"components": components})


@st.cache_data(ttl=300)
def load_regional_hotspots() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            component,
            region,
            repair_quarter,
            regional_failure_count,
            regional_vs_baseline_ratio,
            is_hotspot
        FROM gold.fct_failure_clusters
        ORDER BY regional_vs_baseline_ratio DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_nlp_severity_distribution() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            nlp_severity,
            COUNT(*) as count
        FROM gold.fct_repair_nlp_enriched
        GROUP BY nlp_severity
        ORDER BY count DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_nlp_category_distribution() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            nlp_failure_category,
            COUNT(*) as count,
            ROUND(AVG(nlp_failure_category_confidence)::numeric, 3) as avg_confidence
        FROM gold.fct_repair_nlp_enriched
        GROUP BY nlp_failure_category
        ORDER BY count DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_critical_by_component() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            component,
            COUNT(*) as critical_count,
            ROUND(AVG(repair_cost_usd)::numeric, 2) as avg_cost,
            ROUND(SUM(repair_cost_usd)::numeric, 2) as total_cost
        FROM gold.fct_repair_nlp_enriched
        WHERE nlp_severity = 'critical safety issue'
        GROUP BY component
        ORDER BY critical_count DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_severity_component_matrix() -> pd.DataFrame:
    engine = get_db_engine()
    query = """
        SELECT
            component,
            nlp_severity,
            COUNT(*) as count
        FROM gold.fct_repair_nlp_enriched
        GROUP BY component, nlp_severity
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_forecast_summary() -> pd.DataFrame:
    engine = get_db_engine()
    query = "SELECT * FROM gold.fct_component_forecast_summary ORDER BY forecast_90d_avg DESC"
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def load_component_forecast(component: str) -> tuple:
    engine = get_db_engine()

    forecast_query = """
        SELECT ds, yhat, yhat_lower, yhat_upper, horizon_bucket
        FROM gold.fct_component_failure_forecast
        WHERE component = %(component)s
        ORDER BY ds
    """
    forecast_df = pd.read_sql(forecast_query, engine, params={"component": component})

    historical_query = """
        SELECT repair_date as ds, COUNT(*) as y
        FROM silver.stg_repair_records
        WHERE component = %(component)s
        GROUP BY repair_date
        ORDER BY repair_date
    """
    historical_df = pd.read_sql(historical_query, engine, params={"component": component})

    return historical_df, forecast_df


@st.cache_data(ttl=300)
def get_filter_options() -> dict:
    engine = get_db_engine()
    regions = pd.read_sql("SELECT DISTINCT region FROM silver.stg_repair_records ORDER BY region", engine)["region"].tolist()
    models = pd.read_sql("SELECT DISTINCT vehicle_model FROM silver.stg_repair_records ORDER BY vehicle_model", engine)["vehicle_model"].tolist()
    components = pd.read_sql("SELECT DISTINCT component FROM silver.stg_repair_records ORDER BY component", engine)["component"].tolist()
    date_range = pd.read_sql("SELECT MIN(repair_date) as min_date, MAX(repair_date) as max_date FROM silver.stg_repair_records", engine)

    return {
        "regions": regions,
        "models": models,
        "components": components,
        "min_date": date_range["min_date"].iloc[0],
        "max_date": date_range["max_date"].iloc[0],
    }
