"""Overview Page - LLM Analytics Dashboard.

This page displays global metrics and trends for LLM usage.
Shows cost breakdown, daily trends, and token usage statistics.

Usage:
    Navigate to this page via the sidebar in the multi-page Streamlit app.
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_apps.analytics_dashboard.config import get_config
from streamlit_apps.analytics_dashboard.components.filters import render_global_filters
from streamlit_apps.analytics_dashboard.components.metrics import render_metric_cards
from streamlit_apps.analytics_dashboard.components.charts import (
    create_cost_breakdown_pie,
    create_cost_trend_line,
    create_token_usage_stacked_bar,
)
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_quick_stats,
    get_cost_by_model,
    get_daily_cost_trend,
    get_token_usage_breakdown,
    get_available_models,
    get_available_agents,
)


def main():
    """Main function for the Overview page."""
    # Page configuration
    st.title("📈 Overview")
    st.markdown("### Global Metrics and Trends")

    # Load configuration
    try:
        config = get_config()
        config.validate()
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.stop()

    # Render filters in sidebar
    try:
        with st.spinner("Loading filter options..."):
            available_models = get_available_models(config.db_path)
            available_agents = get_available_agents(config.db_path)
    except Exception as e:
        st.error(f"Failed to load filter options: {e}")
        st.stop()

    filters = render_global_filters(available_models, available_agents)

    # Extract filter values
    date_range = filters["date_range"]
    selected_models = filters["models"] if filters["models"] else None
    filters["agents"] if filters["agents"] else None

    # Display filter summary
    st.caption(f"Showing data from {date_range[0]} to {date_range[1]}")

    st.divider()

    # Section 1: Metric Cards
    st.subheader("Key Performance Indicators")

    try:
        with st.spinner("Loading metrics..."):
            stats = get_quick_stats(config.db_path, date_range)
            render_metric_cards(stats)
    except Exception as e:
        st.error(f"Failed to load metrics: {e}")

    st.divider()

    # Section 2: Cost Breakdown Pie Chart
    st.subheader("Cost Breakdown by Model")

    try:
        with st.spinner("Loading cost breakdown..."):
            cost_data = get_cost_by_model(config.db_path, date_range)

            if cost_data.empty:
                st.info("No cost data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    cost_data = cost_data[cost_data["model_name"].isin(selected_models)]

                if cost_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_cost_breakdown_pie(cost_data)
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load cost breakdown: {e}")

    st.divider()

    # Section 3: Daily Cost Trend Line Chart
    st.subheader("Daily Cost Trend")

    try:
        with st.spinner("Loading cost trend..."):
            trend_data = get_daily_cost_trend(config.db_path, date_range, granularity=filters["time_granularity"])

            if trend_data.empty:
                st.info("No trend data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    trend_data = trend_data[trend_data["model_name"].isin(selected_models)]

                if trend_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_cost_trend_line(trend_data)
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load cost trend: {e}")

    st.divider()

    # Section 4: Token Usage Stacked Bar Chart
    st.subheader("Token Usage by Model")

    try:
        with st.spinner("Loading token usage..."):
            token_data = get_token_usage_breakdown(config.db_path, date_range)

            if token_data.empty:
                st.info("No token usage data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    token_data = token_data[token_data["model_name"].isin(selected_models)]

                if token_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_token_usage_stacked_bar(token_data)
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load token usage: {e}")

    # Footer
    st.divider()
    st.caption("Data refreshed from database. Use filters in the sidebar to refine the view.")


if __name__ == "__main__":
    main()
