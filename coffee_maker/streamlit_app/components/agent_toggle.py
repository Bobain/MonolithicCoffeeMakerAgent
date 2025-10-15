"""Reusable agent toggle component."""

import streamlit as st
from typing import Dict, Any, Callable


def render_agent_toggle(
    agent_name: str,
    agent_config: Dict[str, Any],
    ace_enabled: bool,
    on_toggle: Callable,
):
    """Render agent toggle with status.

    Args:
        agent_name: Agent name (e.g., 'user_interpret')
        agent_config: Agent configuration (description, trace counts, etc.)
        ace_enabled: Current ACE status
        on_toggle: Callback when toggle changed (agent_name, new_status)
    """
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        # Agent name and description
        st.markdown(f"**{agent_name.replace('_', ' ').title()}**")
        st.caption(agent_config.get("description", ""))

        # Trace counts
        traces_today = agent_config.get("traces_today", 0)
        traces_total = agent_config.get("traces_total", 0)
        st.caption(f"Traces: {traces_today} today, {traces_total} total")

    with col2:
        # Status indicator
        if ace_enabled:
            st.success("ENABLED")
        else:
            st.error("DISABLED")

    with col3:
        # Toggle button
        button_label = "Disable" if ace_enabled else "Enable"
        button_type = "secondary" if ace_enabled else "primary"

        if st.button(button_label, key=f"toggle_{agent_name}", type=button_type):
            on_toggle(agent_name, not ace_enabled)
            st.rerun()
