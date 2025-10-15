"""CLI commands for ACE framework.

This module provides command-line interfaces for manually running ACE components
and checking framework status.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from coffee_maker.autonomous.ace.config import get_default_config
from coffee_maker.autonomous.ace.curator import ACECurator
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.autonomous.ace.reflector import ACEReflector

logger = logging.getLogger(__name__)


def cmd_reflector():
    """Run reflector to extract insights from traces.

    Usage:
        poetry run ace-reflector --agent code_developer --hours 24
    """
    parser = argparse.ArgumentParser(
        description="Run ACE Reflector to analyze execution traces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze last 24 hours of traces for code_developer
  poetry run ace-reflector --agent code_developer --hours 24

  # Analyze last 7 days of traces
  poetry run ace-reflector --agent code_developer --hours 168

  # Specify custom output directory
  poetry run ace-reflector --agent code_developer --hours 24 --output /tmp/deltas
        """,
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (e.g., code_developer, project_manager)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours of traces to analyze (default: 24)",
    )
    parser.add_argument(
        "--output",
        help="Output directory for deltas (default: from config)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Initialize reflector
        config = get_default_config()

        # Override output directory if specified
        if args.output:
            config.delta_dir = Path(args.output)
            config.ensure_directories()

        reflector = ACEReflector(config=config, agent_name=args.agent)

        print(f"\n🔍 ACE Reflector - Analyzing traces for {args.agent}")
        print(f"{'='*60}")
        print(f"Time range: Last {args.hours} hours")
        print(f"Trace directory: {config.trace_dir}")
        print(f"Delta output: {config.delta_dir}")
        print()

        # Analyze recent traces
        deltas = reflector.analyze_recent_traces(hours=args.hours)

        print(f"\n✅ Reflector complete!")
        print(f"{'='*60}")
        print(f"Insights extracted: {len(deltas)}")
        print(f"Deltas saved to: {config.delta_dir}")

        if deltas:
            print(f"\nTop insights:")
            for i, delta in enumerate(deltas[:5], 1):
                print(f"  {i}. {delta.bullet_text[:80]}...")
        else:
            print(f"\n⚠️  No traces found in the last {args.hours} hours")
            print(f"   Check that ACE is enabled and traces are being generated")

        return 0

    except Exception as e:
        logger.error(f"Reflector failed: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}")
        return 1


def cmd_curator():
    """Run curator to consolidate deltas into playbook.

    Usage:
        poetry run ace-curator --agent code_developer
    """
    parser = argparse.ArgumentParser(
        description="Run ACE Curator to consolidate deltas into playbook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate all recent deltas for code_developer
  poetry run ace-curator --agent code_developer

  # Specify custom delta directory
  poetry run ace-curator --agent code_developer --input /tmp/deltas

  # Process specific number of recent deltas
  poetry run ace-curator --agent code_developer --max-deltas 10
        """,
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (e.g., code_developer)",
    )
    parser.add_argument(
        "--input",
        help="Delta directory (default: from config)",
    )
    parser.add_argument(
        "--max-deltas",
        type=int,
        default=100,
        help="Maximum number of recent deltas to process (default: 100)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Initialize curator
        config = get_default_config()

        # Override delta directory if specified
        if args.input:
            config.delta_dir = Path(args.input)

        curator = ACECurator(config=config, agent_name=args.agent)

        print(f"\n📚 ACE Curator - Consolidating deltas for {args.agent}")
        print(f"{'='*60}")
        print(f"Delta directory: {config.delta_dir}")
        print(f"Playbook output: {config.playbook_dir}")
        print(f"Max deltas: {args.max_deltas}")
        print()

        # Find recent delta files
        delta_dir = config.delta_dir
        delta_files = _find_recent_deltas(delta_dir, args.agent, args.max_deltas)

        if not delta_files:
            print(f"⚠️  No delta files found in {delta_dir}")
            print(f"   Run ace-reflector first to generate deltas")
            return 1

        print(f"Found {len(delta_files)} delta files to process")

        # Consolidate
        playbook = curator.consolidate_deltas(delta_files)

        print(f"\n✅ Curator complete!")
        print(f"{'='*60}")
        print(f"Playbook version: {playbook.playbook_version}")
        print(f"Total bullets: {playbook.total_bullets}")
        print(f"Effectiveness score: {playbook.effectiveness_score:.2f}")

        if playbook.health_metrics:
            print(f"\n📊 Health Metrics:")
            print(f"  Avg helpful count: {playbook.health_metrics.avg_helpful_count:.2f}")
            print(f"  Effectiveness ratio: {playbook.health_metrics.effectiveness_ratio:.2f}")
            print(f"  Coverage score: {playbook.health_metrics.coverage_score:.2f}")

        print(f"\n📚 Categories:")
        for category, bullets in playbook.categories.items():
            active = [b for b in bullets if not b.deprecated]
            print(f"  {category}: {len(active)} bullets")

        return 0

    except Exception as e:
        logger.error(f"Curator failed: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}")
        return 1


def cmd_status():
    """Show ACE framework status.

    Usage:
        poetry run ace-status --agent code_developer
    """
    parser = argparse.ArgumentParser(
        description="Show ACE framework status and playbook information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show status for code_developer
  poetry run ace-status --agent code_developer

  # Show detailed category breakdown
  poetry run ace-status --agent code_developer --detailed
        """,
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (e.g., code_developer)",
    )
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed category breakdown",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Load playbook
        loader = PlaybookLoader(agent_name=args.agent)

        # Try to load playbook
        try:
            playbook = loader.load()
        except FileNotFoundError:
            print(f"\n⚠️  No playbook found for {args.agent}")
            print(f"   Run ace-reflector and ace-curator to create one")
            return 1

        # Show status
        print(f"\n🤖 ACE Status for {args.agent}")
        print(f"{'='*60}")
        print(f"Playbook version: {playbook.playbook_version}")
        print(f"Last updated: {playbook.last_updated}")
        print(f"Total bullets: {playbook.total_bullets}")
        print(f"Effectiveness score: {playbook.effectiveness_score:.2f}")

        if playbook.health_metrics:
            print(f"\n📊 Health Metrics:")
            print(f"  Avg helpful count: {playbook.health_metrics.avg_helpful_count:.2f}")
            print(f"  Effectiveness ratio: {playbook.health_metrics.effectiveness_ratio:.2f}")
            print(f"  Coverage score: {playbook.health_metrics.coverage_score:.2f}")
            print(f"  Stale bullets: {playbook.health_metrics.stale_bullet_count}")
            print(f"  Recent usage: {playbook.health_metrics.recent_usage_count}")

        print(f"\n📚 Categories:")
        for category, bullets in playbook.categories.items():
            active = [b for b in bullets if not b.deprecated]
            deprecated = [b for b in bullets if b.deprecated]
            print(f"  {category}:")
            print(f"    Active: {len(active)}")
            if deprecated:
                print(f"    Deprecated: {len(deprecated)}")

            if args.detailed and active:
                print(f"    Top bullets:")
                for i, bullet in enumerate(active[:3], 1):
                    helpful = bullet.helpful_count
                    print(f"      {i}. [{helpful} helpful] {bullet.text[:60]}...")

        # Check ACE configuration
        config = get_default_config()
        print(f"\n⚙️  ACE Configuration:")
        print(f"  Enabled: {config.enabled}")
        print(f"  Auto-reflect: {config.auto_reflect}")
        print(f"  Auto-curate: {config.auto_curate}")
        print(f"  Trace directory: {config.trace_dir}")
        print(f"  Delta directory: {config.delta_dir}")
        print(f"  Playbook directory: {config.playbook_dir}")

        # Count traces and deltas
        trace_count = len(list(config.trace_dir.glob(f"{args.agent}_*.json"))) if config.trace_dir.exists() else 0
        delta_count = len(list(config.delta_dir.glob(f"{args.agent}_*.json"))) if config.delta_dir.exists() else 0

        print(f"\n📁 File Counts:")
        print(f"  Traces: {trace_count}")
        print(f"  Deltas: {delta_count}")
        print(f"  Playbooks: 1")

        return 0

    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}")
        return 1


def _find_recent_deltas(delta_dir: Path, agent_name: str, max_count: int) -> List[Path]:
    """Find recent delta files for an agent.

    Args:
        delta_dir: Directory containing delta files
        agent_name: Name of the agent
        max_count: Maximum number of deltas to return

    Returns:
        List of delta file paths, sorted by modification time (newest first)
    """
    if not delta_dir.exists():
        return []

    # Find all delta files for this agent
    delta_files = list(delta_dir.glob(f"{agent_name}_delta_*.json"))

    # Sort by modification time (newest first)
    delta_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Return up to max_count
    return delta_files[:max_count]


if __name__ == "__main__":
    # Support running as module
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Remove command name

        if cmd == "reflector":
            sys.exit(cmd_reflector())
        elif cmd == "curator":
            sys.exit(cmd_curator())
        elif cmd == "status":
            sys.exit(cmd_status())
        else:
            print(f"Unknown command: {cmd}")
            print("Available commands: reflector, curator, status")
            sys.exit(1)
    else:
        print("Usage: python -m coffee_maker.autonomous.ace.cli <command>")
        print("Commands: reflector, curator, status")
        sys.exit(1)
