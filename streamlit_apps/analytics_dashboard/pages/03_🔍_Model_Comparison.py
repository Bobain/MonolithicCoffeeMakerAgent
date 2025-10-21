"""Model Comparison Page - LLM Analytics Dashboard.

This page provides side-by-side comparison of different LLM models
including performance metrics, latency, and cost efficiency.

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
from streamlit_apps.analytics_dashboard.components.charts import (
    create_latency_distribution_box,
    create_model_comparison_bar,
)
from streamlit_apps.analytics_dashboard.components.tables import render_sortable_table
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_model_performance_comparison,
    get_available_models,
    get_available_agents,
)
from streamlit_apps.analytics_dashboard.queries.performance_queries import (
    get_latency_percentiles,
    get_token_efficiency_by_model,
)


def main():
    """Main function for the Model Comparison page."""
    # Page configuration
    st.title("🔍 Model Comparison")
    st.markdown("### Compare Performance Across LLM Models")

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

    # Section 1: Model Performance Comparison Table
    st.subheader("Model Performance Metrics")

    try:
        with st.spinner("Loading model performance data..."):
            performance_data = get_model_performance_comparison(config.db_path, date_range)

            if performance_data.empty:
                st.info("No performance data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    performance_data = performance_data[performance_data["model_name"].isin(selected_models)]

                if performance_data.empty:
                    st.info("No data available for selected models.")
                else:
                    render_sortable_table(performance_data, title="Model Performance Comparison")

                    # Key insights
                    st.markdown("#### Key Insights")
                    col1, col2 = st.columns(2)

                    with col1:
                        best_value = performance_data.loc[performance_data["cost_per_request"].idxmin()]
                        st.success(
                            f"💵 **Most Cost-Effective**: {best_value['model_name']} "
                            f"(${best_value['cost_per_request']:.4f} per request)"
                        )

                    with col2:
                        fastest = performance_data.loc[performance_data["avg_latency_ms"].idxmin()]
                        st.success(
                            f"⚡ **Fastest**: {fastest['model_name']} "
                            f"({fastest['avg_latency_ms']:.1f}ms avg latency)"
                        )

    except Exception as e:
        st.error(f"Failed to load model performance: {e}")

    st.divider()

    # Section 2: Latency Distribution Box Plot
    st.subheader("Latency Distribution by Model")

    try:
        with st.spinner("Loading latency distribution..."):
            latency_data = get_latency_percentiles(config.db_path, date_range)

            if latency_data.empty:
                st.info("No latency data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    latency_data = latency_data[latency_data["model_name"].isin(selected_models)]

                if latency_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_latency_distribution_box(latency_data)
                    st.plotly_chart(fig, use_container_width=True)

                    st.caption("Box plot shows the distribution of latency across models. " "Lower is better.")

    except Exception as e:
        st.error(f"Failed to load latency distribution: {e}")

    st.divider()

    # Section 3: Cost per 1K Tokens Bar Chart
    st.subheader("Cost Efficiency Analysis")

    try:
        with st.spinner("Loading cost efficiency data..."):
            efficiency_data = get_token_efficiency_by_model(config.db_path, date_range)

            if efficiency_data.empty:
                st.info("No efficiency data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    efficiency_data = efficiency_data[efficiency_data["model_name"].isin(selected_models)]

                if efficiency_data.empty:
                    st.info("No data available for selected models.")
                else:
                    # Create bar chart for cost per 1K tokens
                    fig = create_model_comparison_bar(
                        efficiency_data, metric_column="cost_per_1k_tokens", title="Cost per 1,000 Tokens by Model"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show efficiency table
                    st.markdown("#### Detailed Efficiency Metrics")
                    render_sortable_table(efficiency_data, title="Token Efficiency Comparison")

    except Exception as e:
        st.error(f"Failed to load cost efficiency: {e}")

    st.divider()

    # Section 4: Model Comparison Bar Chart
    st.subheader("Request Volume by Model")

    try:
        with st.spinner("Loading request volume data..."):
            performance_data = get_model_performance_comparison(config.db_path, date_range)

            if performance_data.empty:
                st.info("No data available for the selected date range.")
            else:
                # Filter by selected models if any
                if selected_models:
                    performance_data = performance_data[performance_data["model_name"].isin(selected_models)]

                if performance_data.empty:
                    st.info("No data available for selected models.")
                else:
                    fig = create_model_comparison_bar(
                        performance_data, metric_column="request_count", title="Total Requests by Model"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Failed to load request volume: {e}")

    # Footer
    st.divider()
    st.caption("Compare models to optimize your LLM selection based on cost, speed, and usage patterns.")


if __name__ == "__main__":
    main()
