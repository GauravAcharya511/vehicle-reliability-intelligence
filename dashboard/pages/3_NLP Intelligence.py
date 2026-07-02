import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dashboard.styles import apply_theme, render_metric, render_page_header, render_section, render_freshness_indicator, get_plotly_theme
from dashboard.sidebar import render_sidebar
from dashboard.data import (
    load_nlp_severity_distribution,
    load_nlp_category_distribution,
    load_critical_by_component,
    load_severity_component_matrix,
    load_last_pipeline_run,
)

st.set_page_config(page_title="NLP Intelligence", layout="wide")
apply_theme()
filters = render_sidebar()

render_page_header(
    "NLP Failure Intelligence",
    "Zero-shot classification of repair descriptions using HuggingFace BART-MNLI. Failure category, severity, and root cause dimensions."
)

render_freshness_indicator(load_last_pipeline_run())

severity_df = load_nlp_severity_distribution()
critical_count = severity_df[severity_df["nlp_severity"] == "critical safety issue"]["count"].sum() if not severity_df.empty else 0
total_count = severity_df["count"].sum() if not severity_df.empty else 0
critical_pct = round(100 * critical_count / total_count, 1) if total_count > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Records classified", f"{int(total_count):,}")
with col2:
    render_metric("Critical safety flags", f"{int(critical_count):,}")
with col3:
    render_metric("Critical rate", f"{critical_pct}%")
with col4:
    render_metric("NLP dimensions", "3")

col_left, col_right = st.columns([1, 1])

with col_left:
    render_section("Severity distribution")

    theme = get_plotly_theme()
    colors_map = {
        "critical safety issue": "#E63946",
        "high severity functional failure": "#F77F00",
        "medium severity inconvenience": "#FCBF49",
    }
    colors = [colors_map.get(s, "#8b8ba7") for s in severity_df["nlp_severity"]]

    fig = go.Figure(go.Pie(
        labels=severity_df["nlp_severity"],
        values=severity_df["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=theme["bg_color"], width=2)),
        textinfo="percent",
        textfont=dict(size=13, color="white"),
    ))
    fig.update_layout(
        template=theme["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=11)),
        annotations=[dict(text=f"<b>{int(total_count):,}</b><br>records", x=0.5, y=0.5, font=dict(size=16, color=theme["text_color"]), showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    render_section("Failure category breakdown")

    category_df = load_nlp_category_distribution()
    theme = get_plotly_theme()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=category_df["nlp_failure_category"],
        x=category_df["count"],
        orientation="h",
        marker=dict(color="#E63946", line=dict(color="#8b3140", width=0)),
        text=category_df.apply(lambda r: f"{r['count']:,} · {r['avg_confidence']:.0%} conf", axis=1),
        textposition="outside",
        textfont=dict(color=theme["text_color"], size=11),
    ))
    fig.update_layout(
        template=theme["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=theme["grid_color"], title=""),
        yaxis=dict(title=""),
        margin=dict(l=20, r=80, t=20, b=20),
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

render_section("Critical safety issues by component")

critical_df = load_critical_by_component()
st.dataframe(
    critical_df.rename(columns={
        "component": "Component",
        "critical_count": "Critical flags",
        "avg_cost": "Avg cost ($)",
        "total_cost": "Total cost ($)",
    }),
    use_container_width=True,
    hide_index=True,
    height=320,
)

render_section("Severity × component heatmap")

matrix_df = load_severity_component_matrix()
pivot = matrix_df.pivot_table(
    index="component",
    columns="nlp_severity",
    values="count",
    aggfunc="sum",
).fillna(0)

theme = get_plotly_theme()
fig = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale=[[0, "#1a1a28"], [0.5, "#8b3140"], [1, "#E63946"]],
    text=pivot.values.astype(int),
    texttemplate="%{text}",
    textfont=dict(size=11, color="white"),
    colorbar=dict(title="Count", thickness=12),
))
fig.update_layout(
    template=theme["template"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
)
st.plotly_chart(fig, use_container_width=True)
