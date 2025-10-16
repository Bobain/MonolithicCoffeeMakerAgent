"""Technical Spec Review Report Generator (US-047 Phase 2).

This module provides a SpecReviewReport class that scans the ROADMAP and
checks which priorities have technical specifications created by the architect.

The report shows:
- Total priorities in ROADMAP
- Which priorities have specs (and where)
- Which priorities are missing specs
- Suggested action for architect

This enables architect to see at a glance which specs need to be created
before code_developer can implement the priorities (CFR-008 enforcement).

Classes:
    SpecReviewReport: Generate and display spec coverage report

Usage:
    >>> report_gen = SpecReviewReport()
    >>> report = report_gen.generate_report()
    >>> print(report)

    # In CLI:
    $ project-manager spec-review
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from coffee_maker.autonomous.roadmap_parser import RoadmapParser

logger = logging.getLogger(__name__)


class SpecReviewReport:
    """Generate technical spec coverage report for architect.

    Attributes:
        roadmap_path: Path to ROADMAP.md
        spec_dir: Path to docs/architecture/specs/
        priorities: Parsed priorities from ROADMAP
        spec_coverage: Dict mapping priority name to spec path (if exists)
    """

    def __init__(self, roadmap_path: Optional[str] = None):
        """Initialize spec review report.

        Args:
            roadmap_path: Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)
        """
        if roadmap_path is None:
            roadmap_path = "docs/roadmap/ROADMAP.md"

        self.roadmap_path = Path(roadmap_path)
        self.spec_dir = self.roadmap_path.parent.parent / "architecture" / "specs"

        # Parse roadmap to get priorities
        self.parser = RoadmapParser(str(self.roadmap_path))
        self.priorities = []
        self.spec_coverage = {}

        logger.debug(f"SpecReviewReport initialized: roadmap={self.roadmap_path}, specs={self.spec_dir}")

    def _load_priorities(self) -> List[Dict]:
        """Load all priorities from ROADMAP.

        Returns:
            List of priority dictionaries with name, title, status
        """
        try:
            # Get all priorities (including completed, in-progress, planned)
            all_priorities = self.parser.get_priorities()
            return all_priorities
        except Exception as e:
            logger.error(f"Failed to load priorities: {e}")
            return []

    def _get_spec_path(self, priority: Dict) -> Optional[Path]:
        """Get expected spec file path for priority.

        Args:
            priority: Priority dictionary with name and title

        Returns:
            Path object if spec exists, None otherwise
        """
        priority_name = priority.get("name", "")
        priority.get("title", "")

        # Extract spec prefix from priority name
        if priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]
            spec_prefix = f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                major, minor = priority_num.split(".")
                spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
            else:
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        else:
            spec_prefix = f"SPEC-{priority_name.replace(' ', '-')}"

        # Check if spec exists
        if self.spec_dir.exists():
            for spec_file in self.spec_dir.glob(f"{spec_prefix}-*.md"):
                return spec_file

        return None

    def _check_spec_exists(self, priority: Dict) -> bool:
        """Check if technical spec exists for priority.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists, False otherwise
        """
        return self._get_spec_path(priority) is not None

    def generate_report(self) -> str:
        """Generate markdown spec coverage report.

        Returns:
            Markdown-formatted report string
        """
        # Load priorities
        self.priorities = self._load_priorities()

        # Build spec coverage
        specs_exist = []
        specs_missing = []

        for priority in self.priorities:
            spec_path = self._get_spec_path(priority)
            if spec_path:
                specs_exist.append((priority, spec_path))
            else:
                specs_missing.append(priority)

        # Build report
        report = "# Technical Spec Coverage Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Summary
        total = len(self.priorities)
        with_specs = len(specs_exist)
        without_specs = len(specs_missing)
        coverage_pct = int((with_specs / total) * 100) if total > 0 else 0

        report += "## Summary\n\n"
        report += f"- **Total Priorities**: {total}\n"
        report += f"- **Specs Exist**: {with_specs} ({coverage_pct}%)\n"
        report += f"- **Specs Missing**: {without_specs}\n"
        report += f"- **Coverage**: {coverage_pct}%\n\n"

        # Coverage details table
        report += "## Coverage Details\n\n"
        report += "| Priority | Title | Spec Status | File | Action |\n"
        report += "|----------|-------|-------------|------|--------|\n"

        for priority, spec_path in specs_exist:
            name = priority.get("name", "Unknown")
            title = priority.get("title", "")[:40]
            file_name = spec_path.name
            report += f"| {name} | {title} | ✅ Exists | `{file_name}` | N/A |\n"

        for priority in specs_missing:
            name = priority.get("name", "Unknown")
            title = priority.get("title", "")[:40]
            status = priority.get("status", "")
            report += f"| {name} | {title} | ❌ Missing | — | architect CREATE |\n"

        # Priorities needing specs
        if specs_missing:
            report += f"\n## Priorities Needing Specs ({without_specs})\n\n"

            for i, priority in enumerate(specs_missing, 1):
                name = priority.get("name", "Unknown")
                title = priority.get("title", "No title")
                status = priority.get("status", "Unknown")

                # Extract spec prefix
                if name.startswith("US-"):
                    spec_number = name.split("-")[1]
                    spec_prefix = f"SPEC-{spec_number}"
                elif name.startswith("PRIORITY"):
                    priority_num = name.replace("PRIORITY", "").strip()
                    if "." in priority_num:
                        major, minor = priority_num.split(".")
                        spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
                    else:
                        spec_prefix = f"SPEC-{priority_num.zfill(3)}"
                else:
                    spec_prefix = f"SPEC-{name.replace(' ', '-')}"

                report += f"{i}. **{name}**: {title}\n"
                report += f"   - Status: {status}\n"
                report += f"   - Spec prefix: `{spec_prefix}-<descriptive-name>.md`\n"
                report += f"   - Path: `docs/architecture/specs/{spec_prefix}-*.md`\n\n"

        # CFR-008 enforcement notice
        report += "\n## CFR-008 Enforcement (Architect-Only Spec Creation)\n\n"
        report += "**IMPORTANT**: Per CFR-008, ONLY architect can create technical specifications.\n\n"
        report += "- code_developer will **BLOCK** if spec is missing (does NOT create)\n"
        report += "- User notified (CRITICAL alert) when spec missing\n"
        report += "- architect must create spec BEFORE code_developer can implement\n\n"

        # Recommendations
        report += "## Architect Action Items\n\n"
        if specs_missing:
            report += f"**{without_specs} spec(s) need to be created:**\n\n"
            for priority in specs_missing:
                name = priority.get("name", "Unknown")
                title = priority.get("title", "No title")
                report += f"- [ ] {name}: {title}\n"
        else:
            report += "✅ **All priorities have technical specifications!**\n\n"
            report += "No action needed. code_developer can implement any priority.\n"

        report += "\n---\n"
        report += f"Generated by spec-review report | Total priorities: {total}\n"

        return report

    def print_report(self) -> None:
        """Print report to stdout."""
        report = self.generate_report()
        print(report)

    def save_report(self, output_path: Optional[str] = None) -> Optional[Path]:
        """Save report to file.

        Args:
            output_path: Path to save report (optional)

        Returns:
            Path to saved report file
        """
        if output_path is None:
            output_path = Path.home() / ".coffee_maker" / "spec_coverage_report.md"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            report = self.generate_report()
            output_path.write_text(report)
            logger.info(f"Spec review report saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save spec review report: {e}")
            return None


def cmd_spec_review(args) -> int:
    """CLI command handler for spec-review.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager spec-review
        $ project-manager spec-review --save
    """
    try:
        report_gen = SpecReviewReport()

        # Generate report
        report = report_gen.generate_report()

        # Display
        print("\n" + "=" * 80)
        print("TECHNICAL SPEC COVERAGE REPORT")
        print("=" * 80 + "\n")
        print(report)

        # Optionally save
        if hasattr(args, "save") and args.save:
            saved_path = report_gen.save_report()
            if saved_path:
                print(f"\n✅ Report saved to: {saved_path}")

        return 0

    except Exception as e:
        logger.error(f"Spec review failed: {e}", exc_info=True)
        print(f"\n❌ Error generating spec review: {e}")
        return 1


if __name__ == "__main__":
    # Quick test
    report = SpecReviewReport()
    report.print_report()
