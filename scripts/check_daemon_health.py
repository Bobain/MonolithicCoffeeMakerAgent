#!/usr/bin/env python3
"""Check daemon logs for infinite loop patterns.

This script analyzes daemon logs to detect if the daemon is stuck in an
infinite loop attempting the same priority repeatedly.

Exit Codes:
    0: No infinite loop detected (healthy)
    1: Infinite loop detected (unhealthy)
    2: Error analyzing logs

Usage:
    python scripts/check_daemon_health.py [--log-file PATH] [--max-attempts N]

Example:
    python scripts/check_daemon_health.py
    python scripts/check_daemon_health.py --log-file daemon.log --max-attempts 3
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional


def check_for_infinite_loop(log_content: str, max_attempts: int = 3) -> bool:
    """Detect if daemon is stuck in infinite loop.

    Args:
        log_content: Log file content to analyze
        max_attempts: Maximum attempts before considering it an infinite loop

    Returns:
        True if infinite loop detected, False otherwise
    """
    # Pattern: "Starting implementation of PRIORITY X"
    pattern = r"Starting implementation of (PRIORITY [\d.]+)"
    attempts: Dict[str, int] = {}

    for match in re.finditer(pattern, log_content):
        priority = match.group(1)
        attempts[priority] = attempts.get(priority, 0) + 1

    # Check if any priority attempted too many times
    for priority, count in attempts.items():
        if count > max_attempts:
            print(f"❌ INFINITE LOOP DETECTED: {priority} attempted {count} times (max: {max_attempts})")
            print(f"   This indicates the daemon is stuck retrying the same priority.")
            print(f"   Possible causes:")
            print(f"   - No files changed during implementation")
            print(f"   - Priority description too vague")
            print(f"   - Implementation requires manual intervention")
            return True

    print(f"✅ No infinite loop detected")
    print(f"   Priority attempt summary:")
    for priority, count in sorted(attempts.items()):
        status = "✓" if count <= max_attempts else "✗"
        print(f"   {status} {priority}: {count} attempt(s)")

    return False


def find_log_file() -> Optional[Path]:
    """Find daemon log file in common locations.

    Returns:
        Path to log file or None if not found
    """
    # Common log file locations
    locations = [
        Path("daemon.log"),
        Path("logs/daemon.log"),
        Path("data/daemon.log"),
        Path("/var/log/daemon.log"),
    ]

    for location in locations:
        if location.exists():
            print(f"Found log file: {location}")
            return location

    return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check daemon logs for infinite loop patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check for infinite loops in default log location:
    python scripts/check_daemon_health.py

  Check specific log file:
    python scripts/check_daemon_health.py --log-file daemon.log

  Use custom max attempts threshold:
    python scripts/check_daemon_health.py --max-attempts 5
        """,
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to daemon log file (auto-detected if not specified)",
    )

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum attempts before considering it an infinite loop (default: 3)",
    )

    args = parser.parse_args()

    # Find log file
    log_file = args.log_file
    if not log_file:
        log_file = find_log_file()

    if not log_file:
        print("❌ ERROR: No log file found", file=sys.stderr)
        print("   Specify log file with --log-file or create daemon.log", file=sys.stderr)
        sys.exit(2)

    if not log_file.exists():
        print(f"❌ ERROR: Log file not found: {log_file}", file=sys.stderr)
        sys.exit(2)

    # Read log file
    try:
        log_content = log_file.read_text()
    except Exception as e:
        print(f"❌ ERROR: Failed to read log file: {e}", file=sys.stderr)
        sys.exit(2)

    if not log_content:
        print("⚠️  WARNING: Log file is empty", file=sys.stderr)
        print("   No analysis possible", file=sys.stderr)
        sys.exit(0)

    # Check for infinite loop
    print(f"Analyzing daemon logs: {log_file}")
    print(f"Max attempts threshold: {args.max_attempts}")
    print()

    infinite_loop = check_for_infinite_loop(log_content, args.max_attempts)

    if infinite_loop:
        print()
        print("ACTION REQUIRED:")
        print("1. Stop the daemon")
        print("2. Review the problematic priority in ROADMAP.md")
        print("3. Either:")
        print("   a. Make the priority description more concrete")
        print("   b. Manually implement the priority")
        print("   c. Mark as 'Manual Only' in ROADMAP")
        print("4. Restart the daemon")
        sys.exit(1)
    else:
        print()
        print("Daemon health: HEALTHY ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()
