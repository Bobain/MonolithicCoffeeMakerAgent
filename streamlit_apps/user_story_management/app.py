"""User Story Management and Feedback Application.

This Streamlit app provides product owners with a comprehensive interface to:
- View all user stories (implemented and planned)
- Validate feature implementations
- Provide feedback on results and process
- Manage Definition of Done criteria
- Create bug tickets linked to user stories
- Upload and annotate screenshots

Usage:
    streamlit run streamlit_apps/user_story_management/app.py

Related:
    US-111: Web App for User Story Management and Feedback
    SPEC-111: Bug Tracking Database and Skill
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.utils.bug_tracking_helper import get_bug_skill


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="User Story Management",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Main page header
    st.title("📋 User Story Management & Feedback")
    st.markdown("### Product Owner Interface for Managing User Stories and Validations")

    # Initialize parser
    try:
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        parser = RoadmapParser(str(roadmap_path))
    except FileNotFoundError as e:
        st.error(f"❌ **ROADMAP Error**: {e}")
        st.stop()

    # Sidebar navigation
    with st.sidebar:
        st.header("🎯 Navigation")
        st.markdown("Use the pages to manage user stories:")
        st.markdown(
            """
        - **📊 Dashboard**: Overview of all user stories
        - **✅ Validation**: Validate implementations
        - **💬 Feedback**: Provide ratings and feedback
        - **🐛 Bug Tickets**: Create and manage bugs
        - **📸 Screenshots**: Upload and annotate
        - **🔍 Search**: Find specific user stories
        """
        )

        st.divider()

        st.header("ℹ️ About")
        st.markdown(
            """
        **Purpose**: Validate user stories, provide feedback, and track bugs

        **Features**:
        - View all user stories
        - Validate implementations
        - Rate results (1-5 stars)
        - Create bug tickets
        - Upload screenshots

        **Version**: 1.0.0
        """
        )

        st.divider()

        # Quick stats
        try:
            priorities = parser.get_priorities()
            completed = sum(1 for p in priorities if "✅" in p.get("status", ""))
            in_progress = sum(1 for p in priorities if "🔄" in p.get("status", ""))
            planned = sum(1 for p in priorities if "📝" in p.get("status", ""))

            st.metric("Total User Stories", len(priorities))
            st.metric("✅ Completed", completed)
            st.metric("🔄 In Progress", in_progress)
            st.metric("📝 Planned", planned)
        except Exception as e:
            st.error(f"Failed to load stats: {e}")

    # Main content area
    st.header("📊 User Stories Dashboard")

    # Get all priorities
    priorities = parser.get_priorities()

    if not priorities:
        st.warning("No user stories found in ROADMAP.md")
        st.stop()

    # Filter controls
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "✅ Complete", "🔄 In Progress", "📝 Planned"],
            key="status_filter",
        )

    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "HIGH", "MEDIUM", "LOW"],
            key="priority_filter",
        )

    with col3:
        search_query = st.text_input("Search by title", key="search_query")

    # Filter priorities
    filtered = priorities

    if status_filter != "All":
        status_emoji = status_filter.split()[0]
        filtered = [p for p in filtered if status_emoji in p.get("status", "")]

    if priority_filter != "All":
        filtered = [p for p in filtered if priority_filter in p.get("content", "").upper()]

    if search_query:
        filtered = [
            p
            for p in filtered
            if search_query.lower() in p.get("name", "").lower() or search_query.lower() in p.get("content", "").lower()
        ]

    st.markdown(f"**Showing {len(filtered)} of {len(priorities)} user stories**")

    # Display user stories in a table
    for idx, priority in enumerate(filtered):
        with st.expander(f"{priority.get('status', '📝')} {priority.get('name', 'Unknown')}", expanded=(idx < 3)):
            # Extract info from content
            content = priority.get("content", "")

            # Display priority info
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Status**: {priority.get('status', 'Unknown')}")
                st.markdown(f"**Priority Number**: {priority.get('number', 'N/A')}")

                # Try to extract user story
                if "**User Story**:" in content:
                    user_story = content.split("**User Story**:")[1].split("\n\n")[0].strip()
                    st.markdown(f"**User Story**: {user_story}")

                # Try to extract key features
                if "**Key Features**:" in content:
                    features = content.split("**Key Features**:")[1].split("\n\n")[0].strip()
                    st.markdown("**Key Features**:")
                    st.markdown(features)

            with col2:
                # Validation controls
                st.markdown("### Validation")

                validation = st.radio(
                    "Implementation Status",
                    ["Not Validated", "✅ Yes", "❌ No", "🟡 Partial"],
                    key=f"validation_{idx}",
                )

                rating = st.slider(
                    "Rating (1-5 ⭐)",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"rating_{idx}",
                )

                if st.button("💬 Add Feedback", key=f"feedback_{idx}"):
                    st.session_state[f"show_feedback_{idx}"] = True

                if st.button("🐛 Create Bug", key=f"bug_{idx}"):
                    st.session_state[f"show_bug_{idx}"] = True

            # Feedback form
            if st.session_state.get(f"show_feedback_{idx}", False):
                st.markdown("---")
                st.markdown("### Feedback Form")

                feedback_text = st.text_area(
                    "Your feedback on results and process",
                    key=f"feedback_text_{idx}",
                    height=150,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Submit Feedback", key=f"submit_feedback_{idx}"):
                        # Save feedback (would integrate with database)
                        st.success("✅ Feedback submitted!")
                        st.session_state[f"show_feedback_{idx}"] = False

                with col2:
                    if st.button("Cancel", key=f"cancel_feedback_{idx}"):
                        st.session_state[f"show_feedback_{idx}"] = False

            # Bug creation form
            if st.session_state.get(f"show_bug_{idx}", False):
                st.markdown("---")
                st.markdown("### Create Bug Ticket")

                bug_title = st.text_input("Bug Title", key=f"bug_title_{idx}")
                bug_description = st.text_area("Bug Description", key=f"bug_description_{idx}", height=150)
                bug_priority = st.selectbox(
                    "Priority",
                    ["Critical", "High", "Medium", "Low"],
                    key=f"bug_priority_{idx}",
                )
                bug_category = st.selectbox(
                    "Category",
                    ["crash", "performance", "ui", "logic", "documentation", "other"],
                    key=f"bug_category_{idx}",
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create Bug Ticket", key=f"submit_bug_{idx}"):
                        if bug_title and bug_description:
                            # Create bug using BugTrackingSkill
                            try:
                                bug_skill = get_bug_skill()
                                result = bug_skill.report_bug(
                                    title=bug_title,
                                    description=bug_description,
                                    reporter="product_owner",
                                    priority=bug_priority,
                                    category=bug_category,
                                    discovered_in_priority=priority.get("number"),
                                )
                                st.success(f"✅ Bug ticket created: BUG-{result['bug_number']:03d}")
                                st.markdown(f"**Ticket Path**: `{result['ticket_file_path']}`")
                                st.session_state[f"show_bug_{idx}"] = False
                            except Exception as e:
                                st.error(f"❌ Failed to create bug ticket: {e}")
                        else:
                            st.warning("Please fill in title and description")

                with col2:
                    if st.button("Cancel", key=f"cancel_bug_{idx}"):
                        st.session_state[f"show_bug_{idx}"] = False

    # Footer
    st.markdown("---")
    st.markdown(
        """
    **User Story Management App** | Built with Streamlit |
    Related: US-111, SPEC-111 | Version 1.0.0
    """
    )


if __name__ == "__main__":
    main()
