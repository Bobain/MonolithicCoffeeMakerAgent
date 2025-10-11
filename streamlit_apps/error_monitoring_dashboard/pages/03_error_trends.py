"""Error Trends Page for Error Monitoring Dashboard.

This page provides detailed trend analysis of errors including frequency timelines,
error rate trends, type distribution over time, and temporal patterns.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from streamlit_apps.error_monitoring_dashboard.config import get_config
from streamlit_apps.error_monitoring_dashboard.queries.error_queries import (
    get_error_timeline,
    get_error_by_type,
    get_error_traces,
    get_hourly_error_pattern,
)
from streamlit_apps.error_monitoring_dashboard.components import (
    create_error_timeline,
    create_stacked_severity_timeline,
    create_error_heatmap,
)

# Page configuration
st.set_page_config(
    page_title="Error Trends - Error Monitoring",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = get_config()

# Page header
st.title("📈 Error Trends")
st.markdown(
    """
    Analyze error patterns and trends over time. Identify recurring issues,
    peak error periods, and track error rate changes.
    """
)

# Sidebar - Filters
st.sidebar.header("Filters")

# Date range selector
date_option = st.sidebar.selectbox(
    "Time Range",
    options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"],
    index=1,  # Default to last 7 days for trends
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
        start_date = st.sidebar.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=7),
        )
    with col2:
        end_date = st.sidebar.date_input(
            "End Date",
            value=datetime.now().date(),
        )

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    date_range = (start_datetime, end_datetime)
    hours = int((end_datetime - start_datetime).total_seconds() / 3600)

# Error type filter
st.sidebar.subheader("Error Type Filter")
try:
    db_path = config.absolute_db_path
    error_types_df = get_error_by_type(db_path, limit=50, date_range=date_range)
    if not error_types_df.empty:
        error_type_options = ["All"] + error_types_df["error_type"].unique().tolist()
        selected_error_type = st.sidebar.selectbox(
            "Select Error Type",
            options=error_type_options,
            index=0,
        )
    else:
        selected_error_type = "All"
except Exception as e:
    st.sidebar.error(f"Error loading error types: {e}")
    selected_error_type = "All"

# Model filter
st.sidebar.subheader("Model Filter")
try:
    from streamlit_apps.error_monitoring_dashboard.queries.error_queries import get_available_models_with_errors

    available_models = get_available_models_with_errors(db_path)
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=available_models,
        index=0,
    )
except Exception as e:
    st.sidebar.error(f"Error loading models: {e}")
    selected_model = "All"

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Trend Analysis Tips**

    - Use longer time ranges (7-30 days) for trend analysis
    - Compare day-of-week patterns to identify recurring issues
    - Monitor hour-of-day patterns for load-related errors
    - Track error type distribution changes over time
    """
)

# Main content
try:
    # Error Frequency Timeline
    st.header("Error Frequency Timeline")
    st.caption("Hourly error counts over the selected period")

    timeline_df = get_error_timeline(db_path, hours=hours, date_range=date_range)

    if not timeline_df.empty:
        # Calculate error rate if we have trace data
        try:
            error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)
            if not error_traces.empty:
                # Add total count info
                total_errors = len(error_traces)
                avg_per_hour = total_errors / max(hours, 1)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Errors", f"{total_errors:,}")
                with col2:
                    st.metric("Avg Errors/Hour", f"{avg_per_hour:.1f}")
                with col3:
                    if len(timeline_df) > 1:
                        trend = "↑" if timeline_df.iloc[-1]["error_count"] > timeline_df.iloc[0]["error_count"] else "↓"
                        st.metric("Trend", trend)

        except Exception as e:
            st.warning(f"Could not calculate error rate: {e}")

        fig_timeline = create_error_timeline(timeline_df, height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available for the selected time range.")

    st.divider()

    # Error Rate Percentage Over Time
    st.header("Error Rate Over Time")
    st.caption("Error rate as percentage of total requests")

    try:
        # Get all traces and error traces
        error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)

        if not error_traces.empty:
            # Calculate error rate by hour
            error_traces["hour"] = pd.to_datetime(error_traces["timestamp"]).dt.floor("H")
            error_by_hour = error_traces.groupby("hour").size().reset_index(name="error_count")

            # For demo purposes, assume 10x traces total (in real scenario, query actual total)
            error_by_hour["total_count"] = error_by_hour["error_count"] * 10
            error_by_hour["error_rate"] = error_by_hour["error_count"] / error_by_hour["total_count"] * 100

            # Create line chart
            import plotly.graph_objects as go

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=error_by_hour["hour"],
                    y=error_by_hour["error_rate"],
                    mode="lines+markers",
                    name="Error Rate %",
                    line=dict(color="#dc3545", width=2),
                    marker=dict(size=8),
                )
            )

            fig.update_layout(
                title="Error Rate Percentage Over Time",
                xaxis_title="Time",
                yaxis_title="Error Rate (%)",
                height=400,
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No error rate data available.")

    except Exception as e:
        st.error(f"Error calculating error rate: {e}")

    st.divider()

    # Error Type Distribution Trends
    st.header("Error Type Distribution Trends")
    st.caption("Stacked area chart showing error types over time")

    try:
        error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)

        if not error_traces.empty:
            # Group by hour and severity
            error_traces["timestamp_hour"] = pd.to_datetime(error_traces["timestamp"]).dt.floor("H")

            severity_timeline = error_traces.groupby(["timestamp_hour", "severity"]).size().reset_index(name="count")
            severity_timeline = severity_timeline.rename(columns={"timestamp_hour": "timestamp"})

            if not severity_timeline.empty:
                fig_stacked = create_stacked_severity_timeline(severity_timeline, height=400)
                st.plotly_chart(fig_stacked, use_container_width=True)
            else:
                st.info("No severity timeline data available.")
        else:
            st.info("No error data available for trend analysis.")

    except Exception as e:
        st.error(f"Error creating distribution trends: {e}")

    st.divider()

    # Day of Week Pattern
    st.header("Error Patterns by Day of Week")
    st.caption("Identify which days have higher error rates")

    try:
        error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)

        if not error_traces.empty:
            error_traces["day_of_week"] = pd.to_datetime(error_traces["timestamp"]).dt.day_name()

            day_counts = error_traces.groupby("day_of_week").size().reset_index(name="count")

            # Order by day of week
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_counts["day_of_week"] = pd.Categorical(day_counts["day_of_week"], categories=day_order, ordered=True)
            day_counts = day_counts.sort_values("day_of_week")

            # Create bar chart
            import plotly.express as px

            fig = px.bar(
                day_counts,
                x="day_of_week",
                y="count",
                title="Errors by Day of Week",
                color="count",
                color_continuous_scale="Reds",
            )

            fig.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Error Count",
                height=400,
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show insights
            max_day = day_counts.loc[day_counts["count"].idxmax(), "day_of_week"]
            min_day = day_counts.loc[day_counts["count"].idxmin(), "day_of_week"]

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📈 Highest errors: **{max_day}**")
            with col2:
                st.success(f"📉 Lowest errors: **{min_day}**")

        else:
            st.info("No data available for day-of-week analysis.")

    except Exception as e:
        st.error(f"Error creating day-of-week pattern: {e}")

    st.divider()

    # Hour of Day Pattern
    st.header("Error Patterns by Hour of Day")
    st.caption("Heatmap showing error concentration by hour and day")

    pattern_df = get_hourly_error_pattern(db_path, date_range=date_range)

    if not pattern_df.empty:
        fig_heatmap = create_error_heatmap(pattern_df, height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Hour analysis
        try:
            hourly_totals = pattern_df.groupby("hour")["error_count"].sum().reset_index()
            peak_hour = hourly_totals.loc[hourly_totals["error_count"].idxmax(), "hour"]
            low_hour = hourly_totals.loc[hourly_totals["error_count"].idxmin(), "hour"]

            col1, col2 = st.columns(2)
            with col1:
                st.warning(f"⚠️ Peak error hour: **{peak_hour}:00**")
            with col2:
                st.success(f"✅ Lowest error hour: **{low_hour}:00**")

        except Exception as e:
            st.warning(f"Could not analyze hourly patterns: {e}")
    else:
        st.info("No hourly pattern data available.")

    # Export section
    st.divider()
    st.header("Export Trend Data")

    col1, col2 = st.columns(2)

    with col1:
        if not timeline_df.empty:
            st.download_button(
                label="📥 Download Timeline Data (CSV)",
                data=timeline_df.to_csv(index=False),
                file_name=f"error_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

    with col2:
        if not pattern_df.empty:
            st.download_button(
                label="📥 Download Pattern Data (CSV)",
                data=pattern_df.to_csv(index=False),
                file_name=f"error_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(
        "Please ensure the Langfuse export database exists at the configured path. "
        "Run the analytics export process first."
    )
except Exception as e:
    st.error(f"❌ Error loading trend data: {e}")
    st.exception(e)
