"""CFR-011: Architect Daily Integration Enforcement

Enforces the requirement that architect reads code-searcher analysis reports
daily and performs codebase analysis weekly before creating new specs.

This module implements the ArchitectDailyRoutine class which:
1. Tracks when code-searcher reports were last read
2. Tracks when codebase analysis was last performed
3. Raises CFR011ViolationError if violations are detected
4. Provides workflows for daily integration and weekly analysis
"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any


class CFR011ViolationError(Exception):
    """Raised when CFR-011 requirements are violated.

    CFR-011 requires:
    1. Daily reading of code-searcher analysis reports
    2. Weekly (minimum) codebase analysis by architect

    This exception includes clear guidance on what needs to be done.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ArchitectDailyRoutine:
    """Enforces CFR-011 daily integration workflow.

    Ensures architect integrates code-searcher findings daily and performs
    codebase analysis weekly. Tracks dates and prevents spec creation if
    requirements are not met.

    Attributes:
        status_file: Path to architect_integration_status.json tracking file
        docs_dir: Path to /docs directory where code-searcher reports are stored
    """

    def __init__(self, status_file: Optional[Path] = None, docs_dir: Optional[Path] = None):
        """Initialize ArchitectDailyRoutine.

        Args:
            status_file: Path to tracking file (default: data/architect_integration_status.json)
            docs_dir: Path to docs directory (default: docs/)
        """
        if status_file is None:
            status_file = Path(
                "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/data/architect_integration_status.json"
            )
        if docs_dir is None:
            docs_dir = Path("/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs")

        self.status_file = status_file
        self.docs_dir = docs_dir
        self._status = self._load_status()

    def _load_status(self) -> Dict[str, Any]:
        """Load tracking file or create new one.

        Returns:
            Dict with tracking data including dates and reports read
        """
        if not self.status_file.exists():
            return {
                "last_code_searcher_read": None,
                "last_codebase_analysis": None,
                "reports_read": [],
                "action_items_total": 0,
                "specs_created": 0,
                "specs_updated": 0,
                "next_analysis_due": None,
            }

        with open(self.status_file, "r") as f:
            return json.load(f)

    def _save_status(self) -> None:
        """Save tracking file to disk."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, "w") as f:
            json.dump(self._status, f, indent=2)

    def _find_new_code_searcher_reports(self) -> List[str]:
        """Find unread code-searcher analysis reports.

        Looks for files matching patterns:
        - *AUDIT*.md
        - *ANALYSIS*.md
        - CODEBASE_ANALYSIS_SUMMARY*.md

        Returns:
            List of unread report filenames
        """
        if not self.docs_dir.exists():
            return []

        patterns = [
            "*AUDIT*.md",
            "*ANALYSIS*.md",
            "CODEBASE_ANALYSIS_SUMMARY*.md",
        ]

        reports = []
        for pattern in patterns:
            for file_path in self.docs_dir.glob(pattern):
                if file_path.is_file():
                    reports.append(file_path.name)

        # Remove duplicates and filter to only unread reports
        reports = list(set(reports))
        reports_read = set(self._status.get("reports_read", []))
        unread = [r for r in reports if r not in reports_read]

        return sorted(unread)

    def _has_read_reports(self, reports: List[str]) -> bool:
        """Check if all given reports have been marked as read.

        Args:
            reports: List of report filenames to check

        Returns:
            True if all reports are in reports_read list
        """
        reports_read = set(self._status.get("reports_read", []))
        return all(r in reports_read for r in reports)

    def _mark_reports_read(self, reports: Optional[List[str]] = None) -> None:
        """Mark reports as read and update last_read date.

        Args:
            reports: List of report filenames to mark as read.
                    If None, marks today as last_read.
        """
        today = date.today().isoformat()

        if reports:
            current_read = set(self._status.get("reports_read", []))
            current_read.update(reports)
            self._status["reports_read"] = sorted(list(current_read))

        self._status["last_code_searcher_read"] = today
        self._save_status()

    def _mark_codebase_analysis_complete(self) -> None:
        """Mark codebase analysis as complete for today."""
        today = date.today().isoformat()
        next_due = (date.today() + timedelta(days=7)).isoformat()

        self._status["last_codebase_analysis"] = today
        self._status["next_analysis_due"] = next_due
        self._save_status()

    def get_last_code_searcher_read(self) -> Optional[date]:
        """Get the date code-searcher reports were last read.

        Returns:
            date object or None if never read
        """
        date_str = self._status.get("last_code_searcher_read")
        if date_str is None:
            return None
        return datetime.fromisoformat(date_str).date()

    def get_last_codebase_analysis(self) -> Optional[date]:
        """Get the date codebase was last analyzed.

        Returns:
            date object or None if never analyzed
        """
        date_str = self._status.get("last_codebase_analysis")
        if date_str is None:
            return None
        return datetime.fromisoformat(date_str).date()

    def enforce_cfr_011(self) -> None:
        """Enforce CFR-011 requirements before allowing spec creation.

        Checks:
        1. If new code-searcher reports exist today and haven't been read
        2. If >7 days since last codebase analysis

        Raises:
            CFR011ViolationError: If any requirement is violated
        """
        today = date.today()

        # Part 1: Check code-searcher reports
        last_read = self.get_last_code_searcher_read()
        if last_read is None or last_read < today:
            new_reports = self._find_new_code_searcher_reports()
            if new_reports:
                reports_list = "\n".join(f"  - {r}" for r in new_reports)
                raise CFR011ViolationError(
                    f"CFR-011 VIOLATION: Must read {len(new_reports)} new code-searcher "
                    f"report(s) before creating specs today.\n\n"
                    f"Reports to read:\n{reports_list}\n\n"
                    f"Command: architect daily-integration"
                )

        # Part 2: Check codebase analysis frequency
        last_analysis = self.get_last_codebase_analysis()
        if last_analysis is None:
            raise CFR011ViolationError(
                "CFR-011 VIOLATION: Codebase has never been analyzed.\n\n"
                "Must analyze codebase before creating new specs.\n"
                "Command: architect analyze-codebase"
            )

        days_since_analysis = (today - last_analysis).days
        if days_since_analysis > 7:
            raise CFR011ViolationError(
                f"CFR-011 VIOLATION: {days_since_analysis} days since last "
                f"codebase analysis (max: 7 days).\n\n"
                f"Must analyze codebase yourself before creating new specs.\n"
                f"Command: architect analyze-codebase"
            )

    def mark_daily_integration_complete(self) -> None:
        """Mark daily integration workflow as complete.

        Call this after reviewing code-searcher reports and updating specs.
        """
        reports = self._find_new_code_searcher_reports()
        self._mark_reports_read(reports)

    def mark_codebase_analysis_complete(self) -> None:
        """Mark weekly codebase analysis as complete.

        Call this after manually analyzing the codebase and creating
        any necessary refactoring specs.
        """
        self._mark_codebase_analysis_complete()

    def get_status_summary(self) -> str:
        """Get human-readable status summary.

        Returns:
            Formatted string with current status
        """
        last_read = self.get_last_code_searcher_read()
        last_analysis = self.get_last_codebase_analysis()
        today = date.today()

        lines = [
            "Architect Daily Integration Status (CFR-011)",
            "=" * 60,
        ]

        if last_read:
            days_ago = (today - last_read).days
            lines.append(f"Last code-searcher read: {last_read} ({days_ago} days ago)")
        else:
            lines.append("Last code-searcher read: Never")

        if last_analysis:
            days_ago = (today - last_analysis).days
            if isinstance(last_analysis, datetime):
                last_analysis = last_analysis.date()
            next_due = last_analysis + timedelta(days=7)
            lines.append(f"Last codebase analysis: {last_analysis} ({days_ago} days ago)")
            lines.append(f"Next analysis due: {next_due}")
        else:
            lines.append("Last codebase analysis: Never")

        reports_read = self._status.get("reports_read", [])
        if reports_read:
            lines.append(f"\nReports read ({len(reports_read)}):")
            for report in reports_read[-5:]:  # Show last 5
                lines.append(f"  - {report}")

        return "\n".join(lines)

    def get_unread_reports(self) -> List[str]:
        """Get list of unread code-searcher reports.

        Returns:
            List of unread report filenames
        """
        return self._find_new_code_searcher_reports()
