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
    from pathlib import Path

    state_file = Path("data/orchestrator/work_loop_state.json")

    if not state_file.exists():
        click.echo("⚠️  Orchestrator not running (no state file found)")
        return

    try:
        with open(state_file) as f:
            state = json.load(f)

        click.echo("📊 Orchestrator Status")
        click.echo("=" * 60)
        click.echo(f"Last Update: {state.get('last_update', 'N/A')}")
        click.echo(f"Last ROADMAP Update: {state.get('last_roadmap_update', 'N/A')}")
        click.echo("")

        # Active tasks
        active_tasks = state.get("active_tasks", {})
        if active_tasks:
            click.echo("Active Tasks:")
            for task_key, task_info in active_tasks.items():
                click.echo(f"  - {task_key}: {task_info.get('type', 'unknown')}")
        else:
            click.echo("No active tasks")

        click.echo("")

        # ROADMAP cache
        roadmap_cache = state.get("roadmap_cache")
        if roadmap_cache:
            priorities = roadmap_cache.get("priorities", [])
            planned = [p for p in priorities if p.get("status") == "📝"]
            click.echo(f"ROADMAP: {len(priorities)} total priorities, {len(planned)} planned")
        else:
            click.echo("ROADMAP: Not loaded yet")

    except Exception as e:
        click.echo(f"❌ Error reading status: {e}", err=True)


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


def main():
    """Entry point for CLI."""
    orchestrator()


if __name__ == "__main__":
    main()
