"""Progress tracker for user_listener UI.

Shows real-time progress of user requests through delegation chain.

This module provides visual feedback to users that the system is actively
working on their request, showing each step and its status.

Usage:
    from coffee_maker.cli.progress_tracker import ProgressTracker, StepStatus

    progress = ProgressTracker(console)
    progress.start(
        request="Implement authentication",
        steps=["Interpreting request", "Delegating to agent", "Processing", "Summarizing"]
    )

    progress.update_step(0, StepStatus.ACTIVE)
    # ... do work ...
    progress.update_step(0, StepStatus.COMPLETE)

    progress.complete()
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from typing import List, Dict, Any, Optional
from enum import Enum


class StepStatus(Enum):
    """Status of a workflow step."""

    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETE = "complete"
    ERROR = "error"


class ProgressTracker:
    """Track and display progress of user requests.

    Displays a Rich panel showing the current request and step-by-step
    progress through the delegation workflow.

    Example panel:
    ┌─ Coffee Maker Agent ─────────────────────────────────────────┐
    │ 🔄 Working on: "Implement authentication feature"            │
    │                                                                │
    │ Step 1/4: Interpreting request...              [✓] COMPLETE  │
    │ Step 2/4: code_developer implementing...       [●] ACTIVE    │
    │ Step 3/4: Running tests...                     [ ] WAITING   │
    │ Step 4/4: Summarizing results...               [ ] WAITING   │
    └────────────────────────────────────────────────────────────────┘
    """

    def __init__(self, console: Console, use_live: bool = False):
        """Initialize progress tracker.

        Args:
            console: Rich console for rendering
            use_live: Use Live display for auto-refreshing (default: False)
        """
        self.console = console
        self.use_live = use_live
        self.current_request: Optional[str] = None
        self.steps: List[Dict[str, Any]] = []
        self.active_step: int = 0
        self.live: Optional[Live] = None

    def start(self, request: str, steps: List[str]):
        """Start tracking a new request.

        Args:
            request: User's request text
            steps: List of step descriptions in order
        """
        self.current_request = request
        self.steps = [{"name": step, "status": StepStatus.WAITING} for step in steps]
        self.active_step = 0

        if self.use_live:
            self.live = Live(self._create_panel(), console=self.console, refresh_per_second=4)
            self.live.start()
        else:
            self._render()

    def update_step(self, step_index: int, status: StepStatus):
        """Update status of a specific step.

        Args:
            step_index: Index of step to update (0-based)
            status: New status for the step
        """
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = status
            if status == StepStatus.ACTIVE:
                self.active_step = step_index

            if self.use_live and self.live:
                self.live.update(self._create_panel())
            else:
                self._render()

    def complete(self):
        """Mark all steps as complete."""
        for step in self.steps:
            if step["status"] != StepStatus.ERROR:
                step["status"] = StepStatus.COMPLETE

        if self.use_live and self.live:
            self.live.update(self._create_panel())
            self.live.stop()
            self.live = None
        else:
            self._render()

    def error(self, step_index: int, message: str):
        """Mark step as error.

        Args:
            step_index: Index of step that errored
            message: Error message to display
        """
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = StepStatus.ERROR
            self.steps[step_index]["error"] = message

            if self.use_live and self.live:
                self.live.update(self._create_panel())
                self.live.stop()
                self.live = None
            else:
                self._render()

    def stop(self):
        """Stop live display if active."""
        if self.live:
            self.live.stop()
            self.live = None

    def _create_panel(self) -> Panel:
        """Create the progress panel."""
        if not self.current_request:
            return Panel("No active request", title="Coffee Maker Agent")

        # Create table for steps
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Step", style="cyan")
        table.add_column("Status", justify="right")

        for i, step in enumerate(self.steps):
            step_num = f"Step {i+1}/{len(self.steps)}"
            step_name = step["name"]
            status = step["status"]

            # Status indicator
            if status == StepStatus.COMPLETE:
                indicator = "[green]✓ COMPLETE[/green]"
            elif status == StepStatus.ACTIVE:
                indicator = "[yellow]● ACTIVE[/yellow]"
            elif status == StepStatus.ERROR:
                error_msg = step.get("error", "Error occurred")
                indicator = f"[red]✗ ERROR: {error_msg}[/red]"
            else:
                indicator = "[dim]○ WAITING[/dim]"

            table.add_row(f"{step_num}: {step_name}", indicator)

        # Truncate request if too long
        display_request = self.current_request
        if len(display_request) > 60:
            display_request = display_request[:57] + "..."

        # Create panel
        title = f'🔄 Working on: "{display_request}"'
        panel = Panel(
            table,
            title=title,
            title_align="left",
            border_style="blue",
            padding=(1, 2),
        )

        return panel

    def _render(self):
        """Render progress panel to console."""
        # Clear console and render
        self.console.clear()
        self.console.print(self._create_panel())
        self.console.print()
