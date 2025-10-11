"""
Filter components for the Analytics Dashboard.

This module provides functions to render and manage global filters
in the sidebar for data filtering and selection.
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime, timedelta


def render_global_filters(available_models: List[str], available_agents: List[str]) -> Dict[str, Any]:
    """
    Render global filter controls in the sidebar and return selected values.

    Args:
        available_models: List of available model names to choose from
        available_agents: List of available agent names to choose from

    Returns:
        Dictionary containing all selected filter values:
            - date_range (tuple): Start and end dates
            - models (list): Selected model names
            - agents (list): Selected agent names
            - status (str): Selected status filter
            - time_granularity (str): Selected time grouping

    Example:
        >>> filters = render_global_filters(
        ...     available_models=["gpt-4", "gpt-3.5-turbo", "claude-3"],
        ...     available_agents=["CodeAgent", "AnalysisAgent", "TestAgent"]
        ... )
        >>> print(filters)
        {
            'date_range': (datetime(2025, 10, 1), datetime(2025, 10, 11)),
            'models': ['gpt-4', 'claude-3'],
            'agents': ['CodeAgent'],
            'status': 'all',
            'time_granularity': 'day'
        }

    Notes:
        - All filter selections are stored in st.session_state
        - Filters are rendered in collapsible sections for better UX
        - Default date range is last 30 days
        - Filters persist across page reloads via session state
    """
    st.sidebar.header("Filters")

    # Initialize session state for filters if not exists
    _initialize_filter_state()

    # Date Range Filter
    with st.sidebar.expander("Date Range", expanded=True):
        default_start = datetime.now() - timedelta(days=30)
        default_end = datetime.now()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", value=st.session_state.get("filter_start_date", default_start), key="filter_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date", value=st.session_state.get("filter_end_date", default_end), key="filter_end_date"
            )

        date_range = (start_date, end_date)

    # Model Filter
    with st.sidebar.expander("Models", expanded=True):
        selected_models = st.multiselect(
            "Select Models",
            options=available_models,
            default=st.session_state.get("filter_models", []),
            key="filter_models",
            help="Leave empty to include all models",
        )

    # Agent Filter
    with st.sidebar.expander("Agents", expanded=True):
        selected_agents = st.multiselect(
            "Select Agents",
            options=available_agents,
            default=st.session_state.get("filter_agents", []),
            key="filter_agents",
            help="Leave empty to include all agents",
        )

    # Status Filter
    with st.sidebar.expander("Status", expanded=False):
        status_options = ["all", "success", "error", "timeout", "pending"]
        selected_status = st.selectbox(
            "Request Status",
            options=status_options,
            index=status_options.index(st.session_state.get("filter_status", "all")),
            key="filter_status",
        )

    # Time Granularity Filter
    with st.sidebar.expander("Time Granularity", expanded=False):
        granularity_options = ["hour", "day", "week", "month"]
        selected_granularity = st.selectbox(
            "Group By",
            options=granularity_options,
            index=granularity_options.index(st.session_state.get("filter_granularity", "day")),
            key="filter_granularity",
            help="Time interval for grouping data",
        )

    # Reset Filters Button
    st.sidebar.divider()
    if st.sidebar.button("Reset All Filters", use_container_width=True):
        _reset_filters()
        st.rerun()

    # Return filter values
    return {
        "date_range": date_range,
        "models": selected_models,
        "agents": selected_agents,
        "status": selected_status,
        "time_granularity": selected_granularity,
    }


def get_active_filters() -> Dict[str, Any]:
    """
    Retrieve current filter selections from session state.

    Returns:
        Dictionary containing all active filter values:
            - date_range (tuple): Start and end dates
            - models (list): Selected model names
            - agents (list): Selected agent names
            - status (str): Selected status filter
            - time_granularity (str): Selected time grouping

    Example:
        >>> filters = get_active_filters()
        >>> print(filters['models'])
        ['gpt-4', 'claude-3']
        >>> print(filters['date_range'])
        (datetime(2025, 10, 1), datetime(2025, 10, 11))

    Notes:
        - Returns default values if session state is not initialized
        - Should be called after render_global_filters() in the app flow
        - Useful for accessing filters in different pages/components
    """
    _initialize_filter_state()

    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()

    return {
        "date_range": (
            st.session_state.get("filter_start_date", default_start),
            st.session_state.get("filter_end_date", default_end),
        ),
        "models": st.session_state.get("filter_models", []),
        "agents": st.session_state.get("filter_agents", []),
        "status": st.session_state.get("filter_status", "all"),
        "time_granularity": st.session_state.get("filter_granularity", "day"),
    }


def _initialize_filter_state() -> None:
    """
    Initialize filter values in session state if they don't exist.

    This function ensures all filter keys are present in session state
    with appropriate default values.

    Example:
        >>> _initialize_filter_state()
        # Sets up session state with default filter values
    """
    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()

    if "filter_start_date" not in st.session_state:
        st.session_state.filter_start_date = default_start

    if "filter_end_date" not in st.session_state:
        st.session_state.filter_end_date = default_end

    if "filter_models" not in st.session_state:
        st.session_state.filter_models = []

    if "filter_agents" not in st.session_state:
        st.session_state.filter_agents = []

    if "filter_status" not in st.session_state:
        st.session_state.filter_status = "all"

    if "filter_granularity" not in st.session_state:
        st.session_state.filter_granularity = "day"


def _reset_filters() -> None:
    """
    Reset all filters to their default values.

    This function clears all filter selections from session state,
    effectively resetting the dashboard to its initial state.

    Example:
        >>> _reset_filters()
        # All filters are reset to defaults
    """
    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()

    st.session_state.filter_start_date = default_start
    st.session_state.filter_end_date = default_end
    st.session_state.filter_models = []
    st.session_state.filter_agents = []
    st.session_state.filter_status = "all"
    st.session_state.filter_granularity = "day"


def render_quick_filters() -> None:
    """
    Render quick filter buttons for common date range selections.

    Provides convenient buttons for selecting common time ranges like
    "Last 24 Hours", "Last 7 Days", "Last 30 Days", etc.

    Example:
        >>> render_quick_filters()
        # Renders buttons: [24h] [7d] [30d] [90d] [All Time]

    Notes:
        - Updates the date range in session state when clicked
        - Triggers a rerun to refresh the dashboard
        - Should be called in the sidebar after render_global_filters()
    """
    st.sidebar.subheader("Quick Filters")

    col1, col2, col3 = st.sidebar.columns(3)

    with col1:
        if st.button("24h", use_container_width=True):
            st.session_state.filter_start_date = datetime.now() - timedelta(days=1)
            st.session_state.filter_end_date = datetime.now()
            st.rerun()

    with col2:
        if st.button("7d", use_container_width=True):
            st.session_state.filter_start_date = datetime.now() - timedelta(days=7)
            st.session_state.filter_end_date = datetime.now()
            st.rerun()

    with col3:
        if st.button("30d", use_container_width=True):
            st.session_state.filter_start_date = datetime.now() - timedelta(days=30)
            st.session_state.filter_end_date = datetime.now()
            st.rerun()

    col4, col5 = st.sidebar.columns(2)

    with col4:
        if st.button("90d", use_container_width=True):
            st.session_state.filter_start_date = datetime.now() - timedelta(days=90)
            st.session_state.filter_end_date = datetime.now()
            st.rerun()

    with col5:
        if st.button("All Time", use_container_width=True):
            st.session_state.filter_start_date = datetime(2020, 1, 1)
            st.session_state.filter_end_date = datetime.now()
            st.rerun()


def get_filter_summary() -> str:
    """
    Generate a human-readable summary of active filters.

    Returns:
        String describing the currently active filters

    Example:
        >>> summary = get_filter_summary()
        >>> print(summary)
        'Showing data from 2025-10-01 to 2025-10-11 for models: gpt-4, claude-3'

    Notes:
        - Returns "No filters applied" if all filters are at defaults
        - Useful for displaying filter context in the main dashboard
    """
    filters = get_active_filters()

    parts = []

    # Date range
    start, end = filters["date_range"]
    if isinstance(start, datetime):
        start_str = start.strftime("%Y-%m-%d")
    else:
        start_str = str(start)

    if isinstance(end, datetime):
        end_str = end.strftime("%Y-%m-%d")
    else:
        end_str = str(end)

    parts.append(f"from {start_str} to {end_str}")

    # Models
    if filters["models"]:
        models_str = ", ".join(filters["models"])
        parts.append(f"models: {models_str}")

    # Agents
    if filters["agents"]:
        agents_str = ", ".join(filters["agents"])
        parts.append(f"agents: {agents_str}")

    # Status
    if filters["status"] != "all":
        parts.append(f"status: {filters['status']}")

    if len(parts) == 1:  # Only date range
        return f"Showing all data {parts[0]}"
    else:
        return f"Showing data {' | '.join(parts)}"
