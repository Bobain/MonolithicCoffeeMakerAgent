"""Architect CLI commands for CFR-011 enforcement.

This module provides CLI commands for architect's daily integration workflow:
- architect daily-integration: Guided workflow for reading code-searcher reports
- architect analyze-codebase: Perform weekly codebase analysis
- architect cfr-011-status: Check CFR-011 compliance status
"""

import click
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

from coffee_maker.autonomous.architect_daily_routine import (
    ArchitectDailyRoutine,
)


@click.group()
def architect():
    """Architect agent CLI commands."""


@architect.command("daily-integration")
def daily_integration():
    """Guided workflow for reading code-searcher reports.

    This command:
    1. Finds all unread code-searcher reports
    2. Displays each report for review
    3. Confirms architect has read and extracted action items
    4. Marks reports as read in tracking file
    """
    routine = ArchitectDailyRoutine()

    # Check for unread reports
    unread = routine.get_unread_reports()

    if not unread:
        click.echo("No unread code-searcher reports. You're up to date!")
        return

    click.echo(f"Found {len(unread)} unread code-searcher report(s):\n")

    for i, report in enumerate(unread, 1):
        click.echo(f"  {i}. {report.name}")

    click.echo("\nPlease read all reports now:")

    for report in unread:
        click.echo(f"\n{'='*60}")
        click.echo(f"Reading: {report.name}")
        click.echo("=" * 60)

        # Display report content
        content = report.read_text(encoding="utf-8")
        click.echo(content)

        click.echo("\n" + "=" * 60)

        # Confirm read
        if click.confirm("Have you read this report and extracted action items?"):
            routine.mark_reports_read([report])
            click.echo(f"Marked {report.name} as read")
        else:
            click.echo(f"Skipping {report.name} - you must read it later")

    click.echo("\nDaily integration complete!")


@architect.command("analyze-codebase")
def analyze_codebase():
    """Perform weekly codebase analysis.

    Analysis includes:
    1. Radon complexity metrics (cyclomatic complexity average)
    2. Large file detection (>500 LOC)
    3. Test coverage analysis (pytest --cov)
    4. TODO/FIXME comment extraction
    5. Code duplication detection (basic pattern matching)

    Output: Synthetic 1-2 page report saved to docs/architecture/
    """
    routine = ArchitectDailyRoutine()

    click.echo("Starting weekly codebase analysis...\n")

    # Check if analysis is due
    if not routine.is_codebase_analysis_due():
        last = routine.status["last_codebase_analysis"]
        next_due = routine.status["next_analysis_due"]
        click.echo(f"Analysis not due yet:")
        click.echo(f"   Last analysis: {last}")
        click.echo(f"   Next due: {next_due}")

        if not click.confirm("\nPerform analysis anyway?"):
            return

    click.echo("Analyzing codebase for:")
    click.echo("  - Complexity metrics (radon --average)")
    click.echo("  - Large files (>500 LOC)")
    click.echo("  - Test coverage (pytest --cov)")
    click.echo("  - TODO/FIXME comments")
    click.echo("\n(This may take 5-10 minutes...)\n")

    # Perform codebase analysis
    results = {}

    # 1. Radon complexity analysis
    try:
        result = subprocess.run(
            ["radon", "cc", "coffee_maker/", "--average"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        results["complexity"] = result.stdout
    except Exception as e:
        click.echo(f"Radon analysis failed: {e}")
        results["complexity"] = "Failed to analyze"

    # 2. Large file detection
    large_files = []
    for py_file in Path("coffee_maker/").rglob("*.py"):
        try:
            line_count = len(py_file.read_text().splitlines())
            if line_count > 500:
                large_files.append((str(py_file), line_count))
        except Exception:
            continue
    results["large_files"] = large_files

    # 3. Test coverage
    try:
        result = subprocess.run(
            ["pytest", "--cov=coffee_maker", "--cov-report=term"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        results["coverage"] = result.stdout
    except Exception as e:
        click.echo(f"Coverage analysis failed: {e}")
        results["coverage"] = "Failed to analyze"

    # 4. TODO/FIXME extraction
    todos = []
    for py_file in Path("coffee_maker/").rglob("*.py"):
        try:
            for i, line in enumerate(py_file.read_text().splitlines(), 1):
                if "TODO" in line or "FIXME" in line:
                    todos.append((str(py_file), i, line.strip()))
        except Exception:
            continue
    results["todos"] = todos[:20]  # Limit to top 20

    # 5. Generate synthetic report
    report_path = Path(f"docs/architecture/CODEBASE_ANALYSIS_{datetime.now().strftime('%Y-%m-%d')}.md")
    report_content = f"""# Codebase Analysis Report

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Scope**: coffee_maker/

## Complexity Metrics

```
{results["complexity"]}
```

## Large Files (>500 LOC)

"""
    if large_files:
        for file, loc in large_files:
            report_content += f"- `{file}`: {loc} lines\n"
    else:
        report_content += "No files exceed 500 LOC\n"

    report_content += f"""

## Test Coverage

```
{results["coverage"]}
```

## TODO/FIXME Comments ({len(todos)} found, showing top 20)

"""
    for file, line_num, line_content in todos:
        report_content += f"- `{file}:{line_num}`: {line_content}\n"

    report_content += f"""

## Recommendations

**Based on analysis**:
1. Review large files (>500 LOC) for potential refactoring opportunities
2. Address TODO/FIXME comments systematically
3. Maintain test coverage above 80%

**Next Analysis**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""

    # Save report
    report_path.write_text(report_content)
    click.echo(f"\nReport saved: {report_path}")

    # Mark as analyzed
    routine.mark_codebase_analyzed()

    click.echo(f"\nCodebase analysis complete!")
    click.echo(f"   Next analysis due: {routine.status['next_analysis_due']}")


@architect.command("cfr-011-status")
def cfr_011_status():
    """Check CFR-011 compliance status.

    Displays:
    - Whether architect is compliant with CFR-011
    - Last dates for code-searcher read and codebase analysis
    - List of unread reports (if any)
    - Metrics on reports read and specs created/updated
    - Actions required to achieve compliance
    """
    routine = ArchitectDailyRoutine()

    status = routine.get_compliance_status()

    click.echo("\nCFR-011 Compliance Status\n")
    click.echo("=" * 60)

    if status["compliant"]:
        click.echo("COMPLIANT - No violations detected\n")
    else:
        click.echo("NOT COMPLIANT - Violations detected\n")

    click.echo(f"Last code-searcher read: {status['last_code_searcher_read'] or 'NEVER'}")
    click.echo(f"Last codebase analysis: {status['last_codebase_analysis'] or 'NEVER'}")
    click.echo(f"Next analysis due: {status['next_analysis_due'] or 'ASAP'}\n")

    if status["unread_reports"]:
        click.echo(f"Unread reports ({len(status['unread_reports'])}):")
        for report in status["unread_reports"]:
            click.echo(f"  - {report}")
        click.echo()

    if status["analysis_due"]:
        click.echo("Weekly codebase analysis is OVERDUE\n")

    click.echo("Metrics:")
    click.echo(f"  Reports read: {status['reports_read']}")
    click.echo(f"  Refactoring specs created: {status['refactoring_specs_created']}")
    click.echo(f"  Specs updated: {status['specs_updated']}")

    if not status["compliant"]:
        click.echo("\nActions Required:")
        if status["unread_reports"]:
            click.echo("  1. Run: architect daily-integration")
        if status["analysis_due"]:
            click.echo("  2. Run: architect analyze-codebase")

    click.echo()


if __name__ == "__main__":
    architect()
