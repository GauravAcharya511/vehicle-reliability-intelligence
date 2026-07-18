import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dashboard.styles import apply_theme, render_metric, render_page_header, render_section, render_freshness_indicator, get_plotly_theme
from dashboard.sidebar import render_sidebar
from dashboard.data import (
    load_forecast_summary,
    load_component_forecast,
    load_last_pipeline_run,
    get_filter_options,
)

st.set_page_config(page_title="Predictive Forecasts", layout="wide")
apply_theme()
filters = render_sidebar()

render_page_header(
    "Predictive Reliability Forecasts",
    "Prophet-based failure rate projections with 80% confidence intervals. 30/60/90-day horizons per component."
)

render_freshness_indicator(load_last_pipeline_run())

summary_df = load_forecast_summary()
upward_count = (summary_df["trend_direction"] == "upward").sum()
risk_count = (summary_df["risk_flag"] == "high").sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Components forecasted", f"{len(summary_df)}")
with col2:
    render_metric("Trending upward", f"{upward_count}")
with col3:
    render_metric("High-risk flags", f"{risk_count}")
with col4:
    render_metric("Forecast horizon", "90 days")

render_section("Component forecast · historical + projected")

options = get_filter_options()
selected_component = st.selectbox(
    "Select component to forecast",
    options=options["components"],
    index=0,
)

historical_df, forecast_df = load_component_forecast(selected_component)

if not historical_df.empty and not forecast_df.empty:
    theme = get_plotly_theme()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=historical_df["ds"],
        y=historical_df["y"],
        mode="markers",
        name="Historical",
        marker=dict(color="#b0b0c8", size=5, opacity=0.7, line=dict(color="#E8E8F0", width=0.5)),
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df["ds"].tolist() + forecast_df["ds"].tolist()[::-1],
        y=forecast_df["yhat_upper"].tolist() + forecast_df["yhat_lower"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(230, 57, 70, 0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=True,
        name="80% confidence",
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df["ds"],
        y=forecast_df["yhat"],
        mode="lines",
        name="Forecast",
        line=dict(color="#E63946", width=2.5),
    ))

    fig.update_layout(
        template=theme["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=theme["grid_color"], title=""),
        yaxis=dict(gridcolor=theme["grid_color"], title="Daily failures", rangemode="tozero"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=420,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    render_section("Forecast summary for selected component")

    comp_summary = summary_df[summary_df["component"] == selected_component].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Historical daily avg", f"{comp_summary['historical_daily_avg']:.2f}")
    with col2:
        delta_30 = ((comp_summary["forecast_30d_avg"] - comp_summary["historical_daily_avg"]) / comp_summary["historical_daily_avg"] * 100)
        render_metric("30-day forecast", f"{comp_summary['forecast_30d_avg']:.2f}", delta=f"{delta_30:+.1f}%", delta_direction="up" if delta_30 > 0 else "down")
    with col3:
        delta_60 = ((comp_summary["forecast_60d_avg"] - comp_summary["historical_daily_avg"]) / comp_summary["historical_daily_avg"] * 100)
        render_metric("60-day forecast", f"{comp_summary['forecast_60d_avg']:.2f}", delta=f"{delta_60:+.1f}%", delta_direction="up" if delta_60 > 0 else "down")
    with col4:
        delta_90 = ((comp_summary["forecast_90d_avg"] - comp_summary["historical_daily_avg"]) / comp_summary["historical_daily_avg"] * 100)
        render_metric("90-day forecast", f"{comp_summary['forecast_90d_avg']:.2f}", delta=f"{delta_90:+.1f}%", delta_direction="up" if delta_90 > 0 else "down")

render_section("All components · forecast summary")

def color_risk(val):
    if val == "high":
        return f'<span class="badge badge-critical">High risk</span>'
    return f'<span class="badge badge-normal">Normal</span>'

def color_trend(val):
    if val == "upward":
        return f'<span class="badge badge-high">Upward</span>'
    return f'<span class="badge badge-normal">Downward</span>'

display_df = summary_df.copy()
st.dataframe(
    display_df.rename(columns={
        "component": "Component",
        "historical_daily_avg": "Historical",
        "forecast_30d_avg": "30-day",
        "forecast_60d_avg": "60-day",
        "forecast_90d_avg": "90-day",
        "forecast_30d_total": "30d total",
        "forecast_60d_total": "60d total",
        "forecast_90d_total": "90d total",
        "trend_direction": "Trend",
        "risk_flag": "Risk",
    }),
    use_container_width=True,
    hide_index=True,
    height=380,
)
