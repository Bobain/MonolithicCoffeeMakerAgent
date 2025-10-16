"""Parse ROADMAP.md to extract tasks and priorities.

This module provides simple regex/markdown parsing to extract:
- Priority sections (PRIORITY 1, PRIORITY 2, etc.)
- Status (📝 Planned, 🔄 In Progress, ✅ Complete)
- Deliverables
- Dependencies

Example:
    >>> from coffee_maker.autonomous.roadmap_parser import RoadmapParser
    >>>
    >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
    >>> priorities = parser.get_priorities()
    >>> for p in priorities:
    ...     print(f"{p['name']}: {p['status']}")
    PRIORITY 1: Analytics & Observability: 🔄 MOSTLY COMPLETE
    PRIORITY 2: Roadmap Management CLI: 🔄 MVP PHASE 1 IN PROGRESS
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RoadmapParser:
    """Parse ROADMAP.md to extract tasks and priorities.

    This class provides simple parsing of the roadmap markdown to identify
    priorities, their status, and what needs to be done next.

    Attributes:
        roadmap_path: Path to ROADMAP.md
        content: Raw markdown content

    Example:
        >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        >>> next_task = parser.get_next_planned_priority()
        >>> if next_task:
        ...     print(f"Next: {next_task['name']}")
    """

    def __init__(self, roadmap_path: str):
        """Initialize parser with roadmap path.

        Args:
            roadmap_path: Path to ROADMAP.md file
        """
        self.roadmap_path = Path(roadmap_path)

        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        self.content = self.roadmap_path.read_text()
        logger.info(f"Loaded roadmap from {roadmap_path}")

    def get_priorities(self) -> List[Dict]:
        """Get all priorities from roadmap.

        Returns:
            List of priority dictionaries with:
                - name: Priority name (e.g., "PRIORITY 1: Analytics")
                - number: Priority number (e.g., 1)
                - title: Full title
                - status: Status emoji/text (e.g., "📝 Planned")
                - section_start: Line number where section starts
                - content: Full section content

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> priorities = parser.get_priorities()
            >>> len(priorities)
            7
        """
        priorities = []

        # Pattern to match priority headers
        # Example: ### 🔴 **PRIORITY 1: Analytics & Observability** ⚡ FOUNDATION
        pattern = r"^###\s+🔴\s+\*\*PRIORITY\s+(\d+(?:\.\d+)?):([^*]+)\*\*"

        lines = self.content.split("\n")

        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                priority_num = match.group(1)
                title = match.group(2).strip()

                # Look for status in next few lines
                status = self._extract_status(lines, i)

                # Extract full section content
                section_content = self._extract_section(lines, i)

                priorities.append(
                    {
                        "name": f"PRIORITY {priority_num}",
                        "number": priority_num,
                        "title": title,
                        "status": status,
                        "section_start": i,
                        "content": section_content,
                    }
                )

        logger.info(f"Found {len(priorities)} priorities")
        return priorities

    def _extract_status(self, lines: List[str], start_line: int) -> str:
        """Extract status from lines near priority header.

        Args:
            lines: All lines from roadmap
            start_line: Line number of priority header

        Returns:
            Status string (e.g., "📝 Planned", "🔄 In Progress")
        """
        # Look in next 10 lines for **Status**: pattern
        for i in range(start_line, min(start_line + 15, len(lines))):
            line = lines[i]
            if "**Status**:" in line:
                # Extract status after the colon
                status_match = re.search(r"\*\*Status\*\*:\s*(.+?)(?:\n|$)", line)
                if status_match:
                    return status_match.group(1).strip()

        return "Unknown"

    def _extract_section(self, lines: List[str], start_line: int) -> str:
        """Extract full section content until next priority or end.

        Args:
            lines: All lines from roadmap
            start_line: Line number of priority header

        Returns:
            Section content as string
        """
        section_lines = [lines[start_line]]

        # Continue until we hit another ### heading with PRIORITY
        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Stop at next priority section
            if line.startswith("### 🔴 **PRIORITY"):
                break

            # Stop at major section divider
            if line.startswith("## ") and not line.startswith("###"):
                break

            section_lines.append(line)

        return "\n".join(section_lines)

    def get_next_planned_priority(self) -> Optional[Dict]:
        """Get the next priority that is in Planned status.

        Returns:
            Priority dict or None if no planned priorities

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> next_task = parser.get_next_planned_priority()
            >>> if next_task:
            ...     print(f"Implement: {next_task['title']}")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            status = priority["status"].lower()
            if "planned" in status or "📝" in status:
                logger.info(f"Next planned priority: {priority['name']}")
                return priority

        logger.info("No planned priorities found")
        return None

    def get_in_progress_priorities(self) -> List[Dict]:
        """Get all priorities currently in progress.

        Returns:
            List of priority dictionaries

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> in_progress = parser.get_in_progress_priorities()
            >>> for p in in_progress:
            ...     print(f"Working on: {p['title']}")
        """
        priorities = self.get_priorities()

        in_progress = [p for p in priorities if "🔄" in p["status"] or "in progress" in p["status"].lower()]

        logger.info(f"Found {len(in_progress)} in-progress priorities")
        return in_progress

    def extract_deliverables(self, priority_name: str) -> List[str]:
        """Extract deliverables list from a priority section.

        Args:
            priority_name: Priority name (e.g., "PRIORITY 2")

        Returns:
            List of deliverable descriptions

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> deliverables = parser.extract_deliverables("PRIORITY 2")
            >>> for d in deliverables:
            ...     print(f"- {d}")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            if priority["name"] == priority_name:
                content = priority["content"]

                # Look for deliverables section
                deliverables = []
                lines = content.split("\n")

                in_deliverables = False
                for line in lines:
                    if "**Deliverables**" in line or "deliverables:" in line.lower():
                        in_deliverables = True
                        continue

                    if in_deliverables:
                        # Stop at next major heading
                        if line.startswith("**") and ":" in line and not line.startswith("- "):
                            break

                        # Extract list items
                        if line.strip().startswith("- [ ]") or line.strip().startswith("- "):
                            deliverable = line.strip()[2:].strip()  # Remove "- "
                            if deliverable.startswith("[ ] "):
                                deliverable = deliverable[4:]  # Remove "[ ] "
                            deliverables.append(deliverable)

                return deliverables

        return []

    def is_priority_complete(self, priority_name: str) -> bool:
        """Check if a priority is marked as complete.

        Args:
            priority_name: Priority name (e.g., "PRIORITY 1")

        Returns:
            True if complete, False otherwise

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> if parser.is_priority_complete("PRIORITY 1"):
            ...     print("PRIORITY 1 is done!")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            if priority["name"] == priority_name:
                status = priority["status"].lower()
                return "✅" in priority["status"] or "complete" in status

        return False

    def extract_estimated_time(self, priority_name: str) -> Optional[Dict]:
        """Extract estimated time from a priority section.

        Looks for patterns like:
        - **Estimated Effort**: 3-4 days
        - **Estimated Effort**: 3-5 days (description)
        - **Total Estimated**: 1-2 days (7-10 hours)

        Args:
            priority_name: Priority name (e.g., "PRIORITY 2", "US-015")

        Returns:
            Dictionary with min_days and max_days, or None if not found

        Example:
            >>> parser = RoadmapParser("docs/roadmap/ROADMAP.md")
            >>> estimate = parser.extract_estimated_time("US-015")
            >>> if estimate:
            ...     print(f"Estimated: {estimate['min_days']}-{estimate['max_days']} days")
            Estimated: 3-4 days
        """
        priorities = self.get_priorities()

        # Find priority by name (handle both "PRIORITY X" and "US-XXX" formats)
        priority_content = None
        for priority in priorities:
            if priority["name"] == priority_name or priority_name in priority["title"]:
                priority_content = priority["content"]
                break

        if not priority_content:
            # Try searching in full content (for US-XXX stories)
            # Look for US-XXX section headers
            us_pattern = rf"##\s+.*{re.escape(priority_name)}[:\s]"
            match = re.search(us_pattern, self.content, re.IGNORECASE)
            if match:
                # Extract section starting from match
                start_pos = match.start()
                # Find next ## heading or end of document
                next_section = re.search(r"\n##\s+", self.content[start_pos + 1 :])
                end_pos = start_pos + next_section.start() if next_section else len(self.content)
                priority_content = self.content[start_pos:end_pos]

        if not priority_content:
            logger.debug(f"Could not find content for {priority_name}")
            return None

        # Look for **Estimated Effort**: X-Y days pattern
        # Patterns to match:
        # - **Estimated Effort**: 3-4 days
        # - **Total Estimated**: 1-2 days
        # - **Estimated**: 3-5 days
        estimate_patterns = [
            r"\*\*Estimated Effort\*\*:\s*(\d+)-(\d+)\s*days?",
            r"\*\*Total Estimated\*\*:\s*(\d+)-(\d+)\s*days?",
            r"\*\*Estimated\*\*:\s*(\d+)-(\d+)\s*days?",
        ]

        for pattern in estimate_patterns:
            match = re.search(pattern, priority_content, re.IGNORECASE)
            if match:
                min_days = float(match.group(1))
                max_days = float(match.group(2))

                logger.info(f"Extracted estimate for {priority_name}: {min_days}-{max_days} days")

                return {
                    "min_days": min_days,
                    "max_days": max_days,
                    "avg_days": (min_days + max_days) / 2,
                }

        logger.debug(f"No estimate found for {priority_name}")
        return None
