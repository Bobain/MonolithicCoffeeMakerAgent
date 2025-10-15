"""Streamlit ACE Configuration & Monitoring App."""

import streamlit as st

st.set_page_config(
    page_title="ACE Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 ACE Framework")
st.markdown("**A**gentic **C**ontext **E**ngineering - Configuration & Monitoring")

st.info(
    """
Welcome to the ACE Framework management interface!

Use the sidebar to navigate between:
- 📝 **Configuration**: Enable/disable ACE per agent, adjust parameters
- 📊 **Monitor**: Real-time trace visualization
- 📚 **Playbooks**: Interactive playbook management
- 📈 **Analytics**: Performance insights
"""
)

# Show current ACE status
st.subheader("Quick Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Agents", "5/6", "83%")

with col2:
    st.metric("Traces Today", "127", "+12")

with col3:
    st.metric("Success Rate", "95%", "+2%")

st.divider()

st.markdown(
    """
### Getting Started

1. **Configure Agents**: Go to the Configuration page to enable/disable ACE per agent
2. **Monitor Activity**: Check the Monitor page to see real-time trace generation
3. **Review Playbooks**: Visit the Playbooks page to inspect and curate agent learning
4. **Analyze Performance**: Use the Analytics page for performance insights

### About ACE

The **Agentic Context Engineering** framework enables AI agents to learn from their interactions and improve over time. It consists of three main components:

- **Generator**: Captures execution traces (prompts, inputs, outputs, outcomes)
- **Reflector**: Analyzes traces to extract insights and learnings
- **Curator**: Maintains playbooks (collections of learned behaviors)

This app provides a visual interface to manage and monitor the entire ACE lifecycle.
"""
)
