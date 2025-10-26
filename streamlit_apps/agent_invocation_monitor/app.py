"""Claude Agent Invocation Monitor Dashboard.

This Streamlit app provides real-time monitoring of Claude agent invocations,
including streaming progress, historical analysis, and debugging tools.

Features:
- Real-time streaming progress visualization
- Invocation history with filtering
- Token usage and cost tracking
- Streaming message timeline
- Performance metrics

Usage:
    streamlit run streamlit_apps/agent_invocation_monitor/app.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# Add project root to path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coffee_maker.claude_agent_invoker import ClaudeInvocationDB

# Page config
st.set_page_config(page_title="Claude Agent Monitor", page_icon="🤖", layout="wide")


# Initialize database
@st.cache_resource
def get_db():
    """Get database connection."""
    return ClaudeInvocationDB("data/claude_invocations.db")


db = get_db()

# Title
st.title("🤖 Claude Agent Invocation Monitor")
st.markdown("Real-time monitoring and debugging of Claude agent invocations")

# Sidebar filters
st.sidebar.header("Filters")

agent_types = ["All", "architect", "code-developer", "project-manager", "assistant", "ux-design-expert"]
selected_agent = st.sidebar.selectbox("Agent Type", agent_types)

time_ranges = {
    "Last Hour": timedelta(hours=1),
    "Last 24 Hours": timedelta(days=1),
    "Last Week": timedelta(weeks=1),
    "All Time": None,
}
selected_time = st.sidebar.selectbox("Time Range", list(time_ranges.keys()))

status_filter = st.sidebar.multiselect("Status", ["success", "error", "timeout"], default=["success", "error"])

limit = st.sidebar.slider("Max Records", 10, 200, 50)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_resource.clear()
    st.rerun()

# Get invocation history
agent_filter = None if selected_agent == "All" else selected_agent
history = db.get_invocation_history(agent_type=agent_filter, limit=limit)

# Filter by time range
if time_ranges[selected_time]:
    cutoff = datetime.utcnow() - time_ranges[selected_time]
    history = [h for h in history if datetime.fromisoformat(h["invoked_at"]) >= cutoff]

# Filter by status
history = [h for h in history if h["status"] in status_filter]

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_invocations = len(history)
    st.metric("Total Invocations", total_invocations)

with col2:
    total_tokens = sum(h.get("output_tokens", 0) for h in history)
    st.metric("Total Output Tokens", f"{total_tokens:,}")

with col3:
    total_cost = sum(h.get("cost_usd", 0) for h in history)
    st.metric("Total Cost", f"${total_cost:.4f}")

with col4:
    avg_duration = sum(h.get("duration_ms", 0) for h in history) / max(len(history), 1)
    st.metric("Avg Duration", f"{avg_duration:.0f}ms")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📜 History", "🔍 Details", "📈 Analytics"])

with tab1:
    st.header("Recent Invocations Overview")

    if not history:
        st.info("No invocations found matching filters.")
    else:
        # Create DataFrame
        df = pd.DataFrame(history)

        # Agent type distribution
        st.subheader("Invocations by Agent Type")
        agent_counts = df["agent_type"].value_counts()
        st.bar_chart(agent_counts)

        # Status distribution
        st.subheader("Status Distribution")
        col1, col2 = st.columns(2)
        with col1:
            status_counts = df["status"].value_counts()
            st.bar_chart(status_counts)

        with col2:
            success_rate = (df["status"] == "success").sum() / len(df) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

        # Timeline
        st.subheader("Invocation Timeline")
        df["invoked_at_dt"] = pd.to_datetime(df["invoked_at"])
        df_timeline = df.set_index("invoked_at_dt")
        st.line_chart(df_timeline.groupby(df_timeline.index.hour)["invocation_id"].count())

with tab2:
    st.header("Invocation History")

    for inv in history[:50]:  # Show top 50
        status_emoji = "✅" if inv["status"] == "success" else "❌" if inv["status"] == "error" else "⏱️"

        with st.expander(
            f"{status_emoji} [{inv['agent_type']}] {inv['prompt'][:60]}... "
            f"({inv.get('duration_ms', 0)}ms, ${inv.get('cost_usd', 0):.4f})"
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Prompt:**")
                st.text(inv["prompt"][:500])

                if inv.get("content"):
                    st.markdown("**Response:**")
                    st.text_area(
                        "Content",
                        inv["content"][:1000] + ("..." if len(inv.get("content", "")) > 1000 else ""),
                        height=200,
                        key=f"content_{inv['invocation_id']}",
                    )

                # Show final result if available (streaming)
                if inv.get("final_result"):
                    st.markdown("**Final Result:**")
                    st.code(inv["final_result"], language="text")

                if inv.get("error"):
                    st.error(f"Error: {inv['error']}")

            with col2:
                st.markdown("**Metadata:**")
                st.json(
                    {
                        "Invocation ID": inv["invocation_id"],
                        "Session ID": inv.get("session_id", "N/A"),
                        "Model": inv.get("model", "N/A"),
                        "Status": inv["status"],
                        "Stop Reason": inv.get("stop_reason", "N/A"),
                        "Invoked At": inv["invoked_at"],
                        "Completed At": inv.get("completed_at", "N/A"),
                        "Duration (ms)": inv.get("duration_ms", 0),
                        "Input Tokens": inv.get("input_tokens", 0),
                        "Output Tokens": inv.get("output_tokens", 0),
                        "Cost (USD)": inv.get("cost_usd", 0),
                    }
                )

            # Show streaming messages if available
            stream_messages = db.get_stream_messages(inv["invocation_id"])
            if stream_messages:
                st.markdown("**Streaming Timeline:**")
                st.caption(f"{len(stream_messages)} messages")

                for msg in stream_messages[:20]:  # Show first 20
                    msg_emoji = {
                        "init": "🎬",
                        "message": "💬",
                        "tool_use": "🔧",
                        "tool_result": "✅",
                        "result": "🏁",
                    }.get(msg["message_type"], "📝")

                    st.text(
                        f"{msg_emoji} [{msg['sequence']}] {msg['message_type']}: "
                        f"{msg['content'][:100] if msg['content'] else 'N/A'}"
                    )

                    # Show metadata for tool uses
                    if msg["message_type"] == "tool_use" and msg.get("metadata"):
                        try:
                            metadata = json.loads(msg["metadata"])
                            if "name" in metadata:
                                st.caption(f"   Tool: {metadata['name']}")
                        except json.JSONDecodeError:
                            pass

with tab3:
    st.header("Detailed Invocation Inspector")

    if history:
        # Select invocation
        inv_options = {
            f"{inv['invocation_id']}: [{inv['agent_type']}] {inv['prompt'][:40]}...": inv["invocation_id"]
            for inv in history[:50]
        }

        selected_inv_key = st.selectbox("Select Invocation", list(inv_options.keys()))
        selected_inv_id = inv_options[selected_inv_key]

        # Find invocation
        inv = next((h for h in history if h["invocation_id"] == selected_inv_id), None)

        if inv:
            st.subheader(f"Invocation #{inv['invocation_id']}")

            # Full details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### Full Prompt")
                st.text_area("Prompt", inv["prompt"], height=200, key="detailed_prompt")

                if inv.get("system_prompt"):
                    st.markdown("### System Prompt")
                    st.text_area("System", inv["system_prompt"], height=150, key="detailed_system")

                st.markdown("### Full Response")
                st.text_area("Response", inv.get("content", "N/A"), height=400, key="detailed_response")

            with col2:
                st.markdown("### Metrics")
                st.metric("Duration", f"{inv.get('duration_ms', 0)}ms")
                st.metric("Input Tokens", inv.get("input_tokens", 0))
                st.metric("Output Tokens", inv.get("output_tokens", 0))
                st.metric("Cost", f"${inv.get('cost_usd', 0):.6f}")

                st.markdown("### Status")
                status_color = {"success": "🟢", "error": "🔴", "timeout": "🟡"}.get(inv["status"], "⚪")
                st.write(f"{status_color} {inv['status']}")
                st.write(f"Stop Reason: {inv.get('stop_reason', 'N/A')}")

                if inv.get("error"):
                    st.error(inv["error"])

            # Streaming messages
            stream_messages = db.get_stream_messages(inv["invocation_id"])
            if stream_messages:
                st.markdown("### Complete Streaming Timeline")

                # Timeline visualization
                timeline_data = []
                for msg in stream_messages:
                    timeline_data.append(
                        {
                            "Sequence": msg["sequence"],
                            "Type": msg["message_type"],
                            "Timestamp": msg["timestamp"],
                            "Content Preview": msg["content"][:80] if msg["content"] else "N/A",
                        }
                    )

                st.dataframe(pd.DataFrame(timeline_data), use_container_width=True)

                # Full message details
                with st.expander("View All Messages (JSON)"):
                    st.json(stream_messages)

with tab4:
    st.header("Analytics")

    if history:
        df = pd.DataFrame(history)

        # Token usage over time
        st.subheader("Token Usage Over Time")
        df["invoked_at_dt"] = pd.to_datetime(df["invoked_at"])
        df_time = df.set_index("invoked_at_dt").sort_index()

        st.line_chart(df_time[["input_tokens", "output_tokens"]])

        # Cost analysis
        st.subheader("Cost Analysis")
        col1, col2 = st.columns(2)

        with col1:
            cost_by_agent = df.groupby("agent_type")["cost_usd"].sum().sort_values(ascending=False)
            st.bar_chart(cost_by_agent)
            st.caption("Total cost by agent type")

        with col2:
            tokens_by_agent = df.groupby("agent_type")["output_tokens"].sum().sort_values(ascending=False)
            st.bar_chart(tokens_by_agent)
            st.caption("Total output tokens by agent type")

        # Performance metrics
        st.subheader("Performance Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            avg_duration_by_agent = df.groupby("agent_type")["duration_ms"].mean().sort_values(ascending=False)
            st.bar_chart(avg_duration_by_agent)
            st.caption("Avg duration by agent (ms)")

        with col2:
            avg_tokens_per_ms = (df["output_tokens"] / df["duration_ms"].replace(0, 1)).mean()
            st.metric("Avg Tokens/Second", f"{avg_tokens_per_ms * 1000:.1f}")

            fastest_agent = df.groupby("agent_type")["duration_ms"].mean().idxmin()
            st.metric("Fastest Agent", fastest_agent)

        with col3:
            most_efficient = df.groupby("agent_type").apply(
                lambda x: (x["output_tokens"] / x["cost_usd"].replace(0, 1)).mean()
            )
            st.metric("Most Efficient Agent", most_efficient.idxmax())
            st.metric("Tokens per $", f"{most_efficient.max():.0f}")

        # Recent trends
        st.subheader("Recent Trends")

        # Success rate over time
        df_hourly = df.set_index("invoked_at_dt").resample("1H")
        success_rate_hourly = df_hourly.apply(lambda x: (x["status"] == "success").sum() / max(len(x), 1) * 100)

        st.line_chart(success_rate_hourly)
        st.caption("Success rate over time (hourly)")

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data source: data/claude_invocations.db")
