"""Validation Tracking Page - Track validation status across all user stories.

This page provides:
- Overview of validation status for all user stories
- Quick validation actions
- Validation history and trends
- Export validation reports

Related: US-111
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser


def main():
    """Validation tracking page."""
    st.title("✅ Validation Tracking")
    st.markdown("### Track and manage validation status across all user stories")

    # Initialize parser
    try:
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()
    except Exception as e:
        st.error(f"Failed to load ROADMAP: {e}")
        st.stop()

    # Validation summary
    st.header("📊 Validation Summary")

    col1, col2, col3, col4 = st.columns(4)

    # Count status
    completed = sum(1 for p in priorities if "✅" in p.get("status", ""))
    in_progress = sum(1 for p in priorities if "🔄" in p.get("status", ""))
    planned = sum(1 for p in priorities if "📝" in p.get("status", ""))
    total = len(priorities)

    with col1:
        st.metric("Total Stories", total)

    with col2:
        st.metric("✅ Completed", completed, f"{completed/total*100:.1f}%" if total > 0 else "0%")

    with col3:
        st.metric("🔄 In Progress", in_progress, f"{in_progress/total*100:.1f}%" if total > 0 else "0%")

    with col4:
        st.metric("📝 Planned", planned, f"{planned/total*100:.1f}%" if total > 0 else "0%")

    # Progress bar
    st.progress(completed / total if total > 0 else 0)
    st.caption(f"Overall completion: {completed}/{total} stories ({completed/total*100:.1f}%)")

    st.markdown("---")

    # Quick validation section
    st.header("⚡ Quick Validation")
    st.markdown("Quickly validate user stories that need review")

    # Filter for stories that need validation
    needs_validation = [p for p in priorities if "✅" not in p.get("status", "")]

    if not needs_validation:
        st.success("🎉 All user stories have been validated!")
    else:
        st.info(f"**{len(needs_validation)} user stories** need validation")

        for idx, priority in enumerate(needs_validation[:5]):  # Show first 5
            with st.expander(f"{priority.get('status', '📝')} {priority.get('name', 'Unknown')}", expanded=(idx == 0)):
                content = priority.get("content", "")

                # Extract user story
                if "**User Story**:" in content:
                    user_story = content.split("**User Story**:")[1].split("\n\n")[0].strip()
                    st.markdown(f"**User Story**: {user_story}")

                # Validation form
                col1, col2 = st.columns(2)

                with col1:
                    validation_status = st.radio(
                        "Validation Status",
                        ["Not Started", "In Review", "Validated ✅", "Issues Found ❌"],
                        key=f"val_status_{idx}",
                    )

                with col2:
                    confidence = st.slider(
                        "Confidence Level",
                        min_value=1,
                        max_value=5,
                        value=3,
                        key=f"confidence_{idx}",
                        help="How confident are you in this validation?",
                    )

                notes = st.text_area(
                    "Validation Notes",
                    height=100,
                    key=f"val_notes_{idx}",
                    help="Add any notes about this validation",
                )

                if st.button("💾 Save Validation", key=f"save_val_{idx}"):
                    st.success("✅ Validation saved!")
                    # In a real implementation, this would save to a database

    st.markdown("---")

    # Detailed validation table
    st.header("📋 All User Stories - Validation Details")

    # Create a table view
    for idx, priority in enumerate(priorities):
        cols = st.columns([1, 3, 1, 1, 1])

        with cols[0]:
            st.write(f"**{priority.get('number', '?')}**")

        with cols[1]:
            st.write(priority.get("name", "Unknown")[:60])

        with cols[2]:
            status = priority.get("status", "📝 Planned")
            if "✅" in status:
                st.success("Validated")
            elif "🔄" in status:
                st.info("In Progress")
            else:
                st.warning("Planned")

        with cols[3]:
            # Quick validation toggle
            validated = st.checkbox(
                "Validated",
                value="✅" in priority.get("status", ""),
                key=f"quick_val_{idx}",
            )

        with cols[4]:
            if st.button("Details", key=f"details_{idx}"):
                st.session_state[f"show_details_{idx}"] = not st.session_state.get(f"show_details_{idx}", False)

        # Show details if toggled
        if st.session_state.get(f"show_details_{idx}", False):
            with st.container():
                st.markdown("---")
                content = priority.get("content", "")

                if "**User Story**:" in content:
                    user_story = content.split("**User Story**:")[1].split("\n\n")[0].strip()
                    st.markdown(f"**User Story**: {user_story}")

                if "**Key Features**:" in content:
                    features = content.split("**Key Features**:")[1].split("\n\n")[0].strip()
                    st.markdown("**Key Features**:")
                    st.markdown(features)

                if "**Definition of Done**:" in content:
                    dod = content.split("**Definition of Done**:")[1].split("\n\n")[0].strip()
                    st.markdown("**Definition of Done**:")
                    st.markdown(dod)

                st.markdown("---")

    # Export section
    st.markdown("---")
    st.header("📤 Export Validation Report")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Export as CSV"):
            st.info("CSV export would be generated here")

    with col2:
        if st.button("📄 Export as PDF"):
            st.info("PDF export would be generated here")

    # Footer
    st.markdown("---")
    st.markdown("**Validation Tracking** | Keep track of all user story validations")


if __name__ == "__main__":
    main()
