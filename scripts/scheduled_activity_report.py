#!/usr/bin/env python3
"""Scheduled Activity Report Generator.

This script generates activity summaries at scheduled times (2AM, 4AM, 6AM).
Designed to be run via cron or other scheduling mechanism.

Usage:
    python scripts/scheduled_activity_report.py

Cron Setup:
    # Edit crontab
    crontab -e

    # Add these lines (adjust path as needed)
    0 2 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run python scripts/scheduled_activity_report.py
    0 4 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run python scripts/scheduled_activity_report.py
    0 6 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run python scripts/scheduled_activity_report.py

Related:
    .claude/skills/orchestrator/activity-summary/SKILL.md
    coffee_maker/orchestrator/activity_summary.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.orchestrator.activity_summary import generate_activity_summary


def main():
    """Generate scheduled activity report."""
    timestamp = datetime.now()
    print(f"[{timestamp}] Generating scheduled activity report...")

    try:
        # Generate report for last 2 hours (time since last report)
        report = generate_activity_summary(time_window=2, save_to_file=True)

        print(f"[{timestamp}] ✅ Activity report generated successfully")
        print(f"[{timestamp}] Report saved to evidence/")
        print(f"[{timestamp}] Notification created for user")

        return 0

    except Exception as e:
        print(f"[{timestamp}] ❌ Error generating report: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
