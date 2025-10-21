#!/usr/bin/env python3
"""Quick script to check status of all agents."""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def check_agent_status():
    """Check and display status of all agents."""
    status_dir = Path("data/agent_status")

    if not status_dir.exists():
        console.print("[red]❌ Status directory not found. Is the orchestrator running?[/]")
        return

    # Check orchestrator status
    orch_status_file = status_dir / "orchestrator_status.json"

    if orch_status_file.exists():
        orch_status = json.loads(orch_status_file.read_text())

        console.print("\n[bold cyan]Multi-Agent Orchestrator Status[/]\n")

        # Orchestrator info
        console.print(f"[green]✓[/] Orchestrator running")
        if "started_at" in orch_status:
            console.print(f"  Started: {orch_status['started_at']}")
        if "uptime_seconds" in orch_status:
            uptime = int(orch_status["uptime_seconds"])
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            console.print(f"  Uptime: {hours}h {minutes}m")

        # Agent status table
        if "agents" in orch_status:
            table = Table(title="\nAgent Status")
            table.add_column("Agent", style="cyan")
            table.add_column("PID", style="yellow")
            table.add_column("Status", style="green")
            table.add_column("Restarts", style="magenta")

            for agent_name, agent_info in orch_status["agents"].items():
                status = "✓ Running" if agent_info.get("alive", False) else "❌ Dead"
                status_color = "green" if agent_info.get("alive", False) else "red"

                table.add_row(
                    agent_name,
                    str(agent_info.get("pid", "N/A")),
                    f"[{status_color}]{status}[/]",
                    str(agent_info.get("restarts", 0)),
                )

            console.print(table)
    else:
        console.print("[red]❌ Orchestrator not running[/]")
        console.print("\n[yellow]💡 Start with: poetry run user-listener[/]")


if __name__ == "__main__":
    check_agent_status()
