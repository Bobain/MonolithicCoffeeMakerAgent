"""Bug Ticket Markdown Parser.

Parses existing BUG-*.md files and imports them into the database.
Useful for migrating from file-only system to database-backed system.

Usage:
    >>> from bug_parser import BugTicketParser
    >>> parser = BugTicketParser()
    >>> bug_data = parser.parse_ticket('tickets/BUG-001.md')
    >>> print(bug_data['title'], bug_data['status'], bug_data['priority'])
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class BugTicketParser:
    """Parser for BUG-*.md markdown files."""

    def parse_ticket(self, ticket_path: Path) -> Dict:
        """Parse a bug ticket markdown file.

        Args:
            ticket_path: Path to BUG-*.md file

        Returns:
            Dict with parsed bug data
        """
        if not ticket_path.exists():
            raise FileNotFoundError(f"Ticket not found: {ticket_path}")

        content = ticket_path.read_text()

        # Extract bug number from filename
        bug_number_match = re.search(r"BUG-(\d+)", ticket_path.name)
        bug_number = int(bug_number_match.group(1)) if bug_number_match else 0

        # Extract title from first heading
        title_match = re.search(r"# BUG-\d+:\s*(.+)", content)
        title = title_match.group(1).strip() if title_match else "Unknown"

        # Extract metadata fields
        status = self._extract_field(content, "Status")
        priority = self._extract_field(content, "Priority")
        created_at = self._extract_field(content, "Created")
        reporter = self._extract_field(content, "Reporter")
        assigned_to = self._extract_field(content, "Assigned")
        category = self._extract_field(content, "Category")

        # Clean status (remove emoji)
        if status:
            status = re.sub(r"[🔴🔍🟡🧪✅⚫]", "", status).strip().lower().replace(" ", "_")

        # Extract sections
        description = self._extract_section(content, "Description")
        reproduction_steps = self._extract_list(content, "Reproduction Steps")
        expected_behavior = self._extract_section(content, "Expected Behavior")
        actual_behavior = self._extract_section(content, "Actual Behavior")
        root_cause = self._extract_section(content, "Root Cause")
        analysis = self._extract_section(content, "Analysis")
        technical_spec = self._extract_section(content, "Technical Spec")
        implementation = self._extract_section(content, "Implementation")
        testing_results = self._extract_section(content, "Testing Results")

        # Extract test info
        test_file = self._extract_test_field(content, "Test File")
        test_name = self._extract_test_field(content, "Test Name")

        # Extract PR link
        pr_url = self._extract_pr_link(content)

        return {
            "bug_number": bug_number,
            "title": title,
            "status": status or "open",
            "priority": priority or "Medium",
            "created_at": created_at or "",
            "reporter": reporter or "Unknown",
            "assigned_to": assigned_to or "code_developer",
            "category": category,
            "description": description,
            "reproduction_steps": reproduction_steps,
            "expected_behavior": expected_behavior,
            "actual_behavior": actual_behavior,
            "root_cause": root_cause,
            "analysis": analysis,
            "technical_spec": technical_spec,
            "implementation": implementation,
            "testing_results": testing_results,
            "test_file_path": test_file,
            "test_name": test_name,
            "pr_url": pr_url,
            "ticket_file_path": str(ticket_path),
        }

    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract metadata field value (e.g., **Status**: Open)."""
        pattern = rf"\*\*{field_name}\*\*:\s*(.+)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract content from a markdown section."""
        # Match section header and capture content until next ## or end
        pattern = rf"## {section_name}\n\n(.+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return None

        section_content = match.group(1).strip()

        # Remove placeholder text
        placeholders = [
            "_To be determined during analysis_",
            "_To be filled by code_developer_",
            "_Phase",
        ]

        for placeholder in placeholders:
            if placeholder in section_content:
                return None

        return section_content if section_content else None

    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract numbered or bulleted list from a section."""
        section = self._extract_section(content, section_name)

        if not section:
            return []

        # Extract list items (numbered or bulleted)
        items = []
        for line in section.split("\n"):
            # Match "1. item" or "- item" or "* item"
            match = re.match(r"^(?:\d+\.|-|\*)\s+(.+)", line.strip())
            if match:
                items.append(match.group(1).strip())

        return items

    def _extract_test_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract test field from Regression Test section."""
        # Find Regression Test section
        regression_match = re.search(r"## Regression Test\n\n(.+?)(?=\n##|\Z)", content, re.DOTALL)

        if not regression_match:
            return None

        regression_section = regression_match.group(1)

        # Extract field
        pattern = rf"\*\*{field_name}\*\*:\s*`?([^`\n]+)`?"
        match = re.search(pattern, regression_section)

        if not match:
            return None

        value = match.group(1).strip()

        # Filter out placeholders
        if value.startswith("_") or value == "TBD":
            return None

        return value

    def _extract_pr_link(self, content: str) -> Optional[str]:
        """Extract PR URL from PR Link section."""
        # Match GitHub PR URLs
        pattern = r"https://github\.com/[\w-]+/[\w-]+/pull/\d+"
        match = re.search(pattern, content)
        return match.group(0) if match else None

    def import_all_tickets(self, tickets_dir: Path, bug_skill) -> Dict[str, int]:
        """Import all BUG-*.md files into database.

        Args:
            tickets_dir: Directory containing BUG-*.md files
            bug_skill: BugTrackingSkill instance

        Returns:
            Dict with import stats: {"imported": 5, "skipped": 2, "errors": 0}
        """
        stats = {"imported": 0, "skipped": 0, "errors": 0}

        for ticket_file in sorted(tickets_dir.glob("BUG-*.md")):
            try:
                # Parse ticket
                bug_data = self.parse_ticket(ticket_file)

                # Check if already in database
                existing = bug_skill.get_bug_by_number(bug_data["bug_number"])

                if existing:
                    stats["skipped"] += 1
                    continue

                # Import to database
                # Note: This uses the internal database connection directly
                # to avoid re-creating markdown files

                import sqlite3
                from datetime import datetime

                db_path = bug_skill.db_path

                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO bugs (
                            bug_number, title, description, priority, status, category,
                            reporter, assigned_to, created_at, updated_at,
                            reproduction_steps, expected_behavior, actual_behavior,
                            root_cause, test_file_path, test_name, pr_url, ticket_file_path
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            bug_data["bug_number"],
                            bug_data["title"],
                            bug_data["description"],
                            bug_data["priority"],
                            bug_data["status"],
                            bug_data["category"],
                            bug_data["reporter"],
                            bug_data["assigned_to"],
                            bug_data["created_at"] or datetime.now().isoformat(),
                            datetime.now().isoformat(),
                            None,  # reproduction_steps as JSON
                            bug_data["expected_behavior"],
                            bug_data["actual_behavior"],
                            bug_data["root_cause"],
                            bug_data["test_file_path"],
                            bug_data["test_name"],
                            bug_data["pr_url"],
                            bug_data["ticket_file_path"],
                        ),
                    )
                    conn.commit()

                stats["imported"] += 1

            except Exception as e:
                print(f"Error importing {ticket_file}: {e}")
                stats["errors"] += 1

        return stats
