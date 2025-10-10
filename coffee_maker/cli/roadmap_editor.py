"""Roadmap Editor - Safe manipulation of ROADMAP.md with validation and backups.

This module provides safe editing capabilities for ROADMAP.md including:
- Atomic writes with automatic backups
- Priority validation
- Summary extraction
- Safe updates with regex patterns

Example:
    >>> from coffee_maker.cli.roadmap_editor import RoadmapEditor
    >>> from coffee_maker.config import ROADMAP_PATH
    >>>
    >>> editor = RoadmapEditor(ROADMAP_PATH)
    >>> editor.add_priority(
    ...     priority_number="PRIORITY 10",
    ...     title="User Authentication",
    ...     duration="2-3 weeks",
    ...     impact="⭐⭐⭐⭐⭐",
    ...     status="📝 Planned"
    ... )
    >>> summary = editor.get_priority_summary()
    >>> print(f"Total priorities: {summary['total']}")
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import logging

logger = logging.getLogger(__name__)


class RoadmapEditor:
    """Safe editor for ROADMAP.md with validation and backups.

    This class provides methods to safely manipulate the ROADMAP.md file
    with automatic backups, validation, and atomic writes.

    Attributes:
        roadmap_path: Path to ROADMAP.md file
        backup_dir: Directory for backup files

    Example:
        >>> editor = RoadmapEditor(Path("docs/ROADMAP.md"))
        >>> success = editor.add_priority(
        ...     priority_number="PRIORITY 10",
        ...     title="New Feature",
        ...     duration="1 week",
        ...     impact="⭐⭐⭐",
        ...     status="📝 Planned"
        ... )
    """

    def __init__(self, roadmap_path: Path):
        """Initialize RoadmapEditor.

        Args:
            roadmap_path: Path to ROADMAP.md file
        """
        self.roadmap_path = Path(roadmap_path)
        self.backup_dir = self.roadmap_path.parent / "roadmap_backups"
        self.backup_dir.mkdir(exist_ok=True)

        logger.info(f"RoadmapEditor initialized for {self.roadmap_path}")

    def add_priority(
        self,
        priority_number: str,
        title: str,
        duration: str,
        impact: str,
        status: str = "📝 Planned",
        description: str = "",
        deliverables: Optional[List[str]] = None,
    ) -> bool:
        """Add new priority to roadmap.

        Creates a backup before adding the priority. Validates that the priority
        number is unique and properly formatted.

        Args:
            priority_number: e.g., "PRIORITY 10" or "PRIORITY 2.5"
            title: Priority title
            duration: e.g., "2-3 weeks"
            impact: Stars, e.g., "⭐⭐⭐⭐⭐"
            status: Status emoji + text (default: "📝 Planned")
            description: Full description (optional)
            deliverables: List of deliverables (optional)

        Returns:
            True if successful

        Raises:
            ValueError: If priority number is invalid or already exists
            IOError: If file operations fail

        Example:
            >>> editor.add_priority(
            ...     priority_number="PRIORITY 10",
            ...     title="Rate Limiting",
            ...     duration="1-2 weeks",
            ...     impact="⭐⭐⭐⭐",
            ...     status="📝 Planned",
            ...     deliverables=["Implement rate limiter", "Add tests"]
            ... )
            True
        """
        try:
            # Create backup
            self._create_backup()

            # Read current roadmap
            content = self.roadmap_path.read_text()

            # Validate priority number
            if not self._validate_priority_number(priority_number, content):
                raise ValueError(f"Priority {priority_number} already exists or is invalid")

            # Build priority section
            priority_section = self._build_priority_section(
                priority_number,
                title,
                duration,
                impact,
                status,
                description,
                deliverables or [],
            )

            # Find insertion point
            lines = content.split("\n")
            insert_index = self._find_insertion_point(lines, priority_number)

            # Insert new priority
            lines.insert(insert_index, priority_section)

            # Write back atomically
            new_content = "\n".join(lines)
            self._atomic_write(new_content)

            logger.info(f"Added {priority_number}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to add priority: {e}")
            raise

    def update_priority(self, priority_number: str, field: str, value: str) -> bool:
        """Update existing priority field.

        Creates a backup before updating. Supports updating status, duration,
        impact, and other fields.

        Args:
            priority_number: e.g., "PRIORITY 3"
            field: Field to update (status, duration, impact, etc.)
            value: New value

        Returns:
            True if successful

        Raises:
            ValueError: If priority not found or field is invalid
            IOError: If file operations fail

        Example:
            >>> editor.update_priority(
            ...     priority_number="PRIORITY 3",
            ...     field="status",
            ...     value="✅ Complete"
            ... )
            True
        """
        try:
            # Create backup
            self._create_backup()

            # Read roadmap
            content = self.roadmap_path.read_text()

            # Normalize priority number
            if not priority_number.startswith("PRIORITY"):
                priority_number = f"PRIORITY {priority_number}"

            # Find priority section
            pattern = rf"### 🔴 \*\*{re.escape(priority_number)}:.*?\*\*"
            match = re.search(pattern, content, re.IGNORECASE)

            if not match:
                raise ValueError(f"{priority_number} not found in roadmap")

            # Update field based on type
            field_lower = field.lower()

            if field_lower == "status":
                # Update status line
                content = re.sub(
                    rf"(\*\*{re.escape(priority_number)}:.*?\*\*.*?\n.*?\*\*Status\*\*:) [^\n]+",
                    rf"\1 {value}",
                    content,
                    flags=re.IGNORECASE,
                )
            elif field_lower in ["duration", "estimated duration"]:
                content = re.sub(
                    rf"(\*\*{re.escape(priority_number)}:.*?\n.*?\*\*Estimated Duration\*\*:) [^\n]+",
                    rf"\1 {value}",
                    content,
                    flags=re.IGNORECASE,
                )
            elif field_lower == "impact":
                content = re.sub(
                    rf"(\*\*{re.escape(priority_number)}:.*?\n.*?\*\*Impact\*\*:) [^\n]+",
                    rf"\1 {value}",
                    content,
                    flags=re.IGNORECASE,
                )
            else:
                raise ValueError(f"Unsupported field: {field}")

            # Write back atomically
            self._atomic_write(content)

            logger.info(f"Updated {priority_number} {field} to {value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update priority: {e}")
            raise

    def get_priority_summary(self) -> Dict:
        """Get summary of all priorities.

        Scans the roadmap and extracts information about all priorities
        including their status, completion rate, etc.

        Returns:
            Dictionary with summary information:
            - total: Total number of priorities
            - priorities: List of priority dicts (number, title, status)
            - completed: Count of completed priorities
            - in_progress: Count of in-progress priorities
            - planned: Count of planned priorities

        Example:
            >>> summary = editor.get_priority_summary()
            >>> print(f"Progress: {summary['completed']}/{summary['total']}")
            Progress: 3/9
        """
        try:
            content = self.roadmap_path.read_text()

            # Extract all priorities with various status patterns
            # Pattern matches: ### 🔴 **PRIORITY X: Title** ... Status: ...
            pattern = r"### [🔴🟢] \*\*PRIORITY (\d+\.?\d*):(.+?)\*\*.*?\n.*?\*\*Status\*\*: (.+?)\n"
            matches = re.findall(pattern, content, re.DOTALL)

            priorities = []
            for match in matches:
                priorities.append(
                    {
                        "number": f"PRIORITY {match[0]}",
                        "title": match[1].strip(),
                        "status": match[2].strip(),
                    }
                )

            # Count by status
            completed = len([p for p in priorities if "✅" in p["status"]])
            in_progress = len([p for p in priorities if "🔄" in p["status"]])
            planned = len([p for p in priorities if "📝" in p["status"]])

            return {
                "total": len(priorities),
                "priorities": priorities,
                "completed": completed,
                "in_progress": in_progress,
                "planned": planned,
            }

        except Exception as e:
            logger.error(f"Failed to get priority summary: {e}")
            return {
                "total": 0,
                "priorities": [],
                "completed": 0,
                "in_progress": 0,
                "planned": 0,
            }

    def get_priority_content(self, priority_number: str) -> Optional[str]:
        """Get full content of a specific priority.

        Args:
            priority_number: e.g., "PRIORITY 3" or "3"

        Returns:
            Priority section content or None if not found

        Example:
            >>> content = editor.get_priority_content("PRIORITY 3")
            >>> print(content[:100])
        """
        try:
            # Normalize priority number
            if not priority_number.startswith("PRIORITY"):
                priority_number = f"PRIORITY {priority_number}"

            content = self.roadmap_path.read_text()
            lines = content.split("\n")

            # Find priority section
            in_priority = False
            priority_lines = []

            for line in lines:
                # Check if this is the start of our priority
                if priority_number.upper() in line.upper() and line.startswith("###"):
                    in_priority = True
                    priority_lines.append(line)
                elif in_priority:
                    # Check if we've hit the next priority
                    if line.startswith("###") and "PRIORITY" in line.upper():
                        break
                    priority_lines.append(line)

            if priority_lines:
                return "\n".join(priority_lines)
            return None

        except Exception as e:
            logger.error(f"Failed to get priority content: {e}")
            return None

    def _create_backup(self):
        """Create timestamped backup of roadmap.

        Backups are stored in roadmap_backups/ directory with timestamp.
        Only the last 10 backups are kept.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"ROADMAP_{timestamp}.md"
            shutil.copy(self.roadmap_path, backup_path)

            logger.info(f"Created backup: {backup_path}")

            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("ROADMAP_*.md"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")

        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    def _validate_priority_number(self, priority_number: str, content: str) -> bool:
        """Validate priority number is unique and well-formed.

        Args:
            priority_number: Priority number to validate
            content: Current roadmap content

        Returns:
            True if valid, False otherwise
        """
        # Check if already exists (case insensitive)
        if priority_number.upper() in content.upper():
            logger.warning(f"Priority {priority_number} already exists")
            return False

        # Extract and validate number format
        match = re.match(r"PRIORITY (\d+\.?\d*)", priority_number, re.IGNORECASE)
        if not match:
            logger.warning(f"Invalid priority number format: {priority_number}")
            return False

        return True

    def _build_priority_section(
        self,
        priority_number: str,
        title: str,
        duration: str,
        impact: str,
        status: str,
        description: str,
        deliverables: List[str],
    ) -> str:
        """Build formatted priority section.

        Args:
            priority_number: Priority number
            title: Title
            duration: Duration estimate
            impact: Impact stars
            status: Status
            description: Description
            deliverables: List of deliverables

        Returns:
            Formatted priority section as string
        """
        section = f"""
### 🔴 **{priority_number}: {title}**

**Estimated Duration**: {duration}
**Impact**: {impact}
**Status**: {status}

#### Project: {title}

{description if description else f"Implementation of {title}."}

**Deliverables**:
"""
        if deliverables:
            for item in deliverables:
                section += f"- {item}\n"
        else:
            section += "- TBD\n"

        section += "\n---\n"

        return section

    def _find_insertion_point(self, lines: List[str], priority_number: str) -> int:
        """Find where to insert new priority.

        Priorities should be inserted in numerical order.

        Args:
            lines: Roadmap lines
            priority_number: New priority number

        Returns:
            Line index where priority should be inserted
        """
        # Extract number from priority
        match = re.match(r"PRIORITY (\d+\.?\d*)", priority_number, re.IGNORECASE)
        if not match:
            # Fallback to end of file
            return len(lines)

        new_priority_num = float(match.group(1))

        # Find all existing priorities and their line numbers
        priority_positions = []
        for i, line in enumerate(lines):
            if line.startswith("### ") and "PRIORITY" in line.upper():
                # Extract priority number
                priority_match = re.search(r"PRIORITY (\d+\.?\d*)", line, re.IGNORECASE)
                if priority_match:
                    priority_positions.append((float(priority_match.group(1)), i))

        # Find insertion point based on numerical order
        insert_line = len(lines)  # Default to end
        for priority_num, line_idx in priority_positions:
            if new_priority_num < priority_num:
                # Insert before this priority
                insert_line = line_idx
                break
            # If new priority is greater, look for next separator after this priority
            elif new_priority_num > priority_num:
                # Find next --- separator after this priority
                for j in range(line_idx, len(lines)):
                    if lines[j].strip() == "---":
                        insert_line = j + 1
                        break

        return insert_line

    def _atomic_write(self, content: str):
        """Atomically write content to roadmap file.

        Writes to a temporary file first, then renames to ensure atomicity.

        Args:
            content: Content to write
        """
        temp_path = self.roadmap_path.with_suffix(".tmp")
        try:
            # Write to temp file
            temp_path.write_text(content)

            # Atomic rename
            temp_path.replace(self.roadmap_path)

            logger.debug("Atomically wrote roadmap")

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to write roadmap: {e}")
