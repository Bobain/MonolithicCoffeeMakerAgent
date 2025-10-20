"""Orchestrator Rich UI Dashboard.

Provides real-time visualization of:
- Active agents (architect, code_developer, project_manager)
- Current tasks and progress
- Success metrics
- System health

Author: code_developer
Date: 2025-10-19
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import agent management skill
skill_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "orchestrator-agent-management"
sys.path.insert(0, str(skill_dir))
from agent_management import OrchestratorAgentManagementSkill

sys.path.pop(0)

logger = logging.getLogger(__name__)


class OrchestratorDashboard:
    """Real-time dashboard for orchestrator activities."""

    def __init__(self, state_file: Optional[Path] = None):
        """Initialize dashboard.

        Args:
            state_file: Path to orchestrator state file
        """
        self.console = Console()
        self.agent_mgmt = OrchestratorAgentManagementSkill()
        self.state_file = state_file or Path("data/orchestrator/work_loop_state.json")

        # Load ROADMAP cache and get orchestrator start time
        self.roadmap_cache: Optional[Dict[str, Any]] = None
        self.start_time = None
        self._load_roadmap_cache()

    def _load_roadmap_cache(self):
        """Load ROADMAP cache and orchestrator start time from state file."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.roadmap_cache = state.get("roadmap_cache")

                # Try to get orchestrator start time from state
                if "orchestrator_start_time" in state:
                    self.start_time = datetime.fromisoformat(state["orchestrator_start_time"])
                elif "last_updated" in state:
                    # Fallback: use last_updated as a proxy
                    self.start_time = datetime.fromisoformat(state["last_updated"])
                else:
                    # No timestamp available, use current time
                    self.start_time = datetime.now()

        except Exception as e:
            logger.warning(f"Failed to load ROADMAP cache: {e}")
            if not self.start_time:
                self.start_time = datetime.now()

    def _make_system_overview(self) -> Panel:
        """Create system overview panel.

        Returns:
            Rich Panel with system metrics
        """
        # Calculate uptime (handle None case)
        if self.start_time:
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split(".")[0]  # Remove microseconds
        else:
            uptime_str = "Unknown"

        # Get active agents count (only running agents)
        active_result = self.agent_mgmt.execute(action="list_active_agents")
        active_count = active_result.get("result", {}).get("total", 0) if not active_result.get("error") else 0

        # Get ROADMAP stats
        roadmap_stats = self._get_roadmap_stats()

        # Build overview text
        overview = Text()
        overview.append("🤖 Orchestrator Status\n", style="bold cyan")
        overview.append(f"Uptime: {uptime_str}\n", style="white")
        overview.append(f"Running Agents: {active_count}\n", style="green" if active_count > 0 else "yellow")
        overview.append(f"ROADMAP Health: {roadmap_stats['health']}\n", style=roadmap_stats["health_style"])
        overview.append(f"Priorities: {roadmap_stats['completed']}/{roadmap_stats['total']} completed\n", style="white")

        return Panel(overview, title="System Overview", border_style="cyan")

    def _get_roadmap_stats(self) -> Dict[str, Any]:
        """Get ROADMAP statistics.

        Returns:
            Dict with total, completed, in_progress, planned counts and health
        """
        if not self.roadmap_cache:
            return {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planned": 0,
                "health": "Unknown",
                "health_style": "yellow",
            }

        priorities = self.roadmap_cache.get("priorities", [])
        total = len(priorities)
        completed = len([p for p in priorities if p["status"] == "✅"])
        in_progress = len([p for p in priorities if p["status"] == "🚧"])
        planned = len([p for p in priorities if p["status"] == "📝"])

        # Calculate health
        if in_progress > 0:
            health = "Working"
            health_style = "green"
        elif planned > 0:
            health = "Idle (work available)"
            health_style = "yellow"
        else:
            health = "All complete!"
            health_style = "cyan"

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "planned": planned,
            "health": health,
            "health_style": health_style,
        }

    def _make_agents_table(self) -> Table:
        """Create running agents table.

        Returns:
            Rich Table with agent details
        """
        table = Table(title="Running Agents", show_header=True, header_style="bold magenta")
        table.add_column("PID", style="cyan", width=8)
        table.add_column("Agent Type", style="yellow", width=18)
        table.add_column("Task ID", style="white", width=20)
        table.add_column("Status", style="green", width=12)
        table.add_column("Duration", style="blue", width=12)

        # Get active agents
        result = self.agent_mgmt.execute(action="list_active_agents")

        if result.get("error"):
            table.add_row("—", "Error", result["error"], "—", "—")
            return table

        active_agents = result.get("result", {}).get("active_agents", [])

        if not active_agents:
            table.add_row("—", "No running agents", "—", "—", "—")
            return table

        for agent in active_agents:
            # Format duration
            duration_seconds = agent.get("duration", 0)
            duration_str = str(timedelta(seconds=int(duration_seconds))).split(".")[0]

            # Status emoji
            status = agent.get("status", "unknown")
            status_display = "🟢 Running" if status == "running" else "✅ Complete" if status == "completed" else status

            table.add_row(
                str(agent["pid"]),
                agent["agent_type"],
                agent["task_id"],
                status_display,
                duration_str,
            )

        return table

    def _make_work_queue(self) -> Panel:
        """Create work queue panel showing pending priorities.

        Returns:
            Rich Panel with work queue
        """
        if not self.roadmap_cache:
            return Panel("No ROADMAP data", title="Work Queue", border_style="yellow")

        priorities = self.roadmap_cache.get("priorities", [])
        planned = [p for p in priorities if p["status"] == "📝"][:5]  # Next 5 planned

        if not planned:
            queue_text = Text("No pending work", style="green")
        else:
            queue_text = Text()
            queue_text.append("Next priorities:\n", style="bold yellow")
            for i, p in enumerate(planned, 1):
                spec_icon = "📄" if p.get("has_spec") else "❌"
                queue_text.append(f"{i}. US-{p['number']:03d} {spec_icon} {p['name']}\n", style="white")

        return Panel(queue_text, title="Work Queue", border_style="yellow")

    def _make_metrics_panel(self) -> Panel:
        """Create success metrics panel.

        Returns:
            Rich Panel with metrics
        """
        # Calculate metrics from ROADMAP
        stats = self._get_roadmap_stats()
        total = stats["total"]
        completed = stats["completed"]

        completion_pct = (completed / total * 100) if total > 0 else 0

        metrics = Text()
        metrics.append("📊 Success Metrics\n", style="bold cyan")
        metrics.append(f"Completion: {completion_pct:.1f}%\n", style="green")
        metrics.append(f"Completed: {completed}\n", style="white")
        metrics.append(f"In Progress: {stats['in_progress']}\n", style="yellow")
        metrics.append(f"Planned: {stats['planned']}\n", style="blue")

        return Panel(metrics, title="Metrics", border_style="cyan")

    def _make_dashboard_layout(self) -> Layout:
        """Create dashboard layout.

        Returns:
            Rich Layout with all panels
        """
        layout = Layout()

        # Split into header and body
        layout.split(
            Layout(name="header", size=8),
            Layout(name="body"),
        )

        # Split header into overview and metrics
        layout["header"].split_row(
            Layout(self._make_system_overview(), name="overview"),
            Layout(self._make_metrics_panel(), name="metrics"),
        )

        # Split body into agents table and work queue
        layout["body"].split(
            Layout(self._make_agents_table(), name="agents", ratio=2),
            Layout(self._make_work_queue(), name="queue", ratio=1),
        )

        return layout

    def run(self, refresh_interval: int = 3):
        """Run dashboard with live updates.

        Args:
            refresh_interval: Refresh interval in seconds (default: 3)
        """
        self.console.clear()
        self.console.print("[bold cyan]🚀 Orchestrator Dashboard[/bold cyan]")
        self.console.print(f"[dim]Refresh interval: {refresh_interval}s | Press Ctrl+C to exit[/dim]\n")

        try:
            with Live(self._make_dashboard_layout(), refresh_per_second=1 / refresh_interval, console=self.console):
                while True:
                    time.sleep(refresh_interval)

                    # Reload ROADMAP cache
                    self._load_roadmap_cache()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped[/yellow]")
