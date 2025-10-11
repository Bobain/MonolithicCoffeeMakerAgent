"""Error Monitoring Dashboard - Main Application.

This is the main entry point for the Streamlit Error Monitoring Dashboard.
It provides comprehensive error monitoring for LLM traces from Langfuse.

Usage:
    streamlit run streamlit_apps/error_monitoring_dashboard/app.py

Environment Variables:
    SQLITE_PATH: Path to SQLite database (default: llm_metrics.db)
    ERROR_DASHBOARD_TITLE: Dashboard title (default: Error Monitoring Dashboard)
    CACHE_TTL: Cache TTL in seconds (default: 300)
    ERROR_RATE_THRESHOLD: Error rate threshold for alerts (default: 0.10)
    CRITICAL_ERROR_THRESHOLD: Critical error count threshold (default: 5)

Example:
    $ cd /path/to/MonolithicCoffeeMakerAgent
    $ streamlit run streamlit_apps/error_monitoring_dashboard/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_apps.error_monitoring_dashboard.config import get_config


def main():
    """Main application entry point."""
    # Load configuration
    config = get_config()

    # Page configuration
    st.set_page_config(
        page_title=config.page_title,
        page_icon="🚨",
        layout=config.layout,
        initial_sidebar_state=config.initial_sidebar_state,
    )

    # Main page header
    st.title("🚨 Error Monitoring Dashboard")
    st.markdown("### Real-Time Error Monitoring from Langfuse Traces")

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
            "3. Verify the database file exists at the expected location\n"
            "4. Run the Langfuse exporter to populate the database"
        )
        st.code(f"Expected database path: {config.absolute_db_path}", language="bash")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Configuration Error**: {e}")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🎯 Navigation")
        st.markdown("Use the pages in the sidebar to explore different error monitoring views:")
        st.markdown(
            """
        - **📊 Error Overview**: Real-time error metrics and trends
        - **🔍 Trace Explorer**: Investigate failed traces in detail
        - **📈 Error Trends**: Temporal error analysis and patterns
        - **🤖 Model Failures**: Model-specific error analysis
        - **🔔 Alerts Config**: Configure error alerts and notifications
        """
        )

        st.divider()

        st.header("ℹ️ About")
        st.markdown(
            f"""
        **Database**: `{Path(config.sqlite_path).name}`

        **Cache TTL**: {config.cache_ttl}s

        **Error Rate Threshold**: {config.error_rate_threshold * 100:.1f}%

        **Dashboard Version**: 1.0.0
        """
        )

        st.divider()

        # Quick error stats
        try:
            from streamlit_apps.error_monitoring_dashboard.queries.error_queries import get_error_summary

            stats = get_error_summary(config.db_path)

            st.header("🚨 Quick Stats (24h)")
            st.metric("Total Errors", f"{stats['total_errors']:,}")
            st.metric("Error Rate", f"{stats['error_rate']:.2%}")
            st.metric("Critical Errors", f"{stats['critical_errors']:,}")

            # Alert indicator
            if stats["error_rate"] > config.error_rate_threshold:
                st.error(f"⚠️ Error rate above threshold!")
            elif stats["critical_errors"] > config.critical_error_threshold:
                st.warning(f"⚠️ High critical error count!")
            else:
                st.success("✅ Error levels normal")

        except Exception as e:
            st.warning(f"Could not load quick stats: {e}")

    # Home page content
    st.markdown(
        """
    ## 🚀 Getting Started

    This dashboard provides comprehensive error monitoring for LLM traces stored in your Langfuse database.
    Navigate using the sidebar to explore different views:

    ### 📊 Error Overview
    Get a high-level view of errors with real-time metrics, severity distribution, and error trends.

    ### 🔍 Trace Explorer
    Deep dive into failed traces with full context including:
    - Error messages and stack traces
    - Input prompts and model responses
    - Execution metadata (tokens, cost, latency)
    - Related events in the trace

    ### 📈 Error Trends
    Analyze error patterns over time with temporal analysis:
    - Error frequency trends
    - Error type distribution
    - Day-of-week and hour-of-day patterns
    - Model-specific error trends

    ### 🤖 Model Failures
    Compare error rates across different models:
    - Model failure rate comparison
    - Common errors per model
    - Model-specific error insights
    - Cost impact of errors

    ### 🔔 Alerts Config
    Configure alerts for proactive error monitoring:
    - High error rate alerts
    - Critical error notifications
    - Model degradation alerts
    - Custom alert rules

    ---

    ## 🎯 Key Features

    - **Real-time Monitoring**: Data updates every 5 minutes
    - **Error Classification**: Automatic categorization by severity and type
    - **Interactive Filters**: Filter by date range, model, severity, and error type
    - **Rich Visualizations**: Powered by Plotly for interactive charts
    - **Export Capabilities**: CSV and JSON report generation
    - **Alert System**: Configurable alerts for proactive monitoring
    - **Trace Context**: Full trace details for root cause analysis

    ---

    ## 📚 Documentation

    For detailed documentation, see:
    - `README.md` - User guide and installation
    - `DEVELOPMENT.md` - Developer guide (if available)

    ---

    ## 🐛 Issues?

    If you encounter any issues, please check:
    1. Database file exists and has trace data
    2. Environment variables are set correctly
    3. Dependencies are installed (`pip install -r requirements.txt`)
    4. Langfuse exporter has run successfully

    **Database Path**: `{config.absolute_db_path}`

    ---

    ## 💡 Tips

    - Use date range filters to focus on specific time periods
    - Check the Trace Explorer for detailed error context
    - Monitor Error Trends to identify patterns
    - Configure Alerts to stay informed of critical issues
    - Export error data for offline analysis
    """
    )

    # Footer
    st.divider()
    st.markdown(
        """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>Built with Streamlit • Powered by Langfuse Analytics</p>
        <p>MonolithicCoffeeMakerAgent Project • Error Monitoring Dashboard v1.0</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
