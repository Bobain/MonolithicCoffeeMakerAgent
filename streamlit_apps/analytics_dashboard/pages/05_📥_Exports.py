"""Exports Page - LLM Analytics Dashboard.

This page provides data export capabilities for downloading
detailed reports and summaries in CSV format.

Usage:
    Navigate to this page via the sidebar in the multi-page Streamlit app.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import io

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_apps.analytics_dashboard.config import get_config
from streamlit_apps.analytics_dashboard.components.tables import render_sortable_table
from streamlit_apps.analytics_dashboard.queries.export_queries import (
    get_detailed_export_data,
    get_summary_export_data,
)


def main():
    """Main function for the Exports page."""
    # Page configuration
    st.title("📥 Exports")
    st.markdown("### Download Analytics Reports and Data")

    # Load configuration
    try:
        config = get_config()
        config.validate()
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.stop()

    st.divider()

    # Section 1: Date Range Selector
    st.subheader("Select Export Date Range")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="export_start_date")

    with col2:
        end_date = st.date_input("End Date", value=datetime.now(), key="export_end_date")

    # Validate date range
    if start_date > end_date:
        st.error("Error: Start date must be before end date.")
        st.stop()

    date_range = (start_date, end_date)
    st.caption(f"Exporting data from {start_date} to {end_date}")

    st.divider()

    # Section 2: Export Options
    st.subheader("Export Options")

    col1, col2 = st.columns(2)

    # Detailed CSV Export
    with col1:
        st.markdown("#### Detailed Export")
        st.caption(
            "Exports all individual API requests with full details including "
            "timestamps, models, agents, tokens, costs, and latency."
        )

        if st.button("📊 Generate Detailed Export", use_container_width=True):
            try:
                with st.spinner("Generating detailed export..."):
                    export_data = get_detailed_export_data(config.db_path, date_range)

                    if export_data.empty:
                        st.warning("No data available for the selected date range.")
                    else:
                        # Convert to CSV
                        csv_buffer = io.StringIO()
                        export_data.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        # Create filename with timestamp
                        filename = (
                            f"llm_analytics_detailed_"
                            f"{start_date.strftime('%Y%m%d')}_"
                            f"{end_date.strftime('%Y%m%d')}.csv"
                        )

                        # Download button
                        st.download_button(
                            label="⬇️ Download Detailed CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            use_container_width=True,
                        )

                        st.success(f"✅ Generated {len(export_data):,} records for download")

            except Exception as e:
                st.error(f"Failed to generate detailed export: {e}")

    # Summary CSV Export
    with col2:
        st.markdown("#### Summary Export")
        st.caption(
            "Exports aggregated summary statistics by model, agent, and time period. "
            "Includes totals, averages, and key metrics."
        )

        if st.button("📈 Generate Summary Export", use_container_width=True):
            try:
                with st.spinner("Generating summary export..."):
                    summary_data = get_summary_export_data(config.db_path, date_range)

                    if summary_data.empty:
                        st.warning("No data available for the selected date range.")
                    else:
                        # Convert to CSV
                        csv_buffer = io.StringIO()
                        summary_data.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        # Create filename with timestamp
                        filename = (
                            f"llm_analytics_summary_"
                            f"{start_date.strftime('%Y%m%d')}_"
                            f"{end_date.strftime('%Y%m%d')}.csv"
                        )

                        # Download button
                        st.download_button(
                            label="⬇️ Download Summary CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            use_container_width=True,
                        )

                        st.success(f"✅ Generated {len(summary_data):,} summary records for download")

            except Exception as e:
                st.error(f"Failed to generate summary export: {e}")

    st.divider()

    # Section 3: Export Preview
    st.subheader("Export Preview")

    preview_type = st.radio("Select export type to preview:", ["Detailed Export", "Summary Export"], horizontal=True)

    try:
        with st.spinner("Loading preview..."):
            if preview_type == "Detailed Export":
                preview_data = get_detailed_export_data(config.db_path, date_range, limit=100)

                if preview_data.empty:
                    st.info("No detailed data available for preview.")
                else:
                    st.caption(f"Showing first 100 records (Total: {len(preview_data):,})")
                    render_sortable_table(preview_data, title="Detailed Export Preview")

            else:  # Summary Export
                preview_data = get_summary_export_data(config.db_path, date_range)

                if preview_data.empty:
                    st.info("No summary data available for preview.")
                else:
                    st.caption(f"Showing all summary records: {len(preview_data):,}")
                    render_sortable_table(preview_data, title="Summary Export Preview")

    except Exception as e:
        st.error(f"Failed to load preview: {e}")

    st.divider()

    # Section 4: Export Information
    st.subheader("Export Information")

    with st.expander("📖 Export Format Details", expanded=False):
        st.markdown(
            """
        #### Detailed Export Columns
        - `timestamp`: Request timestamp
        - `model_name`: LLM model used
        - `agent_name`: Agent that made the request
        - `prompt_tokens`: Input tokens
        - `completion_tokens`: Output tokens
        - `total_tokens`: Total tokens (prompt + completion)
        - `cost`: Total cost in USD
        - `latency_ms`: Request latency in milliseconds
        - `status`: Request status (success/error)
        - `trace_id`: Unique trace identifier

        #### Summary Export Columns
        - `model_name` or `agent_name`: Grouping dimension
        - `date`: Date of aggregation
        - `request_count`: Total number of requests
        - `total_cost`: Total cost in USD
        - `total_tokens`: Total tokens consumed
        - `avg_latency_ms`: Average latency in milliseconds
        - `success_rate`: Percentage of successful requests
        - `error_count`: Number of failed requests
        """
        )

    with st.expander("💡 Usage Tips", expanded=False):
        st.markdown(
            """
        **Best Practices:**
        - Use **Detailed Export** for deep analysis and debugging
        - Use **Summary Export** for executive reports and trends
        - Export regularly to maintain historical records
        - Smaller date ranges export faster

        **File Naming:**
        - Files are automatically named with date range
        - Format: `llm_analytics_{type}_{start_date}_{end_date}.csv`

        **Data Freshness:**
        - Exports reflect real-time database state
        - No caching applied to export queries
        """
        )

    # Footer
    st.divider()
    st.caption("Exported data can be imported into Excel, Google Sheets, or analysis tools like Python/R.")


if __name__ == "__main__":
    main()
