"""Agent Performance Page - LLM Analytics Dashboard.

This page provides agent-specific performance analytics including
cost breakdown, latency comparison, and usage patterns.

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
    create_cost_breakdown_pie,
    create_model_comparison_bar,
)
from streamlit_apps.analytics_dashboard.components.tables import render_sortable_table
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_agent_analysis,
    get_available_models,
    get_available_agents,
)


def main():
    """Main function for the Agent Performance page."""
    # Page configuration
    st.title("🤖 Agent Performance")
    st.markdown("### Agent-Specific Analytics and Insights")

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
    selected_agents = filters["agents"] if filters["agents"] else None

    # Display filter summary
    st.caption(f"Showing data from {date_range[0]} to {date_range[1]}")

    st.divider()

    # Section 1: Agent Analysis Table
    st.subheader("Agent Performance Metrics")

    try:
        with st.spinner("Loading agent performance data..."):
            agent_data = get_agent_analysis(config.db_path, date_range)

            if agent_data.empty:
                st.info("No agent data available for the selected date range.")
            else:
                # Filter by selected agents if any
                if selected_agents:
                    agent_data = agent_data[agent_data["agent_name"].isin(selected_agents)]

                if agent_data.empty:
                    st.info("No data available for selected agents.")
                else:
                    render_sortable_table(agent_data, title="Agent Performance Analysis")

                    # Key insights
                    st.markdown("#### Key Insights")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        most_used = agent_data.loc[agent_data["request_count"].idxmax()]
                        st.info(
                            f"🔥 **Most Active Agent**: {most_used['agent_name']} "
                            f"({most_used['request_count']:,} requests)"
                        )

                    with col2:
                        most_expensive = agent_data.loc[agent_data["total_cost"].idxmax()]
                        st.info(
                            f"💰 **Highest Cost**: {most_expensive['agent_name']} "
                            f"(${most_expensive['total_cost']:.2f})"
                        )

                    with col3:
                        fastest = agent_data.loc[agent_data["avg_latency_ms"].idxmin()]
                        st.info(
                            f"⚡ **Fastest Agent**: {fastest['agent_name']} " f"({fastest['avg_latency_ms']:.1f}ms)"
                        )

    except Exception as e:
        st.error(f"Failed to load agent performance: {e}")

    st.divider()

    # Section 2: Agent Cost Breakdown Pie Chart
    st.subheader("Cost Distribution by Agent")

    try:
        with st.spinner("Loading cost breakdown..."):
            agent_data = get_agent_analysis(config.db_path, date_range)

            if agent_data.empty:
                st.info("No cost data available for the selected date range.")
            else:
                # Filter by selected agents if any
                if selected_agents:
                    agent_data = agent_data[agent_data["agent_name"].isin(selected_agents)]

                if agent_data.empty:
                    st.info("No data available for selected agents.")
                else:
                    # Prepare data for pie chart (rename column to match expected format)
                    pie_data = agent_data.rename(columns={"agent_name": "model_name"})

                    fig = create_cost_breakdown_pie(pie_data)
                    st.plotly_chart(fig, use_container_width=True)

                    # Cost summary
                    total_cost = agent_data["total_cost"].sum()
                    st.metric("Total Agent Cost", f"${total_cost:.2f}")

    except Exception as e:
        st.error(f"Failed to load cost breakdown: {e}")

    st.divider()

    # Section 3: Agent Latency Comparison
    st.subheader("Agent Latency Comparison")

    try:
        with st.spinner("Loading latency comparison..."):
            agent_data = get_agent_analysis(config.db_path, date_range)

            if agent_data.empty:
                st.info("No latency data available for the selected date range.")
            else:
                # Filter by selected agents if any
                if selected_agents:
                    agent_data = agent_data[agent_data["agent_name"].isin(selected_agents)]

                if agent_data.empty:
                    st.info("No data available for selected agents.")
                else:
                    # Prepare data for bar chart (rename column to match expected format)
                    bar_data = agent_data.rename(columns={"agent_name": "model_name"})

                    fig = create_model_comparison_bar(
                        bar_data, metric_column="avg_latency_ms", title="Average Latency by Agent (ms)"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Latency statistics
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Slowest Agent", f"{agent_data['avg_latency_ms'].max():.1f} ms")

                    with col2:
                        st.metric("Average Latency", f"{agent_data['avg_latency_ms'].mean():.1f} ms")

                    with col3:
                        st.metric("Fastest Agent", f"{agent_data['avg_latency_ms'].min():.1f} ms")

    except Exception as e:
        st.error(f"Failed to load latency comparison: {e}")

    st.divider()

    # Section 4: Token Usage by Agent
    st.subheader("Token Consumption by Agent")

    try:
        with st.spinner("Loading token usage data..."):
            agent_data = get_agent_analysis(config.db_path, date_range)

            if agent_data.empty:
                st.info("No token data available for the selected date range.")
            else:
                # Filter by selected agents if any
                if selected_agents:
                    agent_data = agent_data[agent_data["agent_name"].isin(selected_agents)]

                if agent_data.empty:
                    st.info("No data available for selected agents.")
                else:
                    # Prepare data for bar chart (rename column to match expected format)
                    bar_data = agent_data.rename(columns={"agent_name": "model_name"})

                    fig = create_model_comparison_bar(
                        bar_data, metric_column="total_tokens", title="Total Tokens by Agent"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Token statistics
                    total_tokens = agent_data["total_tokens"].sum()
                    st.metric("Total Tokens Across All Agents", f"{total_tokens:,}")

    except Exception as e:
        st.error(f"Failed to load token usage: {e}")

    # Footer
    st.divider()
    st.caption("Analyze agent-specific performance to optimize resource allocation and identify bottlenecks.")


if __name__ == "__main__":
    main()
