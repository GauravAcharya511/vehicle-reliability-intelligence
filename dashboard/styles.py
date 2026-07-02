import streamlit as st


DARK_CSS = """
<style>
    /* Overall page */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Hide streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #1a1a28 0%, #16162a 100%);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b8ba7;
        margin-bottom: 8px;
        font-weight: 500;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #E8E8F0;
        line-height: 1;
    }

    .metric-delta-up {
        color: #ff6b6b;
        font-size: 12px;
        margin-top: 4px;
    }

    .metric-delta-down {
        color: #51cf66;
        font-size: 12px;
        margin-top: 4px;
    }

    /* Page header */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
        padding-bottom: 12px;
        border-bottom: 1px solid #2a2a3e;
    }

    .page-title {
        font-size: 24px;
        font-weight: 600;
        color: #E8E8F0;
        margin: 0;
    }

    .page-subtitle {
        font-size: 13px;
        color: #8b8ba7;
        margin-top: 4px;
    }

    /* Section header */
    .section-header {
        font-size: 15px;
        font-weight: 600;
        color: #b0b0c8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 24px 0 12px 0;
        padding-left: 8px;
        border-left: 3px solid #E63946;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-critical {
        background: rgba(230, 57, 70, 0.15);
        color: #ff6b6b;
        border: 1px solid rgba(230, 57, 70, 0.3);
    }

    .badge-high {
        background: rgba(255, 165, 0, 0.15);
        color: #ffa500;
        border: 1px solid rgba(255, 165, 0, 0.3);
    }

    .badge-normal {
        background: rgba(81, 207, 102, 0.15);
        color: #51cf66;
        border: 1px solid rgba(81, 207, 102, 0.3);
    }

    /* Data freshness indicator */
    .freshness-indicator {
        background: rgba(230, 57, 70, 0.08);
        border-left: 3px solid #E63946;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 12px;
        color: #b0b0c8;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0F0F1A;
        border-right: 1px solid #2a2a3e;
    }

    /* Dataframe styling */
    .dataframe {
        font-size: 13px;
    }
</style>
"""

LIGHT_CSS = """
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .metric-card {
        background: #ffffff;
        border: 1px solid #e8e8ec;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6b6b7d;
        margin-bottom: 8px;
        font-weight: 500;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a2e;
        line-height: 1;
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e8e8ec;
    }

    .page-title {
        font-size: 24px;
        font-weight: 600;
        color: #1a1a2e;
        margin: 0;
    }

    .page-subtitle {
        font-size: 13px;
        color: #6b6b7d;
        margin-top: 4px;
    }

    .section-header {
        font-size: 15px;
        font-weight: 600;
        color: #4b4b5e;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 24px 0 12px 0;
        padding-left: 8px;
        border-left: 3px solid #E63946;
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-critical {
        background: rgba(230, 57, 70, 0.1);
        color: #c92535;
        border: 1px solid rgba(230, 57, 70, 0.25);
    }

    .badge-high {
        background: rgba(255, 165, 0, 0.1);
        color: #d68d00;
        border: 1px solid rgba(255, 165, 0, 0.25);
    }

    .badge-normal {
        background: rgba(81, 207, 102, 0.1);
        color: #2f9d40;
        border: 1px solid rgba(81, 207, 102, 0.25);
    }

    .freshness-indicator {
        background: rgba(230, 57, 70, 0.04);
        border-left: 3px solid #E63946;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 12px;
        color: #6b6b7d;
    }

    section[data-testid="stSidebar"] {
        background: #f8f8fa;
        border-right: 1px solid #e8e8ec;
    }
</style>
"""


def apply_theme():
    theme = st.session_state.get("theme", "dark")
    if theme == "dark":
        st.markdown(DARK_CSS, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)


def render_metric(label: str, value: str, delta: str = None, delta_direction: str = "up"):
    delta_html = ""
    if delta:
        delta_class = "metric-delta-up" if delta_direction == "up" else "metric-delta-down"
        arrow = "↑" if delta_direction == "up" else "↓"
        delta_html = f'<div class="{delta_class}">{arrow} {delta}</div>'

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str):
    st.markdown(f"""
        <div class="page-header">
            <div>
                <div class="page-title">{title}</div>
                <div class="page-subtitle">{subtitle}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def render_freshness_indicator(last_run: str):
    st.markdown(f"""
        <div class="freshness-indicator">
            <strong>Last pipeline run:</strong> {last_run} · Powered by Airflow + dbt + PySpark + HuggingFace + Prophet
        </div>
    """, unsafe_allow_html=True)


def get_plotly_theme():
    theme = st.session_state.get("theme", "dark")
    if theme == "dark":
        return {
            "template": "plotly_dark",
            "bg_color": "#0A0A0F",
            "grid_color": "rgba(139, 139, 167, 0.15)",
            "text_color": "#E8E8F0",
            "muted_color": "#8b8ba7",
        }
    return {
        "template": "plotly_white",
        "bg_color": "#ffffff",
        "grid_color": "rgba(107, 107, 125, 0.15)",
        "text_color": "#1a1a2e",
        "muted_color": "#6b6b7d",
    }
