"""Cost Analysis Page - LLM Analytics Dashboard.

This page provides detailed cost analysis including hourly breakdown,
expensive requests, budget tracking, and cost forecasts.

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
from streamlit_apps.analytics_dashboard.components.metrics import render_progress_bar
from streamlit_apps.analytics_dashboard.components.charts import (
    create_cost_trend_line,
)
from streamlit_apps.analytics_dashboard.components.tables import render_sortable_table
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_available_models,
    get_available_agents,
)
from streamlit_apps.analytics_dashboard.queries.cost_queries import (
    get_hourly_cost_breakdown,
    get_most_expensive_requests,
    get_budget_tracking,
    get_cost_forecast,
)


def main():
    """Main function for the Cost Analysis page."""
    # Page configuration
    st.title("💰 Cost Analysis")
    st.markdown("### Detailed Cost Breakdown and Forecasts")

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

    # Display filter summary
    st.caption(f"Showing data from {date_range[0]} to {date_range[1]}")

    st.divider()

    # Section 1: Budget Tracking
    st.subheader("Budget Tracking")

    try:
        with st.spinner("Loading budget information..."):
            budget_data = get_budget_tracking(config.db_path, date_range)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Spent", f"${budget_data['total_cost']:.2f}")

            with col2:
                st.metric("Daily Average", f"${budget_data['daily_avg']:.2f}")

            with col3:
                st.metric("Budget Utilization", f"{budget_data['budget_percentage']:.1f}%")

            # Progress bar for budget usage
            render_progress_bar(
                label="Budget Usage",
                current=budget_data["total_cost"],
                total=budget_data["budget_limit"],
                format_as="both",
            )

            if budget_data["budget_percentage"] > 90:
                st.warning("⚠️ Budget utilization is above 90%!")
            elif budget_data["budget_percentage"] > 75:
                st.info("ℹ️ Budget utilization is above 75%")

    except Exception as e:
        st.error(f"Failed to load budget tracking: {e}")

    st.divider()

    # Section 2: Hourly Cost Breakdown
    st.subheader("Hourly Cost Breakdown")

    try:
        with st.spinner("Loading hourly cost breakdown..."):
            hourly_data = get_hourly_cost_breakdown(config.db_path, date_range)

            if hourly_data.empty:
                st.info("No hourly cost data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    hourly_data = hourly_data[hourly_data["model_name"].isin(selected_models)]

                if hourly_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_cost_trend_line(hourly_data)
                    st.plotly_chart(fig, use_container_width=True)

                    # Show summary statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Peak Hour Cost", f"${hourly_data['cost'].max():.2f}")
                    with col2:
                        st.metric("Average Hourly", f"${hourly_data['cost'].mean():.2f}")
                    with col3:
                        st.metric("Minimum Hour Cost", f"${hourly_data['cost'].min():.2f}")

    except Exception as e:
        st.error(f"Failed to load hourly cost breakdown: {e}")

    st.divider()

    # Section 3: Most Expensive Requests
    st.subheader("Most Expensive Requests")

    try:
        with st.spinner("Loading most expensive requests..."):
            expensive_requests = get_most_expensive_requests(config.db_path, date_range, limit=20)

            if expensive_requests.empty:
                st.info("No request data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    expensive_requests = expensive_requests[expensive_requests["model_name"].isin(selected_models)]

                if expensive_requests.empty:
                    st.info("No data available for selected models.")
                else:
                    render_sortable_table(expensive_requests, title="Top 20 Most Expensive API Requests")

    except Exception as e:
        st.error(f"Failed to load expensive requests: {e}")

    st.divider()

    # Section 4: 7-Day Cost Forecast
    st.subheader("7-Day Cost Forecast")

    try:
        with st.spinner("Generating cost forecast..."):
            forecast_data = get_cost_forecast(config.db_path, date_range, forecast_days=7)

            if forecast_data.empty:
                st.info("Insufficient data to generate forecast.")
            else:
                fig = create_cost_trend_line(forecast_data)
                st.plotly_chart(fig, use_container_width=True)

                # Show forecast summary
                forecast_total = forecast_data[forecast_data["is_forecast"]]["cost"].sum()
                st.info(f"📊 Projected spending for next 7 days: **${forecast_total:.2f}**")

    except Exception as e:
        st.error(f"Failed to generate cost forecast: {e}")

    # Footer
    st.divider()
    st.caption("Cost data updated in real-time. Use filters to analyze specific models or time periods.")


if __name__ == "__main__":
    main()
