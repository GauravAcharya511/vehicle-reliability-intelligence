import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.styles import apply_theme
from dashboard.sidebar import render_sidebar

st.set_page_config(
    page_title="Vehicle Reliability Intelligence",
    page_icon=":red_car:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

apply_theme()
filters = render_sidebar()
st.session_state["filters"] = filters

st.markdown("""
    <div style='padding:40px 0; text-align:center;'>
        <div style='font-size:11px; color:#8b8ba7; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px;'>
            Vehicle Reliability Intelligence System
        </div>
        <div style='font-size:32px; font-weight:600; color:#E8E8F0; line-height:1.2; margin-bottom:16px;'>
            Fleet reliability analytics for engineering decision-making
        </div>
        <div style='font-size:14px; color:#b0b0c8; max-width:720px; margin:0 auto; line-height:1.6;'>
            End-to-end platform for identifying failure trends, forecasting component reliability,
            and surfacing engineering insights from repair data at fleet scale.
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-top:40px;'>
        <a href="/Fleet_Overview" target="_self" style='text-decoration:none;'>
            <div style='background:linear-gradient(135deg, #1a1a28 0%, #16162a 100%); border:1px solid #2a2a3e; border-radius:12px; padding:24px; cursor:pointer;'>
                <div style='font-size:11px; color:#E63946; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>01</div>
                <div style='font-size:15px; font-weight:600; color:#E8E8F0; margin-bottom:8px;'>Fleet Health Overview</div>
                <div style='font-size:12px; color:#8b8ba7; line-height:1.5;'>Top-line metrics, MTTF rankings, regional health.</div>
            </div>
        </a>
        <a href="/Failure_Trends" target="_self" style='text-decoration:none;'>
            <div style='background:linear-gradient(135deg, #1a1a28 0%, #16162a 100%); border:1px solid #2a2a3e; border-radius:12px; padding:24px; cursor:pointer;'>
                <div style='font-size:11px; color:#E63946; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>02</div>
                <div style='font-size:15px; font-weight:600; color:#E8E8F0; margin-bottom:8px;'>Failure Trend Analysis</div>
                <div style='font-size:12px; color:#8b8ba7; line-height:1.5;'>Rolling failure rates, hotspots, trend detection.</div>
            </div>
        </a>
        <a href="/NLP_Intelligence" target="_self" style='text-decoration:none;'>
            <div style='background:linear-gradient(135deg, #1a1a28 0%, #16162a 100%); border:1px solid #2a2a3e; border-radius:12px; padding:24px; cursor:pointer;'>
                <div style='font-size:11px; color:#E63946; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>03</div>
                <div style='font-size:15px; font-weight:600; color:#E8E8F0; margin-bottom:8px;'>NLP Failure Intelligence</div>
                <div style='font-size:12px; color:#8b8ba7; line-height:1.5;'>Severity classification, category breakdown.</div>
            </div>
        </a>
        <a href="/Predictive_Forecasts" target="_self" style='text-decoration:none;'>
            <div style='background:linear-gradient(135deg, #1a1a28 0%, #16162a 100%); border:1px solid #2a2a3e; border-radius:12px; padding:24px; cursor:pointer;'>
                <div style='font-size:11px; color:#E63946; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>04</div>
                <div style='font-size:15px; font-weight:600; color:#E8E8F0; margin-bottom:8px;'>Predictive Forecasts</div>
                <div style='font-size:12px; color:#8b8ba7; line-height:1.5;'>30/60/90-day Prophet forecasts by component.</div>
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)
