"""Trace Explorer Page for Error Monitoring Dashboard.

This page provides detailed trace exploration with search, filtering, and
full trace detail viewing capabilities for error investigation.
"""

import streamlit as st
import json
from datetime import datetime, timedelta

from streamlit_apps.error_monitoring_dashboard.config import get_config
from streamlit_apps.error_monitoring_dashboard.queries.trace_queries import (
    search_traces,
    get_trace_details,
    get_related_traces,
)
from streamlit_apps.error_monitoring_dashboard.queries.error_queries import (
    get_available_models_with_errors,
    get_error_by_type,
)
from streamlit_apps.error_monitoring_dashboard.components import (
    render_trace_details,
)
from streamlit_apps.error_monitoring_dashboard.utils.error_classifier import ErrorClassifier

# Page configuration
st.set_page_config(
    page_title="Trace Explorer - Error Monitoring",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = get_config()

# Page header
st.title("🔍 Trace Explorer")
st.markdown(
    """
    Search, filter, and explore error traces in detail. View complete trace context,
    error classifications, and related traces for comprehensive debugging.
    """
)

# Sidebar - Filters
st.sidebar.header("Search & Filters")

# Search box
search_query = st.sidebar.text_input(
    "🔍 Search Traces",
    placeholder="Enter trace ID or keywords...",
    help="Search by trace ID, trace name, or error message",
)

# Date range filter
st.sidebar.subheader("Date Range")
date_option = st.sidebar.selectbox(
    "Select Range",
    options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"],
    index=0,
)

if date_option == "Last 24 Hours":
    date_range = (
        datetime.now() - timedelta(hours=24),
        datetime.now(),
    )
elif date_option == "Last 7 Days":
    date_range = (
        datetime.now() - timedelta(days=7),
        datetime.now(),
    )
elif date_option == "Last 30 Days":
    date_range = (
        datetime.now() - timedelta(days=30),
        datetime.now(),
    )
else:  # Custom Range
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.sidebar.date_input(
            "Start",
            value=datetime.now().date() - timedelta(days=7),
        )
    with col2:
        end_date = st.sidebar.date_input(
            "End",
            value=datetime.now().date(),
        )

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    date_range = (start_datetime, end_datetime)

# Model filter
st.sidebar.subheader("Model Filter")
try:
    db_path = config.absolute_db_path
    available_models = get_available_models_with_errors(db_path)
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=available_models,
        index=0,
    )
except Exception as e:
    st.sidebar.error(f"Error loading models: {e}")
    selected_model = "All"

# Error type filter
st.sidebar.subheader("Error Type Filter")
try:
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

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **How to Use**

    1. Search by trace ID or keywords
    2. Apply date range and model filters
    3. Select a trace to view full details
    4. Export traces to JSON for further analysis
    """
)

# Main content
try:
    # Initialize session state for selected trace
    if "selected_trace_id" not in st.session_state:
        st.session_state.selected_trace_id = None

    # Search traces
    st.header("Trace Search Results")

    # Perform search
    traces_df = search_traces(
        db_path=db_path,
        search_query=search_query,
        date_range=date_range,
        model=selected_model if selected_model != "All" else None,
        limit=100,
    )

    # Filter by error type if selected
    if selected_error_type != "All" and not traces_df.empty:
        from streamlit_apps.error_monitoring_dashboard.queries.error_queries import get_error_traces

        error_traces = get_error_traces(db_path, limit=1000, date_range=date_range, error_type=selected_error_type)
        if not error_traces.empty:
            # Filter traces_df to only include matching trace IDs
            matching_ids = error_traces["trace_id"].unique()
            traces_df = traces_df[traces_df["id"].isin(matching_ids)]

    if not traces_df.empty:
        st.success(f"Found {len(traces_df)} matching traces")

        # Display as table
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Matching Traces")
        with col2:
            # Export option
            if st.button("📥 Export All to JSON"):
                all_traces_data = []
                for trace_id in traces_df["id"].head(50):  # Limit to 50 for export
                    trace_detail = get_trace_details(db_path, trace_id)
                    if trace_detail:
                        all_traces_data.append(trace_detail)

                st.download_button(
                    label="Download JSON",
                    data=json.dumps(all_traces_data, indent=2, default=str),
                    file_name=f"traces_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

        # Create clickable list
        display_cols = ["id", "name", "timestamp", "status_message", "model"]
        available_cols = [col for col in display_cols if col in traces_df.columns]

        display_df = traces_df[available_cols].copy()

        # Format timestamp
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Add selection column
        for idx, row in display_df.iterrows():
            col1, col2, col3, col4 = st.columns([1, 2, 3, 1])

            with col1:
                if st.button("📋 View", key=f"select_{row['id']}"):
                    st.session_state.selected_trace_id = row["id"]

            with col2:
                st.text(row["timestamp"] if "timestamp" in row else "N/A")

            with col3:
                error_msg = row.get("status_message", "No error message")
                if error_msg and len(str(error_msg)) > 60:
                    error_msg = str(error_msg)[:57] + "..."
                st.caption(f"{row.get('name', 'Unknown')} - {error_msg}")

            with col4:
                st.text(row.get("model", "Unknown"))

            st.divider()

    else:
        st.info("No traces found matching your search criteria. Try adjusting the filters.")

    # Display selected trace details
    if st.session_state.selected_trace_id:
        st.divider()
        st.header("Trace Details")

        # Get full trace details
        trace_data = get_trace_details(db_path, st.session_state.selected_trace_id)

        if trace_data:
            # Prepare trace data for rendering
            # Classify error if not already classified
            error_message = (
                trace_data.get("status_message")
                or (trace_data.get("events", [{}])[0].get("message") if trace_data.get("events") else None)
                or "Unknown error"
            )

            classification = ErrorClassifier.classify(error_message)

            # Merge classification into trace data
            trace_display_data = {
                "trace_id": trace_data.get("id"),
                "trace_name": trace_data.get("name"),
                "timestamp": trace_data.get("timestamp"),
                "error_message": error_message,
                "error_type": classification["type"],
                "severity": classification["severity"],
                "category": classification["category"],
                "recommendation": classification["recommendation"],
                "metadata": trace_data.get("metadata"),
            }

            # Add generation data if available
            if trace_data.get("generation"):
                gen = trace_data["generation"]
                trace_display_data.update(
                    {
                        "model": gen.get("model"),
                        "model_parameters": gen.get("model_parameters"),
                        "prompt_tokens": gen.get("prompt_tokens"),
                        "completion_tokens": gen.get("completion_tokens"),
                        "total_tokens": gen.get("total_tokens"),
                        "total_cost": gen.get("total_cost"),
                        "latency_ms": gen.get("latency_ms"),
                    }
                )

            # Render trace details
            render_trace_details(trace_display_data)

            # Export single trace
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.download_button(
                    label="📥 Export Trace to JSON",
                    data=json.dumps(trace_data, indent=2, default=str),
                    file_name=f"trace_{st.session_state.selected_trace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

            with col2:
                if st.button("🔄 Clear Selection"):
                    st.session_state.selected_trace_id = None
                    st.rerun()

            # Related traces section
            st.subheader("Related Traces")
            st.caption("Traces with the same name/operation")

            related_df = get_related_traces(db_path, st.session_state.selected_trace_id, limit=5)

            if not related_df.empty:
                # Format and display
                if "timestamp" in related_df.columns:
                    related_df["timestamp"] = related_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

                st.dataframe(
                    related_df[["id", "timestamp", "status_message", "model"]],
                    use_container_width=True,
                    hide_index=True,
                )

                # Add buttons to view related traces
                for trace_id in related_df["id"].head(3):
                    if st.button(f"View Trace {trace_id[:12]}...", key=f"related_{trace_id}"):
                        st.session_state.selected_trace_id = trace_id
                        st.rerun()
            else:
                st.info("No related traces found")

        else:
            st.error(f"Trace not found: {st.session_state.selected_trace_id}")
            if st.button("Clear Selection"):
                st.session_state.selected_trace_id = None
                st.rerun()

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(
        "Please ensure the Langfuse export database exists at the configured path. "
        "Run the analytics export process first."
    )
except Exception as e:
    st.error(f"❌ Error loading trace data: {e}")
    st.exception(e)
