#!/usr/bin/env python3
"""Check daemon logs for infinite loop patterns and health issues.

This script analyzes daemon logs to detect:
- Infinite loops (same priority attempted >3 times)
- Repeated failures
- Performance issues

Usage:
    python scripts/check_daemon_health.py [--log-file PATH]
    python scripts/check_daemon_health.py --stdin  # Read from stdin

Exit Codes:
    0: All checks passed
    1: Infinite loop or critical issue detected
    2: Script error
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def check_for_infinite_loop(log_content: str, max_attempts: int = 3) -> Tuple[bool, Dict[str, int]]:
    """Detect if daemon is stuck in infinite loop.

    Args:
        log_content: Full log content to analyze
        max_attempts: Maximum attempts before considering it a loop

    Returns:
        Tuple of (has_loop, attempts_dict)
        has_loop: True if infinite loop detected
        attempts_dict: Dict mapping priority names to attempt counts
    """
    # Pattern: Look for "Starting implementation of PRIORITY X"
    pattern = r"Starting implementation of (PRIORITY [\w.]+)"
    attempts = defaultdict(int)

    for match in re.finditer(pattern, log_content, re.IGNORECASE):
        priority = match.group(1)
        attempts[priority] += 1

    # Check if any priority exceeded max attempts
    has_loop = any(count > max_attempts for count in attempts.values())

    return has_loop, dict(attempts)


def check_for_repeated_errors(log_content: str) -> List[str]:
    """Detect repeated error messages.

    Args:
        log_content: Full log content to analyze

    Returns:
        List of repeated error messages
    """
    error_pattern = r"(ERROR|CRITICAL|Exception):(.+)"
    errors = defaultdict(int)

    for match in re.finditer(error_pattern, log_content):
        error_msg = match.group(2).strip()
        errors[error_msg] += 1

    # Return errors that occurred more than twice
    repeated = [msg for msg, count in errors.items() if count > 2]
    return repeated


def check_for_no_progress(log_content: str) -> bool:
    """Detect if daemon is making no progress.

    Args:
        log_content: Full log content to analyze

    Returns:
        True if no progress detected
    """
    # Look for success indicators
    success_patterns = [
        r"✅|Complete|Success|Committed|Created PR",
        r"Moving to next priority",
        r"Implementation complete",
    ]

    for pattern in success_patterns:
        if re.search(pattern, log_content, re.IGNORECASE):
            return False

    # No success indicators found
    return True


def check_performance_issues(log_content: str) -> List[str]:
    """Detect performance issues in logs.

    Args:
        log_content: Full log content to analyze

    Returns:
        List of performance warnings
    """
    warnings = []

    # Check for timeout patterns
    if re.search(r"timeout|timed out", log_content, re.IGNORECASE):
        warnings.append("Timeout detected in logs")

    # Check for long execution times
    duration_pattern = r"took (\d+) (minutes|seconds)"
    for match in re.finditer(duration_pattern, log_content):
        duration = int(match.group(1))
        unit = match.group(2)

        if unit == "minutes" and duration > 30:
            warnings.append(f"Long execution time: {duration} minutes")

    return warnings


def analyze_log_file(log_path: Path) -> Dict[str, any]:
    """Analyze a log file for health issues.

    Args:
        log_path: Path to log file

    Returns:
        Dict with analysis results
    """
    if not log_path.exists():
        print(f"⚠️  Log file not found: {log_path}")
        return {"exists": False, "healthy": True, "warnings": ["No log file found"]}  # No logs = no issues yet

    content = log_path.read_text()

    # Run all checks
    has_loop, attempts = check_for_infinite_loop(content)
    repeated_errors = check_for_repeated_errors(content)
    no_progress = check_for_no_progress(content)
    perf_issues = check_performance_issues(content)

    results = {
        "exists": True,
        "healthy": not (has_loop or repeated_errors or no_progress),
        "infinite_loop": has_loop,
        "attempts": attempts,
        "repeated_errors": repeated_errors,
        "no_progress": no_progress,
        "performance_issues": perf_issues,
    }

    return results


def print_results(results: Dict[str, any]) -> None:
    """Print analysis results in human-readable format.

    Args:
        results: Results from analyze_log_file()
    """
    print("\n" + "=" * 60)
    print("DAEMON HEALTH CHECK RESULTS")
    print("=" * 60 + "\n")

    if not results["exists"]:
        print("⚠️  No log file found - cannot perform health check")
        print("   This is okay if daemon hasn't run yet.")
        return

    # Overall health
    if results["healthy"]:
        print("✅ HEALTHY: No critical issues detected\n")
    else:
        print("❌ UNHEALTHY: Issues detected\n")

    # Infinite loop check
    if results["infinite_loop"]:
        print("❌ INFINITE LOOP DETECTED:")
        for priority, count in results["attempts"].items():
            if count > 3:
                print(f"   - {priority}: attempted {count} times")
        print()
    else:
        print("✅ No infinite loops detected")
        if results["attempts"]:
            print("   Attempts per priority:")
            for priority, count in sorted(results["attempts"].items()):
                print(f"   - {priority}: {count} attempt(s)")
        print()

    # Repeated errors
    if results["repeated_errors"]:
        print("⚠️  REPEATED ERRORS:")
        for error in results["repeated_errors"]:
            print(f"   - {error}")
        print()
    else:
        print("✅ No repeated errors\n")

    # Progress check
    if results["no_progress"]:
        print("⚠️  NO PROGRESS: Daemon may be stuck\n")
    else:
        print("✅ Daemon is making progress\n")

    # Performance issues
    if results["performance_issues"]:
        print("⚠️  PERFORMANCE ISSUES:")
        for issue in results["performance_issues"]:
            print(f"   - {issue}")
        print()
    else:
        print("✅ No performance issues\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check daemon health from logs", formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--log-file", type=Path, default=Path("daemon.log"), help="Path to daemon log file (default: daemon.log)"
    )
    parser.add_argument("--stdin", action="store_true", help="Read log content from stdin")
    parser.add_argument("--quiet", action="store_true", help="Only output errors (exit code indicates status)")

    args = parser.parse_args()

    try:
        if args.stdin:
            # Read from stdin
            content = sys.stdin.read()
            has_loop, attempts = check_for_infinite_loop(content)
            repeated_errors = check_for_repeated_errors(content)
            no_progress = check_for_no_progress(content)
            perf_issues = check_performance_issues(content)

            results = {
                "exists": True,
                "healthy": not (has_loop or repeated_errors or no_progress),
                "infinite_loop": has_loop,
                "attempts": attempts,
                "repeated_errors": repeated_errors,
                "no_progress": no_progress,
                "performance_issues": perf_issues,
            }
        else:
            # Read from file
            results = analyze_log_file(args.log_file)

        if not args.quiet:
            print_results(results)

        # Exit with appropriate code
        if results["healthy"]:
            sys.exit(0)
        else:
            if results["infinite_loop"]:
                print("\n❌ CRITICAL: Infinite loop detected")
                sys.exit(1)
            else:
                print("\n⚠️  WARNING: Issues detected but not critical")
                sys.exit(0)

    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
