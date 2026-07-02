import streamlit as st
from dashboard.data import get_filter_options, load_last_pipeline_run


def render_sidebar():
    with st.sidebar:
        st.markdown("### Vehicle Reliability")
        st.markdown("<div style='font-size:11px; color:#8b8ba7; margin-bottom:20px;'>Intelligence System</div>", unsafe_allow_html=True)

        theme = st.radio(
            "Theme",
            ["dark", "light"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state["theme"] = theme

        st.markdown("---")
        st.markdown("<div style='font-size:11px; color:#8b8ba7; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Filters</div>", unsafe_allow_html=True)

        options = get_filter_options()

        date_range = st.date_input(
            "Date range",
            value=(options["min_date"], options["max_date"]),
            min_value=options["min_date"],
            max_value=options["max_date"],
        )

        selected_regions = st.multiselect(
            "Region",
            options=options["regions"],
            default=[],
            placeholder="All regions",
        )

        selected_models = st.multiselect(
            "Vehicle model",
            options=options["models"],
            default=[],
            placeholder="All models",
        )

        st.markdown("---")

        last_run = load_last_pipeline_run()
        st.markdown(f"""
            <div style='font-size:11px; color:#8b8ba7;'>
                <div style='text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;'>Last pipeline run</div>
                <div style='color:#b0b0c8; font-weight:500;'>{last_run}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px; font-size:10px; color:#6b6b7d; line-height:1.6;'>Pipeline: Airflow · dbt · PySpark · HuggingFace · Prophet</div>", unsafe_allow_html=True)

    return {
        "date_range": date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None,
        "regions": selected_regions if selected_regions else None,
        "models": selected_models if selected_models else None,
    }
