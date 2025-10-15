"""Playbook tab for interactive playbook management."""

import streamlit as st

st.title("📚 Playbooks")

st.info("⏳ Coming in Phase 3: Interactive playbook management")

st.markdown(
    """
### Planned Features (Phase 3)

**Playbook Browser**:
- Dropdown to select agent playbook
- Collapsible categories with bullet counts
- Expandable bullets showing helpfulness scores
- Visual effectiveness rating (stars)
- Manual curation trigger
- Export playbook to JSON
- Import playbook from JSON

**Bullet Detail View**:
- View full bullet content
- Show confidence and helpfulness scores
- Link to source traces that generated this bullet
- Show similar bullets (potential duplicates)
- Manual curation actions (mark helpful/unhelpful)
- Edit bullet content
- Delete bullet

**Curation Queue**:
- Show pending bullets from latest reflection
- Quick approve/reject buttons
- Edit before approving
- Batch actions (approve all, reject all)
- Sort by confidence, agent, or date

### Mock Playbook (for preview)

Below is what the Playbook tab will look like:
"""
)

# Mock Playbook Browser
st.subheader("Agent Playbooks (Preview)")

selected_agent = st.selectbox(
    "Select Agent",
    [
        "user_interpret",
        "assistant",
        "code_searcher",
        "code_developer",
        "project_manager",
    ],
)

st.markdown(f"**Playbook**: {selected_agent}")
st.caption("Last Updated: 2025-10-15 14:00:00")
st.caption("Size: 147 bullets (out of 150 max)")

col1, col2 = st.columns([3, 1])
with col1:
    st.caption("Effectiveness: 0.82")
with col2:
    st.text("⭐⭐⭐⭐")

st.divider()

# Mock Categories
with st.expander("🎯 Intent Interpretation (42 bullets)"):
    st.markdown('When user says "implement" → add_feature')
    st.caption("Helpful: 25 | Unhelpful: 2 | Confidence: 0.9")
    st.caption("...")

with st.expander("💭 Sentiment Analysis (38 bullets)"):
    st.markdown("Detect frustration from repeated issues")
    st.caption("Helpful: 14 | Unhelpful: 0 | Confidence: 0.95")
    st.caption("...")

with st.expander("🤝 Agent Delegation (35 bullets)"):
    st.markdown("delegate to code_developer for features")
    st.caption("Helpful: 32 | Unhelpful: 3 | Confidence: 0.85")
    st.caption("...")
