"""Configuration tab for ACE settings."""

import streamlit as st
from coffee_maker.streamlit_app.utils.env_manager import EnvManager
from coffee_maker.streamlit_app.components.agent_toggle import render_agent_toggle

st.title("📝 ACE Configuration")

# Initialize env manager
env_manager = EnvManager()

# Agent configurations
AGENT_CONFIGS = {
    "user_interpret": {
        "description": "Fast operations, high volume, immediate feedback",
        "traces_today": 127,
        "traces_total": 1453,
        "recommended": True,
    },
    "assistant": {
        "description": "Good volume, quick feedback loop",
        "traces_today": 89,
        "traces_total": 982,
        "recommended": True,
    },
    "code_searcher": {
        "description": "Moderate volume, clear success metrics",
        "traces_today": 34,
        "traces_total": 401,
        "recommended": True,
    },
    "code_developer": {
        "description": "Slow operations (opt-out during dev)",
        "traces_today": 0,
        "traces_total": 15,
        "recommended": False,
    },
    "user_listener": {
        "description": "UI only (no learning needed)",
        "traces_today": 0,
        "traces_total": 0,
        "recommended": False,
    },
    "project_manager": {
        "description": "Strategic decisions benefit from learning",
        "traces_today": 12,
        "traces_total": 156,
        "recommended": True,
    },
}

# Get current statuses
agent_statuses = env_manager.get_all_agent_statuses()


# Toggle callback
def handle_toggle(agent_name: str, new_status: bool):
    """Handle agent toggle."""
    success = env_manager.set_agent_ace_status(agent_name, new_status)
    if success:
        action = "enabled" if new_status else "disabled"
        st.success(f"ACE {action} for {agent_name}")
    else:
        st.error(f"Failed to update {agent_name}")


# Render toggles
st.subheader("Agent ACE Toggles")
st.markdown("**Default**: ACE is enabled for all agents (opt-out)")

for agent_name, agent_config in AGENT_CONFIGS.items():
    with st.container():
        ace_enabled = agent_statuses.get(agent_name, True)
        render_agent_toggle(agent_name, agent_config, ace_enabled, handle_toggle)
        st.divider()

# Parameters section (stub for now)
st.subheader("ACE Configuration Parameters")
st.info("⏳ Parameter configuration coming in Phase 2")

st.markdown(
    """
### Future Parameters

The following ACE parameters will be configurable in Phase 2:

- **Trace Directory**: Where to store execution traces
- **Delta Directory**: Where to store reflection deltas
- **Playbook Directory**: Where to store curated playbooks
- **Similarity Threshold**: For detecting duplicate bullets (0-1)
- **Pruning Rate**: How aggressively to prune low-value bullets (0-1)
- **Max Bullets**: Maximum playbook size (50-300)
- **Auto-Reflect**: Enable automatic reflection after N traces
- **Auto-Curate**: Enable automatic curation after reflection
"""
)
