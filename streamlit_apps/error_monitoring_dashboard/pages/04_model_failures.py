"""Model Failures Page for Error Monitoring Dashboard.

This page provides detailed analysis of model-specific failures including
failure rates, error distributions, cost impacts, and trends by model.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from streamlit_apps.error_monitoring_dashboard.config import get_config
from streamlit_apps.error_monitoring_dashboard.queries.error_queries import (
    get_model_failure_rates,
    get_error_by_model,
    get_error_traces,
    get_available_models_with_errors,
)
from streamlit_apps.error_monitoring_dashboard.components import (
    create_failure_rate_chart,
    create_model_error_comparison,
    create_category_pie_chart,
    create_error_timeline,
    render_model_error_cards,
)

# Page configuration
st.set_page_config(
    page_title="Model Failures - Error Monitoring",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = get_config()

# Page header
st.title("🤖 Model Failures Analysis")
st.markdown(
    """
    Comprehensive analysis of model-specific failures. Compare error rates across models,
    identify problematic models, and understand the cost impact of failures.
    """
)

# Sidebar - Filters
st.sidebar.header("Filters")

# Date range selector
date_option = st.sidebar.selectbox(
    "Time Range",
    options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"],
    index=1,
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

# Model filter
st.sidebar.subheader("Model Filter")
try:
    db_path = config.absolute_db_path
    available_models = get_available_models_with_errors(db_path)
    selected_model = st.sidebar.selectbox(
        "Focus on Model",
        options=available_models,
        index=0,
        help="Select 'All' to compare all models, or choose a specific model for detailed analysis",
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
    **Model Analysis Tips**

    - Compare failure rates to identify problematic models
    - Check cost impact of failed requests
    - Analyze error patterns per model
    - Monitor trends to detect model degradation
    """
)

# Main content
try:
    # Model Failure Rate Comparison
    st.header("Model Failure Rate Comparison")
    st.caption("Compare error rates across all models")

    failure_rates_df = get_model_failure_rates(db_path, date_range=date_range)

    if not failure_rates_df.empty:
        # Show metrics for top models
        top_models = failure_rates_df.head(4)

        if not top_models.empty:
            model_stats = {}
            for _, row in top_models.iterrows():
                model_stats[row["model"]] = {
                    "errors": int(row["error_count"]),
                    "failure_rate": float(row["failure_rate"]) / 100,  # Convert to decimal
                }

            render_model_error_cards(model_stats)

        # Show bar chart
        st.subheader("Failure Rates by Model")
        fig_failure = create_failure_rate_chart(failure_rates_df, height=400)
        st.plotly_chart(fig_failure, use_container_width=True)

        # Show detailed table
        with st.expander("📊 View Detailed Model Statistics"):
            display_df = failure_rates_df.copy()
            display_df["failure_rate"] = display_df["failure_rate"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "model": "Model",
                    "error_count": st.column_config.NumberColumn("Errors", format="%d"),
                    "total_count": st.column_config.NumberColumn("Total Requests", format="%d"),
                    "failure_rate": "Failure Rate",
                },
            )

    else:
        st.info("No model failure data available for the selected time range.")

    st.divider()

    # Errors by Model Distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Error Count by Model")
        model_error_df = get_error_by_model(db_path, date_range=date_range)

        if not model_error_df.empty:
            fig_model_errors = create_model_error_comparison(model_error_df, height=400)
            st.plotly_chart(fig_model_errors, use_container_width=True)
        else:
            st.info("No model error data available.")

    with col2:
        st.subheader("Error Distribution (Pie)")
        if not model_error_df.empty:
            # Create pie chart data
            pie_df = model_error_df[["model", "error_count"]].rename(
                columns={"model": "category", "error_count": "count"}
            )
            fig_pie = create_category_pie_chart(pie_df, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No distribution data available.")

    st.divider()

    # Model-Specific Error Breakdown
    st.header("Model-Specific Error Breakdown")

    if selected_model and selected_model != "All":
        st.subheader(f"Detailed Analysis: {selected_model}")

        # Get errors for specific model
        model_errors = get_error_traces(db_path, limit=1000, date_range=date_range, model=selected_model)

        if not model_errors.empty:
            # Error type breakdown
            st.markdown("#### Error Types")
            error_type_counts = model_errors["error_type"].value_counts().reset_index()
            error_type_counts.columns = ["error_type", "count"]

            col1, col2 = st.columns([1, 2])

            with col1:
                st.dataframe(
                    error_type_counts.head(10),
                    use_container_width=True,
                    hide_index=True,
                )

            with col2:
                # Pie chart of error types for this model
                pie_data = error_type_counts.head(10).rename(columns={"error_type": "category"})
                fig_types = create_category_pie_chart(pie_data, height=300)
                st.plotly_chart(fig_types, use_container_width=True)

            # Common errors
            st.markdown("#### Common Error Messages")
            common_errors = model_errors["combined_error"].value_counts().head(5).reset_index()
            common_errors.columns = ["Error Message", "Count"]

            for idx, row in common_errors.iterrows():
                with st.expander(f"❌ {row['Error Message'][:80]}... ({row['Count']} occurrences)"):
                    st.code(row["Error Message"], language=None)

            # Severity distribution
            st.markdown("#### Severity Distribution")
            severity_counts = model_errors["severity"].value_counts()

            col1, col2, col3, col4 = st.columns(4)
            cols = [col1, col2, col3, col4]

            for idx, severity in enumerate(["CRITICAL", "HIGH", "MEDIUM", "LOW"]):
                with cols[idx]:
                    count = severity_counts.get(severity, 0)
                    st.metric(severity, f"{count:,}")

        else:
            st.info(f"No errors found for model: {selected_model}")

    else:
        st.info("Select a specific model from the sidebar to view detailed breakdown.")

    st.divider()

    # Model Error Trends Over Time
    st.header("Model Error Trends Over Time")

    if selected_model and selected_model != "All":
        st.subheader(f"Error Timeline: {selected_model}")

        model_errors = get_error_traces(db_path, limit=5000, date_range=date_range, model=selected_model)

        if not model_errors.empty:
            # Create hourly timeline
            model_errors["hour"] = pd.to_datetime(model_errors["timestamp"]).dt.floor("H")
            timeline = model_errors.groupby("hour").size().reset_index(name="error_count")

            fig_timeline = create_error_timeline(timeline, height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Errors", f"{len(model_errors):,}")
            with col2:
                avg_per_hour = len(model_errors) / max(hours, 1)
                st.metric("Avg Errors/Hour", f"{avg_per_hour:.1f}")
            with col3:
                unique_types = model_errors["error_type"].nunique()
                st.metric("Unique Error Types", unique_types)

        else:
            st.info(f"No timeline data for {selected_model}")

    else:
        st.info("Select a specific model to view trends over time.")

    st.divider()

    # Cost Impact of Errors
    st.header("Cost Impact of Errors by Model")
    st.caption("Estimated cost wasted due to failed requests")

    try:
        error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)

        if not error_traces.empty and "total_cost" in error_traces.columns:
            # Calculate cost by model
            cost_by_model = error_traces.groupby("model")["total_cost"].agg(["sum", "mean", "count"]).reset_index()
            cost_by_model.columns = ["model", "total_cost", "avg_cost", "error_count"]
            cost_by_model = cost_by_model.sort_values("total_cost", ascending=False)

            # Display metrics
            col1, col2 = st.columns(2)

            with col1:
                total_wasted = cost_by_model["total_cost"].sum()
                st.metric("Total Cost Wasted", f"${total_wasted:.2f}")

            with col2:
                avg_cost = cost_by_model["avg_cost"].mean()
                st.metric("Avg Cost per Error", f"${avg_cost:.4f}")

            # Show table
            display_cost_df = cost_by_model.copy()
            display_cost_df["total_cost"] = display_cost_df["total_cost"].apply(lambda x: f"${x:.2f}")
            display_cost_df["avg_cost"] = display_cost_df["avg_cost"].apply(lambda x: f"${x:.4f}")

            st.dataframe(
                display_cost_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "model": "Model",
                    "total_cost": "Total Wasted",
                    "avg_cost": "Avg per Error",
                    "error_count": st.column_config.NumberColumn("Error Count", format="%d"),
                },
            )

            # Bar chart
            import plotly.express as px

            fig_cost = px.bar(
                cost_by_model,
                x="model",
                y="total_cost",
                title="Cost Impact by Model",
                color="total_cost",
                color_continuous_scale="Reds",
            )

            fig_cost.update_layout(
                xaxis_title="Model",
                yaxis_title="Total Cost ($)",
                height=400,
                showlegend=False,
            )

            st.plotly_chart(fig_cost, use_container_width=True)

        else:
            st.info("Cost data not available for error traces.")

    except Exception as e:
        st.error(f"Error calculating cost impact: {e}")

    # Export section
    st.divider()
    st.header("Export Model Data")

    col1, col2 = st.columns(2)

    with col1:
        if not failure_rates_df.empty:
            st.download_button(
                label="📥 Download Failure Rates (CSV)",
                data=failure_rates_df.to_csv(index=False),
                file_name=f"model_failure_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

    with col2:
        if not model_error_df.empty:
            st.download_button(
                label="📥 Download Error Distribution (CSV)",
                data=model_error_df.to_csv(index=False),
                file_name=f"model_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(
        "Please ensure the Langfuse export database exists at the configured path. "
        "Run the analytics export process first."
    )
except Exception as e:
    st.error(f"❌ Error loading model failure data: {e}")
    st.exception(e)
