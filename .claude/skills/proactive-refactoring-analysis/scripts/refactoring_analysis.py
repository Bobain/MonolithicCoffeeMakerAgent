#!/usr/bin/env python3
"""
Proactive Refactoring Analysis Skill Entry Point

This script serves as the entry point for the proactive-refactoring-analysis skill.
It analyzes the codebase for refactoring opportunities and generates a comprehensive report.

Usage:
    python refactoring_analysis.py [--codebase-path PATH] [--output-dir DIR]

Examples:
    # Analyze current codebase
    python refactoring_analysis.py

    # Analyze specific codebase
    python refactoring_analysis.py --codebase-path /path/to/project

    # Save report to specific directory
    python refactoring_analysis.py --output-dir /path/to/reports
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add coffee_maker to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from coffee_maker.skills.refactoring_analysis.proactive_refactoring_analysis import main


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Proactive Refactoring Analysis Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current codebase
  %(prog)s

  # Analyze specific codebase
  %(prog)s --codebase-path /path/to/project

  # Save report to specific directory
  %(prog)s --output-dir /path/to/reports

Report will be saved to: evidence/refactoring-analysis-YYYYMMDD-HHMMSS.md
        """,
    )

    parser.add_argument(
        "--codebase-path",
        type=Path,
        default=Path.cwd(),
        help="Path to codebase root (default: current directory)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for report (default: codebase_path/evidence)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args()


def main_entry_point():
    """Main entry point for the skill."""
    args = parse_arguments()

    codebase_path = args.codebase_path.resolve()

    if not codebase_path.exists():
        print(f"Error: Codebase path does not exist: {codebase_path}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"🔍 Analyzing codebase: {codebase_path}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run analysis
        report = main(codebase_path=codebase_path)

        if args.verbose:
            print(f"✅ Analysis complete!")
            print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Determine output directory
        if args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = codebase_path / "evidence"

        # Find the generated report
        timestamp = datetime.now().strftime("%Y%m%d")
        report_files = list(output_dir.glob(f"refactoring-analysis-{timestamp}-*.md"))

        if report_files:
            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
            print(f"📊 Report saved to: {latest_report}")

            if args.verbose:
                # Show summary
                content = latest_report.read_text()
                lines = content.split("\n")
                for line in lines[:30]:  # First 30 lines (Executive Summary)
                    print(line)
        else:
            print(f"⚠️  Report generated but not found in expected location: {output_dir}")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_entry_point()
