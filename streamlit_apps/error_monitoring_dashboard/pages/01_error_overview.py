"""Error Overview Page for Error Monitoring Dashboard.

This page displays a comprehensive overview of error metrics including summary cards,
timeline charts, error type distributions, and recent error lists.
"""

import streamlit as st
from datetime import datetime, timedelta

from streamlit_apps.error_monitoring_dashboard.config import get_config
from streamlit_apps.error_monitoring_dashboard.queries.error_queries import (
    get_error_summary,
    get_error_timeline,
    get_error_by_type,
    get_error_by_model,
    get_error_severity_distribution,
    get_recent_errors,
    get_hourly_error_pattern,
)
from streamlit_apps.error_monitoring_dashboard.components import (
    render_error_summary_cards,
    render_severity_metric_cards,
    create_error_timeline,
    create_error_type_bar_chart,
    create_category_pie_chart,
    create_error_heatmap,
    render_trace_table,
)

# Page configuration
st.set_page_config(
    page_title="Error Overview - Error Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = get_config()

# Page header
st.title("📊 Error Overview")
st.markdown(
    """
    Comprehensive overview of error metrics across your LLM applications.
    Monitor error rates, severity distribution, and identify trends.
    """
)

# Sidebar - Date Range Filter
st.sidebar.header("Filters")

# Date range selector
date_option = st.sidebar.selectbox(
    "Time Range",
    options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"],
    index=0,
)

if date_option == "Last 24 Hours":
    hours = 24
    date_range = None
elif date_option == "Last 7 Days":
    hours = 24 * 7
    date_range = None
elif date_option == "Last 30 Days":
    hours = 24 * 30
    date_range = None
else:  # Custom Range
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=7),
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
        )

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    date_range = (start_datetime, end_datetime)
    hours = int((end_datetime - start_datetime).total_seconds() / 3600)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **About This Page**

    The Error Overview provides a high-level view of all errors occurring
    in your LLM traces. Use the filters to explore different time periods.
    """
)

# Main content
try:
    db_path = config.absolute_db_path

    # Summary metrics
    st.header("Error Summary")
    error_stats = get_error_summary(db_path, hours=hours if not date_range else 168)

    if date_range:
        # Recalculate stats for custom range
        from streamlit_apps.error_monitoring_dashboard.queries.error_queries import get_error_traces

        error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)
        error_stats["total_errors"] = len(error_traces)
        # Keep other stats as approximations

    render_error_summary_cards(error_stats)

    # Severity distribution
    st.header("Severity Distribution")
    severity_df = get_error_severity_distribution(db_path, date_range=date_range)

    if not severity_df.empty:
        severity_counts = dict(zip(severity_df["severity"], severity_df["count"]))
        render_severity_metric_cards(severity_counts)
    else:
        st.info("No severity data available for the selected time range.")

    st.divider()

    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Error Timeline")
        timeline_df = get_error_timeline(db_path, hours=hours, date_range=date_range)

        if not timeline_df.empty:
            fig_timeline = create_error_timeline(timeline_df, height=350)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No timeline data available for the selected time range.")

    with col2:
        st.subheader("Top 5 Error Types")
        error_types_df = get_error_by_type(db_path, limit=5, date_range=date_range)

        if not error_types_df.empty:
            fig_types = create_error_type_bar_chart(error_types_df, height=350)
            st.plotly_chart(fig_types, use_container_width=True)
        else:
            st.info("No error type data available for the selected time range.")

    st.divider()

    # Model and pattern analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Errors by Model")
        model_df = get_error_by_model(db_path, date_range=date_range)

        if not model_df.empty:
            # Create pie chart data
            model_chart_df = model_df[["model", "error_count"]].rename(
                columns={"model": "category", "error_count": "count"}
            )
            fig_model = create_category_pie_chart(model_chart_df, height=350)
            st.plotly_chart(fig_model, use_container_width=True)
        else:
            st.info("No model data available for the selected time range.")

    with col2:
        st.subheader("Error Severity Heatmap")
        st.caption("Error patterns by hour and day of week")

        pattern_df = get_hourly_error_pattern(db_path, date_range=date_range)

        if not pattern_df.empty:
            fig_heatmap = create_error_heatmap(pattern_df, height=350)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No pattern data available for the selected time range.")

    st.divider()

    # Recent errors table
    st.header("Recent Errors")
    st.caption("Last 10 error traces")

    recent_errors_df = get_recent_errors(db_path, limit=10, date_range=date_range)

    if not recent_errors_df.empty:
        render_trace_table(recent_errors_df)
    else:
        st.info("No recent errors found for the selected time range.")

    # Export option
    if not recent_errors_df.empty:
        st.download_button(
            label="📥 Download Recent Errors (CSV)",
            data=recent_errors_df.to_csv(index=False),
            file_name=f"recent_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(
        "Please ensure the Langfuse export database exists at the configured path. "
        "Run the analytics export process first."
    )
except Exception as e:
    st.error(f"❌ Error loading dashboard data: {e}")
    st.exception(e)
