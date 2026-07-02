"""
Prophet-based failure rate forecasting per component.

Forecasts daily failure counts 30/60/90 days into the future using
Facebook's Prophet model. Captures confidence intervals for each
forecast horizon and flags components with projected upward trends.
"""
import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd
from prophet import Prophet
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.database import get_engine
from utils.logger import get_logger

logger = get_logger(__name__)

# Silence Prophet's chatty output
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


FORECAST_HORIZONS = [30, 60, 90]


def load_component_time_series(engine, component: str) -> pd.DataFrame:
    query = """
        SELECT
            repair_date AS ds,
            COUNT(*) AS y
        FROM silver.stg_repair_records
        WHERE component = %(component)s
        GROUP BY repair_date
        ORDER BY repair_date
    """
    df = pd.read_sql(query, engine, params={"component": component})
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def forecast_component(df: pd.DataFrame, component: str, max_horizon: int = 90) -> pd.DataFrame:
    if len(df) < 30:
        logger.warning(f"Skipping {component} — insufficient history ({len(df)} days)")
        return None

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.80,
    )

    model.fit(df)

    future = model.make_future_dataframe(periods=max_horizon)
    forecast = model.predict(future)

    forecast_only = forecast.tail(max_horizon)[
        ["ds", "yhat", "yhat_lower", "yhat_upper", "trend"]
    ].copy()
    forecast_only["component"] = component
    forecast_only["yhat"] = forecast_only["yhat"].clip(lower=0).round(2)
    forecast_only["yhat_lower"] = forecast_only["yhat_lower"].clip(lower=0).round(2)
    forecast_only["yhat_upper"] = forecast_only["yhat_upper"].clip(lower=0).round(2)
    forecast_only["trend"] = forecast_only["trend"].round(2)

    forecast_only["horizon_days"] = range(1, len(forecast_only) + 1)
    forecast_only["horizon_bucket"] = forecast_only["horizon_days"].apply(
        lambda d: "30d" if d <= 30 else ("60d" if d <= 60 else "90d")
    )

    return forecast_only[[
        "component", "ds", "horizon_days", "horizon_bucket",
        "yhat", "yhat_lower", "yhat_upper", "trend"
    ]]


def summarize_forecast(forecast: pd.DataFrame, historical_avg: float) -> dict:
    horizon_30 = forecast[forecast["horizon_bucket"] == "30d"]
    horizon_60 = forecast[forecast["horizon_bucket"] == "60d"]
    horizon_90 = forecast[forecast["horizon_bucket"] == "90d"]

    return {
        "component": forecast["component"].iloc[0],
        "historical_daily_avg": round(historical_avg, 2),
        "forecast_30d_avg": round(horizon_30["yhat"].mean(), 2),
        "forecast_60d_avg": round(horizon_60["yhat"].mean(), 2),
        "forecast_90d_avg": round(horizon_90["yhat"].mean(), 2),
        "forecast_30d_total": round(horizon_30["yhat"].sum(), 0),
        "forecast_60d_total": round(horizon_60["yhat"].sum(), 0),
        "forecast_90d_total": round(horizon_90["yhat"].sum(), 0),
        "trend_direction": "upward" if forecast["trend"].iloc[-1] > forecast["trend"].iloc[0] else "downward",
        "risk_flag": "high" if horizon_30["yhat"].mean() > historical_avg * 1.2 else "normal",
    }


def run_forecasts(engine, components: List[str]) -> tuple:
    all_forecasts = []
    all_summaries = []

    for component in components:
        logger.info(f"Forecasting failure rate for: {component}")
        df = load_component_time_series(engine, component)

        if df.empty:
            logger.warning(f"No data for {component}")
            continue

        historical_avg = df["y"].mean()
        forecast = forecast_component(df, component)

        if forecast is None:
            continue

        all_forecasts.append(forecast)
        all_summaries.append(summarize_forecast(forecast, historical_avg))

    forecast_df = pd.concat(all_forecasts, ignore_index=True) if all_forecasts else pd.DataFrame()
    summary_df = pd.DataFrame(all_summaries)

    return forecast_df, summary_df


def write_to_gold(forecast_df: pd.DataFrame, summary_df: pd.DataFrame, engine):
    logger.info(f"Writing {len(forecast_df)} forecast rows to gold.fct_component_failure_forecast")
    forecast_df.to_sql(
        name="fct_component_failure_forecast",
        schema="gold",
        con=engine,
        if_exists="replace",
        index=False,
    )

    logger.info(f"Writing {len(summary_df)} summary rows to gold.fct_component_forecast_summary")
    summary_df.to_sql(
        name="fct_component_forecast_summary",
        schema="gold",
        con=engine,
        if_exists="replace",
        index=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Prophet forecasting for component failure rates")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to gold")
    args = parser.parse_args()

    engine = get_engine()

    components_df = pd.read_sql(
        "SELECT DISTINCT component FROM silver.stg_repair_records ORDER BY component",
        engine
    )
    components = components_df["component"].tolist()

    logger.info(f"Forecasting for {len(components)} components")

    forecast_df, summary_df = run_forecasts(engine, components)

    print("\nForecast summary per component (90-day horizon):")
    print(summary_df.to_string(index=False))

    if not args.dry_run:
        write_to_gold(forecast_df, summary_df, engine)
    else:
        logger.info("Dry run - skipping write")


if __name__ == "__main__":
    main()
