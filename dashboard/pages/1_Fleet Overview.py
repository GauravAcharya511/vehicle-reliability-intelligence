import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dashboard.styles import apply_theme, render_metric, render_page_header, render_section, render_freshness_indicator, get_plotly_theme
from dashboard.sidebar import render_sidebar
from dashboard.data import (
    load_fleet_overview,
    load_top_reliability_concerns,
    load_component_distribution,
    load_regional_health,
    load_last_pipeline_run,
)

st.set_page_config(page_title="Fleet Overview", layout="wide")
apply_theme()
filters = render_sidebar()

render_page_header(
    "Fleet Health Overview",
    "Aggregate reliability metrics across the vehicle fleet, ranked component concerns, and regional health summary."
)

render_freshness_indicator(load_last_pipeline_run())

overview = load_fleet_overview(
    region_filter=filters.get("regions"),
    model_filter=filters.get("models"),
    date_range=filters.get("date_range"),
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric("Total repairs", f"{int(overview['total_repairs']):,}")
with col2:
    render_metric("Vehicles affected", f"{int(overview['unique_vehicles']):,}")
with col3:
    render_metric("Total cost", f"${overview['total_cost']:,.0f}")
with col4:
    render_metric("Avg per repair", f"${overview['avg_cost']:,.0f}")
with col5:
    render_metric("Warranty rate", f"{overview['warranty_rate']}%")

render_section("Top reliability concerns · lowest MTTF")

mttf_df = load_top_reliability_concerns()
st.dataframe(
    mttf_df.rename(columns={
        "component": "Component",
        "vehicle_model": "Model",
        "mttf_miles": "MTTF (mi)",
        "failure_count": "Failures",
        "unique_vehicles_affected": "Vehicles",
        "avg_repair_cost_usd": "Avg cost ($)",
    }),
    use_container_width=True,
    hide_index=True,
    height=430,
)

col_left, col_right = st.columns([1.2, 1])

with col_left:
    render_section("Failure distribution by component")
    dist_df = load_component_distribution()

    theme = get_plotly_theme()
    fig = go.Figure(go.Treemap(
        labels=dist_df["component"],
        parents=[""] * len(dist_df),
        values=dist_df["failure_count"],
        textinfo="label+value",
        marker=dict(
            colors=dist_df["failure_count"],
            colorscale=[[0, "#2a2a3e"], [0.5, "#8b3140"], [1, "#E63946"]],
            showscale=False,
        ),
        textfont=dict(color="white", size=13),
    ))
    fig.update_layout(
        template=theme["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    render_section("Regional health summary")
    regional_df = load_regional_health()

    st.dataframe(
        regional_df.rename(columns={
            "region": "Region",
            "continent": "Continent",
            "total_repairs": "Repairs",
            "unique_vehicles": "Vehicles",
            "avg_cost": "Avg cost ($)",
            "warranty_claims": "Warranty",
        }),
        use_container_width=True,
        hide_index=True,
        height=380,
    )
