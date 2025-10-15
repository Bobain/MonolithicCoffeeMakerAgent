"""Monitor tab for real-time trace visualization."""

import streamlit as st

st.title("📊 Monitor")

st.info("⏳ Coming in Phase 2: Real-time trace monitoring")

st.markdown(
    """
### Planned Features (Phase 2)

**Live Trace Feed**:
- Real-time streaming of new traces
- Color-coded status (success/failure/partial)
- Expandable details per trace
- Filters by agent, date, result status
- Search traces by prompt content

**Agent Performance Dashboard**:
- Success rate bars (visual progress)
- Trace counts (today / total)
- Average execution time
- Warnings for low success rates
- Click to drill down into specific agent

**Reflection Status**:
- Last reflection run timestamp
- Pending trace count
- Manual trigger button
- Schedule auto-reflection
- View latest delta items

### Mock Data (for preview)

Below is what the Monitor tab will look like:
"""
)

# Mock Live Trace Feed
st.subheader("Live Trace Feed (Preview)")

with st.container():
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        st.text("user_interpret")
    with col2:
        st.text("2025-10-15 14:32:15")
    with col3:
        st.success("SUCCESS")
    with col4:
        st.text("1.2s")

    st.caption('Prompt: "add a login feature"')
    st.caption("Intent: add_feature → code_developer")

st.divider()

# Mock Performance Dashboard
st.subheader("Agent Performance (Preview)")

col1, col2 = st.columns([1, 1])

with col1:
    st.metric("user_interpret", "95%", "+2%")
    st.progress(0.95)
    st.caption("127 traces today | 1,453 total | Avg: 1.2s")

with col2:
    st.metric("assistant", "89%", "+1%")
    st.progress(0.89)
    st.caption("89 traces today | 982 total | Avg: 2.8s")
