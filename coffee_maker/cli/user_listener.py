"""User Listener CLI - The ONLY UI for the system.

This module provides the primary user interface for the Coffee Maker Agent system.
ALL user interactions go through user_listener.

user_listener is an interpreter and delegator that:
1. Listens to user's words
2. Interprets their intent
3. Delegates to appropriate team members
4. Synthesizes responses back to user

Commands:
    user-listener                      Start interactive chat (default)
    user-listener agents               List all available agents
    user-listener curate [agent]       Trigger ACE curation
    user-listener playbook [agent]     View agent playbook
    user-listener status               Project status
    user-listener metrics              Estimation metrics
    user-listener roadmap              View ROADMAP

Example:
    # Start interactive chat
    user-listener

    # List team members
    user-listener agents

    # Trigger curation
    user-listener curate code_developer

    # View playbook
    user-listener playbook code_developer

    # Check project status
    user-listener status
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from coffee_maker.cli.agent_colors import (
    format_agent_message,
    list_all_agents,
    get_agent_color,
)

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def user_listener(ctx):
    """user_listener - The only UI for interacting with the system.

    user_listener is your primary interface to the autonomous development team.
    It interprets your requests and delegates to appropriate team members.

    Run without arguments to start interactive chat mode.
    """
    if ctx.invoked_subcommand is None:
        # Default to chat mode
        ctx.invoke(chat)


@user_listener.command()
@click.argument("agent_name", default="code_developer")
def curate(agent_name):
    """Trigger ACE curation (delegates to curator).

    This command delegates to the reflector and curator agents to analyze
    recent execution traces and update the playbook with new insights.

    Args:
        agent_name: Agent to curate (default: code_developer)

    Example:
        user-listener curate code_developer
    """
    console.print(format_agent_message("user_listener", f"Delegating curation to curator..."), style="bold")
    console.print()

    try:
        from coffee_maker.autonomous.ace import ACECurator, ACEReflector
        from coffee_maker.autonomous.ace.config import get_default_config

        # Step 1: Run reflector
        console.print(format_agent_message("reflector", "Analyzing execution traces from last 24 hours..."))

        config = get_default_config()
        reflector = ACEReflector(agent_name=agent_name, config=config)
        deltas = reflector.analyze_recent_traces(hours=24)

        if not deltas:
            console.print(format_agent_message("reflector", "⚠️ No traces found in last 24 hours"), style="yellow")
            console.print()
            console.print(
                format_agent_message(
                    "user_listener",
                    "Make sure daemon is running with ACE_ENABLED=true and has executed at least one priority.",
                )
            )
            return

        console.print(
            format_agent_message("reflector", f"✅ Extracted {len(deltas)} insights from traces"), style="bold"
        )
        console.print()

        # Step 2: Run curator
        console.print(format_agent_message("curator", "Consolidating deltas into playbook..."))

        curator = ACECurator(agent_name=agent_name, config=config)

        # Find recent delta files
        delta_dir = config.delta_dir
        delta_files = list(delta_dir.glob(f"{agent_name}_delta_*.json"))

        if not delta_files:
            console.print(format_agent_message("curator", f"⚠️ No delta files found in {delta_dir}"), style="yellow")
            return

        # Sort by modification time (newest first)
        delta_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Use up to 100 most recent deltas
        delta_files = delta_files[:100]

        playbook = curator.consolidate_deltas(delta_files)

        console.print(format_agent_message("curator", f"✅ Playbook updated successfully!"), style="bold")
        console.print()

        # Show results
        console.print(
            format_agent_message(
                "user_listener",
                f"Curation complete! Playbook has {playbook.total_bullets} bullets "
                f"(effectiveness: {playbook.effectiveness_score:.2f})",
            )
        )
        console.print()
        console.print(f"💡 Tip: Use 'user-listener playbook {agent_name}' to view full playbook")
        console.print()

    except ImportError:
        console.print(format_agent_message("user_listener", "❌ ACE framework not available"), style="bold red")
        console.print("\nThe ACE framework is not installed or has missing dependencies.")
    except Exception as e:
        console.print(format_agent_message("user_listener", f"❌ Error during curation: {e}"), style="bold red")
        import traceback

        traceback.print_exc()


@user_listener.command()
@click.argument("agent_name", default="code_developer")
@click.option("--category", help="Filter by category")
def playbook(agent_name, category):
    """View agent playbook (delegates to curator).

    Args:
        agent_name: Agent whose playbook to view (default: code_developer)
        category: Optional category filter

    Example:
        user-listener playbook code_developer
        user-listener playbook code_developer --category implementation
    """
    console.print(format_agent_message("user_listener", f"Fetching playbook from curator..."), style="bold")
    console.print()

    try:
        from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
        from coffee_maker.autonomous.ace.config import get_default_config

        config = get_default_config()
        loader = PlaybookLoader(agent_name=agent_name, config=config)

        try:
            playbook_obj = loader.load()
        except FileNotFoundError:
            console.print(format_agent_message("curator", f"❌ No playbook found for {agent_name}"), style="bold red")
            console.print()
            console.print(
                format_agent_message("user_listener", f"Run curation first: user-listener curate {agent_name}")
            )
            return

        # Display playbook
        console.print(Panel(f"[bold]ACE Playbook - {agent_name}[/bold]", style=get_agent_color("curator")))
        console.print()

        if category:
            # Show specific category
            if category not in playbook_obj.categories:
                console.print(format_agent_message("curator", f"❌ Category '{category}' not found"), style="red")
                console.print(f"\nAvailable categories: {', '.join(playbook_obj.categories.keys())}")
                return

            bullets = playbook_obj.categories[category]
            active_bullets = [b for b in bullets if not b.deprecated]

            console.print(format_agent_message("curator", f"Category: {category} ({len(active_bullets)} bullets)"))
            console.print()

            for i, bullet in enumerate(active_bullets, 1):
                console.print(f"{i}. {bullet.text}")
                console.print(f"   [dim]Helpful: {bullet.helpful_count} | Pruned: {bullet.pruned_count}[/dim]")
                if bullet.evidence:
                    console.print(f"   [dim]Evidence: {len(bullet.evidence)} trace(s)[/dim]")
                console.print()
        else:
            # Show full playbook summary
            console.print(f"Version: {playbook_obj.playbook_version}")
            console.print(f"Last updated: {playbook_obj.last_updated}")
            console.print(f"Total bullets: {playbook_obj.total_bullets}")
            console.print(f"Effectiveness score: {playbook_obj.effectiveness_score:.2f}")
            console.print()

            if playbook_obj.health_metrics:
                console.print("[bold]Health Metrics:[/bold]")
                console.print(f"  Avg helpful count: {playbook_obj.health_metrics.avg_helpful_count:.2f}")
                console.print(f"  Effectiveness ratio: {playbook_obj.health_metrics.effectiveness_ratio:.2f}")
                console.print(f"  Coverage score: {playbook_obj.health_metrics.coverage_score:.2f}")
                console.print(f"  Stale bullets: {playbook_obj.health_metrics.stale_bullet_count}")
                console.print()

            console.print("[bold]Categories:[/bold]")
            for cat, bullets in playbook_obj.categories.items():
                active = [b for b in bullets if not b.deprecated]
                deprecated = [b for b in bullets if b.deprecated]
                console.print(f"\n  [bold]{cat.upper()}[/bold] ({len(active)} active, {len(deprecated)} deprecated)")

                # Show top 3 bullets per category
                for i, bullet in enumerate(active[:3], 1):
                    helpful = bullet.helpful_count
                    console.print(f"    {i}. [{helpful} helpful] {bullet.text[:70]}...")

                if len(active) > 3:
                    console.print(f"    [dim]... and {len(active) - 3} more[/dim]")

            console.print()
            console.print(f"💡 Tip: Use --category <name> to see full category details")
            console.print(f"   Available: {', '.join(playbook_obj.categories.keys())}")

        console.print()

    except ImportError:
        console.print(format_agent_message("user_listener", "❌ ACE framework not available"), style="bold red")
    except Exception as e:
        console.print(format_agent_message("user_listener", f"❌ Error: {e}"), style="bold red")
        import traceback

        traceback.print_exc()


@user_listener.command()
def status():
    """Project status (delegates to project_manager).

    Example:
        user-listener status
    """
    console.print(format_agent_message("user_listener", "Asking project_manager for status..."), style="bold")
    console.print()

    # Delegate to project_manager
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "poetry", "run", "project-manager", "status"])
    sys.exit(result.returncode)


@user_listener.command()
def metrics():
    """Estimation metrics and velocity (delegates to project_manager).

    Example:
        user-listener metrics
    """
    console.print(format_agent_message("user_listener", "Getting metrics from project_manager..."), style="bold")
    console.print()

    # Delegate to project_manager
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "poetry", "run", "project-manager", "metrics"])
    sys.exit(result.returncode)


@user_listener.command()
@click.argument("priority", required=False)
def roadmap(priority):
    """View ROADMAP (delegates to project_manager).

    Args:
        priority: Optional specific priority to view

    Example:
        user-listener roadmap
        user-listener roadmap PRIORITY-5
    """
    console.print(format_agent_message("user_listener", "Fetching ROADMAP from project_manager..."), style="bold")
    console.print()

    # Delegate to project_manager
    import subprocess
    import sys

    cmd = [sys.executable, "-m", "poetry", "run", "project-manager", "view"]
    if priority:
        cmd.append(priority)

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@user_listener.command()
def agents():
    """List all available agents with their colors and descriptions.

    Example:
        user-listener agents
    """
    console.print()
    console.print(Panel("[bold]Coffee Maker Agent Team Members[/bold]", style="blue"))
    console.print()

    all_agents = list_all_agents()

    if not all_agents:
        console.print(format_agent_message("user_listener", "⚠️ No agent definitions found"), style="yellow")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="bold")
    table.add_column("Color", justify="center")
    table.add_column("Description")
    table.add_column("Model")

    for name, info in sorted(all_agents.items()):
        color = info["color"]
        description = info["description"][:60] + "..." if len(info["description"]) > 60 else info["description"]
        model = info["model"]

        # Show color swatch
        color_swatch = f"[{color}]●[/{color}]"

        table.add_row(name, color_swatch, description, model)

    console.print(table)
    console.print()
    console.print(
        format_agent_message(
            "user_listener",
            "These agents work together as your autonomous development team. "
            "I delegate to them based on what you need.",
        )
    )
    console.print()


@user_listener.command()
def chat():
    """Start interactive chat mode.

    This is the default mode when you run user-listener without arguments.

    Example:
        user-listener
        user-listener chat
    """
    console.print()
    console.print(Panel("[bold]Coffee Maker Agent - User Listener[/bold]", style="blue"))
    console.print()
    console.print(
        format_agent_message(
            "user_listener",
            "Welcome! I'm your interface to the autonomous development team. "
            "I'll interpret your requests and delegate to the right agents.",
        )
    )
    console.print()
    console.print("[dim]Type 'help' for commands, 'agents' to see team members, or 'exit' to quit.[/dim]")
    console.print()

    # For now, delegate to existing project-manager chat
    # TODO: Implement proper user_listener chat with delegation
    console.print(format_agent_message("user_listener", "Delegating to project-manager chat interface for now..."))
    console.print()

    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "poetry", "run", "project-manager", "chat"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    user_listener()
