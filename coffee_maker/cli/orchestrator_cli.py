"""CLI commands for Orchestrator Continuous Work Loop.

Provides commands to start, stop, and monitor the continuous work loop.

Usage:
    poetry run orchestrator start        # Start continuous work loop
    poetry run orchestrator status        # Check orchestrator status
    poetry run orchestrator stop          # Stop orchestrator gracefully

Related:
    SPEC-104: Technical specification
    US-104: Strategic requirement (PRIORITY 20)
"""

import logging
import sys

import click

from coffee_maker.orchestrator.continuous_work_loop import ContinuousWorkLoop, WorkLoopConfig

logger = logging.getLogger(__name__)


@click.group()
def orchestrator():
    """Orchestrator commands for continuous agent work coordination."""


@orchestrator.command()
@click.option("--poll-interval", default=30, help="ROADMAP polling interval (seconds)")
@click.option("--spec-backlog", default=3, help="Number of specs to keep ahead")
@click.option("--max-retries", default=3, help="Maximum retry attempts for failed tasks")
def start(poll_interval, spec_backlog, max_retries):
    """Start orchestrator continuous work loop.

    The work loop runs 24/7, continuously monitoring ROADMAP.md and delegating
    work to architect and code_developer agents.

    Example:
        poetry run orchestrator start
        poetry run orchestrator start --poll-interval 60 --spec-backlog 5
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    click.echo("🚀 Starting Orchestrator Continuous Work Loop")
    click.echo(f"   Poll interval: {poll_interval}s")
    click.echo(f"   Spec backlog target: {spec_backlog}")
    click.echo(f"   Max retries: {max_retries}")
    click.echo("")
    click.echo("Press Ctrl+C to stop gracefully")
    click.echo("")

    # Create configuration
    config = WorkLoopConfig(
        poll_interval_seconds=poll_interval,
        spec_backlog_target=spec_backlog,
        max_retry_attempts=max_retries,
    )

    # Create and start work loop
    work_loop = ContinuousWorkLoop(config)

    try:
        work_loop.start()
    except KeyboardInterrupt:
        click.echo("\n✅ Orchestrator stopped gracefully")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        logger.error(f"Orchestrator error: {e}", exc_info=True)
        sys.exit(1)


@orchestrator.command()
def status():
    """Check orchestrator status.

    Displays current work loop state, active tasks, and recent activity.

    Example:
        poetry run orchestrator status
    """
    import json
    import sqlite3
    from datetime import datetime
    from pathlib import Path

    db_path = Path("data/orchestrator.db")

    if not db_path.exists():
        click.echo("⚠️  Orchestrator not running (no database found)")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Read state from database (CFR-014 compliant)
        cursor.execute("SELECT key, value, updated_at FROM orchestrator_state")
        rows = cursor.fetchall()

        state = {}
        for row in rows:
            key = row["key"]
            value = row["value"]
            if key == "active_tasks":
                state[key] = json.loads(value)
            else:
                state[key] = value

        conn.close()

        if not state:
            click.echo("⚠️  Orchestrator not running (no state in database)")
            return

        click.echo("📊 Orchestrator Status")
        click.echo("=" * 60)

        # Display last update times
        if "last_roadmap_update" in state:
            last_roadmap_ts = float(state["last_roadmap_update"])
            last_roadmap_dt = datetime.fromtimestamp(last_roadmap_ts)
            click.echo(f"Last ROADMAP Update: {last_roadmap_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            click.echo("Last ROADMAP Update: N/A")

        click.echo("")

        # Active tasks
        active_tasks = state.get("active_tasks", {})
        if active_tasks:
            click.echo(f"Active Tasks: {len(active_tasks)}")
            for task_key, task_info in active_tasks.items():
                task_type = task_info.get("type", "unknown")
                agent = task_info.get("agent", "unknown")
                pid = task_info.get("pid", "N/A")
                click.echo(f"  - {task_key}: {task_type} (agent: {agent}, PID: {pid})")
        else:
            click.echo("No active tasks")

        click.echo("")

        # Check agent processes
        import psutil

        running_agents = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline", [])
                cmdline_str = " ".join(cmdline) if cmdline else ""
                if any(agent in cmdline_str for agent in ["architect", "code_developer", "code-reviewer"]):
                    running_agents.append((proc.info["name"], proc.info["pid"]))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if running_agents:
            click.echo(f"Running Agents: {len(running_agents)}")
            for name, pid in running_agents[:10]:  # Show first 10
                click.echo(f"  - PID {pid}: {name}")
        else:
            click.echo("No agents currently running")

    except Exception as e:
        click.echo(f"❌ Error reading status: {e}", err=True)
        logger.error(f"Status error: {e}", exc_info=True)


@orchestrator.command()
@click.option("--refresh", default=3, help="Refresh interval in seconds (default: 3)")
def dashboard(refresh):
    """Launch real-time dashboard showing agent activities.

    Displays:
    - System overview (uptime, health, ROADMAP status)
    - Active agents table (architect, code_developer, project_manager)
    - Work queue (next priorities)
    - Success metrics

    Example:
        poetry run orchestrator dashboard
        poetry run orchestrator dashboard --refresh 5
    """
    from coffee_maker.orchestrator.dashboard import OrchestratorDashboard

    dashboard_instance = OrchestratorDashboard()
    dashboard_instance.run(refresh_interval=refresh)


@orchestrator.command()
def stop():
    """Stop orchestrator gracefully.

    Sends SIGTERM signal to running orchestrator process.

    Example:
        poetry run orchestrator stop
    """
    import os
    import signal
    import psutil

    # Find orchestrator process
    found = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "orchestrator" in " ".join(cmdline) and "start" in cmdline:
                click.echo(f"Stopping orchestrator (PID: {proc.info['pid']})...")
                os.kill(proc.info["pid"], signal.SIGTERM)
                found = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if found:
        click.echo("✅ Stop signal sent. Orchestrator will shut down gracefully.")
    else:
        click.echo("⚠️  No running orchestrator found")


@orchestrator.command()
@click.option("--hours", default=6, help="Hours to look back (default: 6)")
@click.option("--save", is_flag=True, help="Save report to evidence/ directory")
def activity_summary(hours, save):
    """Generate activity and progress summary.

    Generates a comprehensive report showing:
    - Completed work (commits, merged priorities)
    - Current work (running agents, active worktrees)
    - Upcoming work (next planned priorities)
    - Summary statistics

    Example:
        poetry run orchestrator activity-summary
        poetry run orchestrator activity-summary --hours 2
        poetry run orchestrator activity-summary --save
    """
    from coffee_maker.orchestrator.activity_summary import generate_activity_summary

    click.echo(f"📊 Generating activity summary (last {hours} hours)...")
    click.echo("")

    try:
        report = generate_activity_summary(time_window=hours, save_to_file=save)

        click.echo(report)

        if save:
            click.echo("")
            click.echo("✅ Report saved to evidence/activity-summary-*.md")
            click.echo("   Notification created")

    except Exception as e:
        click.echo(f"\n❌ Error generating summary: {e}", err=True)
        logger.error(f"Activity summary error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    orchestrator()


if __name__ == "__main__":
    main()
