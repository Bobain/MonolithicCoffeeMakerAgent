"""LLM Analytics Dashboard - Main Application.

This is the main entry point for the Streamlit Analytics Dashboard.
It provides comprehensive analytics for LLM usage, costs, and performance.

Usage:
    streamlit run streamlit_apps/analytics_dashboard/app.py

Environment Variables:
    SQLITE_PATH: Path to SQLite database (default: llm_metrics.db)
    DASHBOARD_TITLE: Dashboard title (default: LLM Analytics Dashboard)
    CACHE_TTL: Cache TTL in seconds (default: 300)

Example:
    $ cd /path/to/MonolithicCoffeeMakerAgent
    $ streamlit run streamlit_apps/analytics_dashboard/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_apps.analytics_dashboard.config import get_config


def main():
    """Main application entry point."""
    # Load configuration
    config = get_config()

    # Page configuration
    st.set_page_config(
        page_title=config.page_title,
        page_icon="📊",
        layout=config.layout,
        initial_sidebar_state=config.initial_sidebar_state,
    )

    # Main page header
    st.title("📊 LLM Analytics Dashboard")
    st.markdown("### Welcome to the Analytics Dashboard")

    # Validate database exists
    try:
        config.validate()
    except FileNotFoundError as e:
        st.error(f"❌ **Database Error**")
        st.error(str(e))
        st.info(
            "**Quick Fix:**\n"
            "1. Ensure the analytics export has been run\n"
            "2. Check the SQLITE_PATH environment variable\n"
            "3. Verify the database file exists at the expected location"
        )
        st.code(f"Expected database path: {config.absolute_db_path}", language="bash")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Configuration Error**: {e}")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🎯 Navigation")
        st.markdown("Use the pages in the sidebar to explore different analytics views:")
        st.markdown(
            """
        - **📈 Overview**: Global metrics and trends
        - **💰 Cost Analysis**: Detailed cost breakdown
        - **🔍 Model Comparison**: Compare model performance
        - **🤖 Agent Performance**: Agent-specific analytics
        - **📥 Exports**: Download reports and data
        """
        )

        st.divider()

        st.header("ℹ️ About")
        st.markdown(
            f"""
        **Database**: `{Path(config.sqlite_path).name}`

        **Cache TTL**: {config.cache_ttl}s

        **Dashboard Version**: 1.0.0
        """
        )

        st.divider()

        # Database stats
        try:
            from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_quick_stats

            stats = get_quick_stats(config.db_path)

            st.header("📊 Quick Stats")
            st.metric("Total Cost", f"${stats['total_cost']:.2f}")
            st.metric("Total Requests", f"{stats['total_requests']:,}")
            st.metric("Total Tokens", f"{stats['total_tokens']:,}")

        except Exception as e:
            st.warning(f"Could not load quick stats: {e}")

    # Home page content
    st.markdown(
        """
    ## 🚀 Getting Started

    This dashboard provides comprehensive analytics for LLM usage across your system.
    Navigate using the sidebar to explore different views:

    ### 📈 Overview
    Get a high-level view of your LLM usage with global metrics, cost trends, and token usage.

    ### 💰 Cost Analysis
    Dive deep into cost breakdowns by model, time, and agent. Track budget and forecast spending.

    ### 🔍 Model Comparison
    Compare performance metrics across different LLM models to optimize your selection.

    ### 🤖 Agent Performance
    Analyze agent-specific performance, costs, and usage patterns.

    ### 📥 Exports
    Download detailed reports in CSV or PDF format for offline analysis.

    ---

    ## 🎯 Key Features

    - **Real-time Analytics**: Data updates every 5 minutes
    - **Interactive Filters**: Filter by date range, model, and agent
    - **Rich Visualizations**: Powered by Plotly for interactive charts
    - **Export Capabilities**: CSV and PDF report generation
    - **Performance Optimized**: Cached queries for fast loading

    ---

    ## 📚 Documentation

    For detailed documentation, see:
    - `README.md` - User guide and installation
    - `DEVELOPMENT.md` - Developer guide

    ---

    ## 🐛 Issues?

    If you encounter any issues, please check:
    1. Database file exists and has data
    2. Environment variables are set correctly
    3. Dependencies are installed (`pip install -r requirements.txt`)

    **Database Path**: `{config.absolute_db_path}`
    """
    )

    # Footer
    st.divider()
    st.markdown(
        """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>Built with Streamlit • Powered by Langfuse Analytics</p>
        <p>MonolithicCoffeeMakerAgent Project</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
