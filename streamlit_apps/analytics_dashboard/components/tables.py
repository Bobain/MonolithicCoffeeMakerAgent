"""
Table rendering components for Streamlit Analytics Dashboard.

This module provides reusable table components with features like sorting,
pagination, and interactive display using Streamlit.
"""

import streamlit as st
import pandas as pd


def render_sortable_table(df: pd.DataFrame, key: str = "table") -> None:
    """
    Render a sortable DataFrame using Streamlit's dataframe component.

    This function displays a DataFrame with built-in sorting capabilities,
    allowing users to click column headers to sort the data.

    Args:
        df: The pandas DataFrame to display. Can be empty or None.
        key: Unique key for the Streamlit component to maintain state.
             Must be unique across the app to avoid conflicts.

    Returns:
        None. Renders the table directly to the Streamlit app.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        >>> render_sortable_table(df, key="my_table")

        >>> # Handle empty DataFrame
        >>> empty_df = pd.DataFrame()
        >>> render_sortable_table(empty_df, key="empty_table")

    Note:
        - If DataFrame is None or empty, displays an info message
        - Uses Streamlit's native dataframe component with sorting enabled
        - The table will use full container width
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        st.info("No data available to display.")
        return

    # Create a copy to avoid modifying the original
    display_df = df.copy()

    # Display the sortable dataframe
    st.dataframe(display_df, use_container_width=True, key=key, hide_index=False)


def render_paginated_table(df: pd.DataFrame, page_size: int = 10, key: str = "paginated") -> None:
    """
    Render a paginated table with navigation controls.

    This function splits a DataFrame into pages and provides navigation
    controls (Previous/Next buttons and page selector) for browsing through
    the data. Useful for large datasets to improve performance and UX.

    Args:
        df: The pandas DataFrame to display. Can be empty or None.
        page_size: Number of rows to display per page. Must be positive.
                  Defaults to 10.
        key: Unique key for the Streamlit component to maintain state.
             Must be unique across the app to avoid conflicts.

    Returns:
        None. Renders the paginated table directly to the Streamlit app.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': range(100), 'B': range(100, 200)})
        >>> render_paginated_table(df, page_size=20, key="large_table")

        >>> # Handle small DataFrame
        >>> small_df = pd.DataFrame({'X': [1, 2, 3]})
        >>> render_paginated_table(small_df, page_size=10, key="small")

    Note:
        - If DataFrame is None or empty, displays an info message
        - Page size must be at least 1
        - Current page is stored in session state for persistence
        - Displays page information and total rows
        - Navigation controls adapt to available pages
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        st.info("No data available to display.")
        return

    # Validate page_size
    if page_size < 1:
        st.error("Page size must be at least 1.")
        return

    # Calculate total pages
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size  # Ceiling division

    # Initialize session state for current page if not exists
    page_state_key = f"{key}_current_page"
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 0

    # Ensure current page is within valid range
    current_page = st.session_state[page_state_key]
    if current_page >= total_pages:
        current_page = max(0, total_pages - 1)
        st.session_state[page_state_key] = current_page

    # Calculate slice indices
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, total_rows)

    # Display page information
    st.caption(f"Showing rows {start_idx + 1}-{end_idx} of {total_rows} " f"(Page {current_page + 1} of {total_pages})")

    # Display the current page of data
    page_df = df.iloc[start_idx:end_idx]
    st.dataframe(page_df, use_container_width=True, key=f"{key}_table_{current_page}", hide_index=False)

    # Navigation controls
    if total_pages > 1:
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

        with col1:
            # Previous button
            if st.button("← Previous", key=f"{key}_prev", disabled=(current_page == 0), use_container_width=True):
                st.session_state[page_state_key] = current_page - 1
                st.rerun()

        with col2:
            # Page selector dropdown
            page_options = [f"Page {i + 1}" for i in range(total_pages)]
            selected_page_label = st.selectbox(
                "Go to page",
                options=page_options,
                index=current_page,
                key=f"{key}_selector",
                label_visibility="collapsed",
            )
            # Extract page number from selection
            selected_page = int(selected_page_label.split()[1]) - 1
            if selected_page != current_page:
                st.session_state[page_state_key] = selected_page
                st.rerun()

        with col3:
            # Show page size info
            st.caption(f"{page_size} rows per page")

        with col4:
            # Next button
            if st.button(
                "Next →", key=f"{key}_next", disabled=(current_page >= total_pages - 1), use_container_width=True
            ):
                st.session_state[page_state_key] = current_page + 1
                st.rerun()
