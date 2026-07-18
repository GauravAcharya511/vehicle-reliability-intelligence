import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dashboard.styles import apply_theme, render_page_header, render_section, render_freshness_indicator, get_plotly_theme
from dashboard.sidebar import render_sidebar
from dashboard.data import (
    load_rolling_failure_rates,
    load_regional_hotspots,
    load_component_distribution,
    load_last_pipeline_run,
    get_filter_options,
)

st.set_page_config(page_title="Failure Trends", layout="wide")
apply_theme()
filters = render_sidebar()

render_page_header(
    "Failure Trend Analysis",
    "Rolling 30/60/90-day failure rates by component. Regional hotspot detection based on deviation from global baseline."
)

render_freshness_indicator(load_last_pipeline_run())

options = get_filter_options()
top_5_components = load_component_distribution().head(5)["component"].tolist()

render_section("Rolling failure rate trends")

selected_components = st.multiselect(
    "Select components to analyze",
    options=options["components"],
    default=top_5_components[:3],
    placeholder="Choose components",
)

if selected_components:
    rolling_df = load_rolling_failure_rates(selected_components)

    if not rolling_df.empty:
        theme = get_plotly_theme()

        window_choice = st.radio(
            "Rolling window",
            ["30-day", "60-day", "90-day"],
            index=0,
            horizontal=True,
        )
        window_col = {
            "30-day": "rolling_30d_failures",
            "60-day": "rolling_60d_failures",
            "90-day": "rolling_90d_failures",
        }[window_choice]

        fig = go.Figure()
        colors = ["#E63946", "#F77F00", "#FCBF49", "#06D6A0", "#118AB2"]

        for i, component in enumerate(selected_components):
            comp_df = rolling_df[rolling_df["component"] == component]
            fig.add_trace(go.Scatter(
                x=comp_df["repair_date"],
                y=comp_df[window_col],
                mode="lines",
                name=component,
                line=dict(color=colors[i % len(colors)], width=2),
            ))

        fig.update_layout(
            template=theme["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=theme["grid_color"], title=""),
            yaxis=dict(gridcolor=theme["grid_color"], title=f"{window_choice} rolling failures"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=380,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        render_section("Trend acceleration indicators")

        latest = rolling_df.sort_values("repair_date").groupby("component").tail(1)
        for _, row in latest.iterrows():
            ratio = row["trend_30d_vs_90d_ratio"]
            if pd.isna(ratio):
                continue

            if ratio >= 1.15:
                badge = f'<span class="badge badge-critical">Accelerating · {ratio}x</span>'
            elif ratio >= 1.05:
                badge = f'<span class="badge badge-high">Slight uptick · {ratio}x</span>'
            else:
                badge = f'<span class="badge badge-normal">Stable · {ratio}x</span>'

            st.markdown(
                f'<div style="padding:12px 16px; background:rgba(255,255,255,0.02); border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;"><span style="color:#E8E8F0; font-weight:500;">{row["component"]}</span>{badge}</div>',
                unsafe_allow_html=True
            )

render_section("Regional hotspots · failure rate deviation from baseline")

hotspots_df = load_regional_hotspots()
hotspots_only = hotspots_df[hotspots_df["is_hotspot"] == True].head(20)

if not hotspots_only.empty:
    theme = get_plotly_theme()
    pivot = hotspots_only.pivot_table(
        index="component",
        columns="region",
        values="regional_vs_baseline_ratio",
        aggfunc="max",
    ).fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[[0, "#1a1a28"], [0.3, "#8b3140"], [1, "#E63946"]],
        text=pivot.values,
        texttemplate="%{text:.2f}",
        textfont=dict(size=11, color="white"),
        colorbar=dict(title="Ratio", thickness=12),
    ))
    fig.update_layout(
        template=theme["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)
