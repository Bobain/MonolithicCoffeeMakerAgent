"""Bug Tickets Management Page - View and create bug tickets.

This page provides:
- View all bug tickets from the database
- Create new bug tickets linked to user stories
- Filter and search bugs
- View bug analytics and statistics

Related: US-111, SPEC-111
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.utils.bug_tracking_helper import get_bug_skill


def main():
    """Bug tickets management page."""
    st.title("🐛 Bug Tickets Management")
    st.markdown("### View, create, and manage bug tickets linked to user stories")

    # Initialize bug skill
    try:
        bug_skill = get_bug_skill()
    except Exception as e:
        st.error(f"Failed to initialize bug tracking: {e}")
        st.stop()

    # Initialize roadmap parser
    try:
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()
    except Exception as e:
        st.error(f"Failed to load ROADMAP: {e}")
        priorities = []

    # Bug summary
    st.header("📊 Bug Summary")

    try:
        summary = bug_skill.get_open_bugs_summary()
        total_open = sum(summary.values())

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Open", total_open)

        with col2:
            st.metric("🚨 Critical", summary.get("critical", 0))

        with col3:
            st.metric("⚠️ High", summary.get("high", 0))

        with col4:
            st.metric("🔸 Medium", summary.get("medium", 0))

        with col5:
            st.metric("🔹 Low", summary.get("low", 0))

    except Exception as e:
        st.error(f"Failed to load bug summary: {e}")

    st.markdown("---")

    # Create new bug ticket section
    st.header("➕ Create New Bug Ticket")

    with st.expander("Create Bug Ticket", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            bug_title = st.text_input("Bug Title", key="new_bug_title")

            bug_priority = st.selectbox(
                "Priority",
                ["Critical", "High", "Medium", "Low"],
                key="new_bug_priority",
                help="Auto-assessed based on description if not specified",
            )

            bug_category = st.selectbox(
                "Category",
                ["crash", "performance", "ui", "logic", "documentation", "security", "other"],
                key="new_bug_category",
            )

        with col2:
            # Link to user story
            priority_options = ["None"] + [f"{p.get('number', '?')} - {p.get('name', 'Unknown')}" for p in priorities]
            linked_priority = st.selectbox(
                "Link to User Story",
                priority_options,
                key="new_bug_priority_link",
            )

            bug_reporter = st.text_input("Reporter", value="product_owner", key="new_bug_reporter")

        bug_description = st.text_area(
            "Bug Description",
            height=150,
            key="new_bug_description",
            help="Detailed description of the bug",
        )

        # Reproduction steps
        st.markdown("**Reproduction Steps** (Optional)")
        repro_steps = []
        for i in range(3):
            step = st.text_input(f"Step {i+1}", key=f"repro_step_{i}")
            if step:
                repro_steps.append(step)

        # Create button
        if st.button("🐛 Create Bug Ticket", type="primary"):
            if not bug_title or not bug_description:
                st.error("❌ Please provide both title and description")
            else:
                try:
                    # Extract priority number if linked
                    discovered_in_priority = None
                    if linked_priority != "None":
                        discovered_in_priority = int(linked_priority.split(" - ")[0])

                    # Create bug
                    result = bug_skill.report_bug(
                        title=bug_title,
                        description=bug_description,
                        reporter=bug_reporter,
                        priority=bug_priority,
                        category=bug_category,
                        reproduction_steps=repro_steps if repro_steps else None,
                        discovered_in_priority=discovered_in_priority,
                    )

                    st.success(f"✅ Bug ticket created: BUG-{result['bug_number']:03d}")
                    st.markdown(f"**Ticket Path**: `{result['ticket_file_path']}`")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Failed to create bug ticket: {e}")

    st.markdown("---")

    # View existing bugs
    st.header("📋 Existing Bug Tickets")

    # Filter controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "open", "analyzing", "in_progress", "testing", "resolved", "closed"],
            key="bug_status_filter",
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "Critical", "High", "Medium", "Low"],
            key="bug_priority_filter",
        )

    with col3:
        category_filter = st.selectbox(
            "Category",
            ["All", "crash", "performance", "ui", "logic", "documentation", "security", "other"],
            key="bug_category_filter",
        )

    with col4:
        limit = st.number_input("Show", min_value=10, max_value=200, value=50, step=10)

    # Query bugs
    try:
        bugs = bug_skill.query_bugs(
            status=status_filter if status_filter != "All" else None,
            priority=priority_filter if priority_filter != "All" else None,
            category=category_filter if category_filter != "All" else None,
            limit=limit,
        )

        if not bugs:
            st.info("No bugs found matching the filters")
        else:
            st.markdown(f"**Showing {len(bugs)} bug(s)**")

            # Display bugs in table format
            for bug in bugs:
                status_emoji = {
                    "open": "🔴",
                    "analyzing": "🔍",
                    "in_progress": "🟡",
                    "testing": "🧪",
                    "resolved": "✅",
                    "closed": "⚫",
                }.get(bug.get("status", "open"), "🔴")

                priority_emoji = {
                    "Critical": "🚨",
                    "High": "⚠️",
                    "Medium": "🔸",
                    "Low": "🔹",
                }.get(bug.get("priority", "Medium"), "🔸")

                with st.expander(
                    f"{status_emoji} BUG-{bug['bug_number']:03d}: {bug['title']} [{priority_emoji} {bug['priority']}]"
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Description**: {bug['description']}")

                        if bug.get("reproduction_steps"):
                            st.markdown("**Reproduction Steps**:")
                            try:
                                import json

                                steps = json.loads(bug["reproduction_steps"])
                                for i, step in enumerate(steps, 1):
                                    st.markdown(f"{i}. {step}")
                            except:
                                st.markdown(bug["reproduction_steps"])

                        if bug.get("root_cause"):
                            st.markdown(f"**Root Cause**: {bug['root_cause']}")

                        if bug.get("fix_description"):
                            st.markdown(f"**Fix**: {bug['fix_description']}")

                    with col2:
                        st.markdown(f"**Status**: {status_emoji} {bug['status']}")
                        st.markdown(f"**Priority**: {priority_emoji} {bug['priority']}")
                        st.markdown(f"**Category**: {bug.get('category', 'N/A')}")
                        st.markdown(f"**Reporter**: {bug.get('reporter', 'N/A')}")
                        st.markdown(f"**Assigned**: {bug.get('assigned_to', 'N/A')}")
                        st.markdown(f"**Created**: {bug.get('created_at', 'N/A')[:10]}")

                        if bug.get("pr_url"):
                            st.markdown(f"**PR**: [{bug['pr_url']}]({bug['pr_url']})")

                        if bug.get("ticket_file_path"):
                            st.markdown(f"**Ticket**: `{bug['ticket_file_path']}`")

                    # Update status button
                    new_status = st.selectbox(
                        "Update Status",
                        ["open", "analyzing", "in_progress", "testing", "resolved", "closed"],
                        index=[
                            "open",
                            "analyzing",
                            "in_progress",
                            "testing",
                            "resolved",
                            "closed",
                        ].index(bug.get("status", "open")),
                        key=f"status_update_{bug['bug_id']}",
                    )

                    if st.button("Update Status", key=f"update_btn_{bug['bug_id']}"):
                        try:
                            bug_skill.update_bug_status(bug_number=bug["bug_number"], status=new_status)
                            st.success(f"✅ Bug status updated to: {new_status}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update status: {e}")

    except Exception as e:
        st.error(f"Failed to load bugs: {e}")

    # Bug analytics
    st.markdown("---")
    st.header("📈 Bug Analytics")

    try:
        velocity = bug_skill.get_bug_resolution_velocity()

        if velocity:
            st.markdown("### Bug Resolution Velocity (by month)")

            # Create a simple table
            for row in velocity[:6]:  # Show last 6 months
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Month", row.get("month", "N/A"))
                with col2:
                    st.metric("Total", row.get("total_bugs", 0))
                with col3:
                    st.metric("Resolved", row.get("resolved", 0))
                with col4:
                    st.metric("Open", row.get("open", 0))
        else:
            st.info("No bug analytics data available yet")

    except Exception as e:
        st.error(f"Failed to load analytics: {e}")

    # Footer
    st.markdown("---")
    st.markdown("**Bug Tickets Management** | Track and manage bugs efficiently")


if __name__ == "__main__":
    main()
