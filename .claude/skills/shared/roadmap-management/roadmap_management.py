"""ROADMAP Management Skill - Fast ROADMAP parsing and manipulation for autonomous agents.

This skill provides utilities to read, write, search, and update priorities in docs/roadmap/ROADMAP.md.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("roadmap-management")
    result = skill.execute(operation="get_next_planned_priority")
"""

import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# BUG-066: Use unified RoadmapParser instead of custom parsing
# This ensures all agents see all user stories regardless of format (## or ###)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "coffee_maker"))
from coffee_maker.autonomous.roadmap_parser import RoadmapParser

sys.path.pop(0)

logger = logging.getLogger(__name__)


class RoadmapManagementSkill:
    """ROADMAP management skill for all autonomous agents."""

    def __init__(self):
        """Initialize the skill."""
        self.roadmap_path = Path("docs/roadmap/ROADMAP.md")
        self.priorities: List[Dict[str, Any]] = []
        self._parsed = False

    def execute(self, operation: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a ROADMAP operation.

        Args:
            operation: Operation to perform (get_next, find_by_us_id, update_status, etc.)
            parameters: Operation-specific parameters

        Returns:
            dict: {"result": <result>, "error": <error_message>}
        """
        parameters = parameters or {}

        try:
            # Parse ROADMAP if not already done
            if not self._parsed:
                self._parse_roadmap()

            # Dispatch to operation handler
            operation_map = {
                "get_next_planned_priority": self.get_next_planned_priority,
                "check_spec_exists": lambda: self.check_spec_exists(parameters.get("us_id")),
                "get_priorities_without_specs": self.get_priorities_without_specs,
                "check_dependencies": lambda: self.check_dependencies(parameters.get("priority_number")),
                "get_progress": self.get_progress,
                "find_priority_by_us_id": lambda: self.find_priority_by_us_id(parameters.get("us_id")),
                "find_priority_by_number": lambda: self.find_priority_by_number(parameters.get("number")),
                "search_priorities": lambda: self.search_priorities(parameters.get("keyword")),
                "get_all_priorities": self.get_all_priorities,
                "update_priority_status": lambda: self.update_priority_status(
                    parameters.get("priority_number"), parameters.get("new_status")
                ),
                "add_new_priority": lambda: self.add_new_priority(**parameters),
            }

            if operation not in operation_map:
                return {"result": None, "error": f"Unknown operation: {operation}"}

            result = operation_map[operation]()
            return {"result": result, "error": None}

        except Exception as e:
            logger.error(f"Error in operation {operation}: {e}")
            return {"result": None, "error": str(e)}

    def _parse_roadmap(self) -> None:
        """Parse ROADMAP.md using unified RoadmapParser (BUG-066)."""
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {self.roadmap_path}")

        # BUG-066: Use unified RoadmapParser to support both ## and ### formats
        parser = RoadmapParser(str(self.roadmap_path))
        raw_priorities = parser.get_priorities()

        self.priorities = []
        for p in raw_priorities:
            # Convert RoadmapParser format to RoadmapManagementSkill format
            number = p.get("number", "")
            title = p.get("title", "")
            status = p.get("status", "Unknown")
            content = p.get("content", "")
            name = p.get("name", "")

            # Extract US ID from name or title
            us_id = None
            if "US-" in name:
                us_id = name  # e.g., "US-110"
            else:
                us_id_match = re.search(r"US-(\d+)", title)
                us_id = us_id_match.group(0) if us_id_match else None

            # Extract dependencies from content
            dependencies = []
            dep_match = re.search(r"\*\*Dependencies\*\*:(.+?)(?:\n|$)", content)
            if dep_match:
                dep_str = dep_match.group(1).strip()
                dependencies = [d.strip() for d in dep_str.split(",")]

            # Extract estimated effort from content
            effort = None
            effort_match = re.search(
                r"\*\*(?:Estimated effort|Estimated Effort|Time estimate)\*\*:(.+?)(?:\n|$)", content, re.IGNORECASE
            )
            if effort_match:
                effort = effort_match.group(1).strip()

            # Extract spec links from content
            technical_spec = None
            spec_match = re.search(r"(docs/architecture/specs/SPEC-\d+-[^\s)]+\.md)", content)
            if spec_match:
                technical_spec = spec_match.group(1)

            strategic_spec = None
            strat_spec_match = re.search(r"(docs/roadmap/PRIORITY_\d+_STRATEGIC_SPEC\.md)", content)
            if strat_spec_match:
                strategic_spec = strat_spec_match.group(1)

            # Extract status emoji from status string
            status_emoji_map = {
                "Planned": "📝",
                "In Progress": "🔄",
                "Complete": "✅",
                "Blocked": "⏸️",
                "Manual Review": "🚧",
            }
            status_emoji = status_emoji_map.get(
                status.replace("📝 ", "").replace("🔄 ", "").replace("✅ ", "").replace("⏸️ ", "").strip(), "📝"
            )

            priority = {
                "number": number,
                "title": title,
                "status": status,
                "status_emoji": status_emoji,
                "us_id": us_id,
                "description": content,  # Use full section content
                "dependencies": dependencies,
                "estimated_effort": effort,
                "technical_spec": technical_spec,
                "strategic_spec": strategic_spec,
                "line_number": p.get("section_start", 0) + 1,
            }

            self.priorities.append(priority)

        self._parsed = True
        logger.info(f"Parsed {len(self.priorities)} priorities from ROADMAP")

    # Query Operations

    def get_next_planned_priority(self) -> Optional[Dict[str, Any]]:
        """Return next priority ready to implement.

        Returns:
            dict: Next planned priority with all dependencies met, or None if no work available
        """
        for priority in self.priorities:
            if priority["status"] == "Planned":
                # Check dependencies
                deps_result = self.check_dependencies(priority["number"])
                if deps_result["all_met"]:
                    return priority

        return None

    def check_spec_exists(self, us_id: str) -> bool:
        """Check if US has technical spec.

        Args:
            us_id: US-XXX identifier

        Returns:
            bool: True if spec exists, False otherwise
        """
        priority = self.find_priority_by_us_id(us_id)
        if not priority:
            return False

        # Check if technical_spec field is populated
        if priority["technical_spec"]:
            spec_path = Path(priority["technical_spec"])
            return spec_path.exists()

        # Fallback: Search for SPEC-XXX-*.md
        us_number = us_id.split("-")[1] if "-" in us_id else us_id
        spec_pattern = f"docs/architecture/specs/SPEC-{us_number}-*.md"

        import glob

        specs = glob.glob(spec_pattern)
        return len(specs) > 0

    def get_priorities_without_specs(self) -> List[Dict[str, Any]]:
        """Return priorities needing specs (estimated effort >16 hours, no spec yet).

        Returns:
            list: Priorities needing specs
        """
        needs_specs = []

        for priority in self.priorities:
            # Skip completed priorities
            if priority["status"] == "Complete":
                continue

            # Check estimated effort
            effort_hours = self._parse_effort_hours(priority["estimated_effort"])
            if effort_hours and effort_hours > 16:  # >2 days
                # Check if spec exists
                if priority["us_id"] and not self.check_spec_exists(priority["us_id"]):
                    needs_specs.append(priority)

        return needs_specs

    def check_dependencies(self, priority_number: str) -> Dict[str, Any]:
        """Check if dependencies are met.

        Args:
            priority_number: Priority number (e.g., "11", "11.5")

        Returns:
            dict: {
                "all_met": bool,
                "blocking": [list of blocking priorities],
                "pending": [list of pending priorities]
            }
        """
        priority = self.find_priority_by_number(priority_number)
        if not priority or not priority["dependencies"]:
            return {"all_met": True, "blocking": [], "pending": []}

        blocking = []
        pending = []

        for dep in priority["dependencies"]:
            # Extract priority number from dependency string (e.g., "PRIORITY 10" → "10")
            dep_number_match = re.search(r"PRIORITY (\d+(?:\.\d+)?)", dep)
            if dep_number_match:
                dep_number = dep_number_match.group(1)
                dep_priority = self.find_priority_by_number(dep_number)

                if dep_priority:
                    if dep_priority["status"] == "Blocked":
                        blocking.append(dep)
                    elif dep_priority["status"] != "Complete":
                        pending.append(dep)

        return {"all_met": len(blocking) == 0 and len(pending) == 0, "blocking": blocking, "pending": pending}

    def get_progress(self) -> Dict[str, Any]:
        """Calculate ROADMAP progress.

        Returns:
            dict: {
                "total": int,
                "completed": int,
                "in_progress": int,
                "planned": int,
                "blocked": int,
                "completion_percentage": float
            }
        """
        total = len(self.priorities)
        completed = sum(1 for p in self.priorities if p["status"] == "Complete")
        in_progress = sum(1 for p in self.priorities if p["status"] == "In Progress")
        planned = sum(1 for p in self.priorities if p["status"] == "Planned")
        blocked = sum(1 for p in self.priorities if p["status"] == "Blocked")

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "planned": planned,
            "blocked": blocked,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
        }

    def find_priority_by_us_id(self, us_id: str) -> Optional[Dict[str, Any]]:
        """Find priority by US-XXX identifier.

        Args:
            us_id: US-XXX identifier

        Returns:
            dict: Priority or None if not found
        """
        for priority in self.priorities:
            if priority["us_id"] == us_id:
                return priority
        return None

    def find_priority_by_number(self, number: str) -> Optional[Dict[str, Any]]:
        """Find priority by number (e.g., "11", "11.5").

        Args:
            number: Priority number

        Returns:
            dict: Priority or None if not found
        """
        for priority in self.priorities:
            if priority["number"] == number:
                return priority
        return None

    def search_priorities(self, keyword: str) -> List[Dict[str, Any]]:
        """Search priorities by keyword in title or description.

        Args:
            keyword: Search keyword

        Returns:
            list: Matching priorities
        """
        results = []
        keyword_lower = keyword.lower()

        for priority in self.priorities:
            if keyword_lower in priority["title"].lower() or keyword_lower in priority["description"].lower():
                results.append(priority)

        return results

    def get_all_priorities(self) -> List[Dict[str, Any]]:
        """Get all priorities.

        Returns:
            list: All priorities
        """
        return self.priorities.copy()

    # Update Operations

    def update_priority_status(self, priority_number: str, new_status: str) -> bool:
        """Update priority status in ROADMAP.md.

        Args:
            priority_number: "11", "11.5", etc.
            new_status: "📝 Planned", "🔄 In Progress", "✅ Complete", etc.

        Returns:
            bool: True if update successful, False otherwise
        """
        if not self.roadmap_path.exists():
            logger.error(f"ROADMAP not found: {self.roadmap_path}")
            return False

        # Read current content
        content = self.roadmap_path.read_text(encoding="utf-8")

        # Normalize new_status to emoji if it's a string
        status_map = {"Planned": "📝", "In Progress": "🔄", "Complete": "✅", "Blocked": "⏸️", "Manual Review": "🚧"}
        if new_status in status_map:
            new_status = status_map[new_status]

        # Regex to find and replace status
        pattern = rf"(### PRIORITY {re.escape(priority_number)}:.*?)(📝|🔄|✅|⏸️|🚧)"
        replacement = rf"\1{new_status}"

        updated_content = re.sub(pattern, replacement, content)

        if updated_content == content:
            logger.warning(f"Priority {priority_number} not found or status unchanged")
            return False

        # Atomic write
        self._atomic_write(updated_content)

        # Invalidate parsed cache
        self._parsed = False

        logger.info(f"Updated PRIORITY {priority_number} status to {new_status}")
        return True

    def add_new_priority(
        self,
        number: str,
        title: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        estimated_effort: Optional[str] = None,
        status: str = "📝 Planned",
    ) -> bool:
        """Add new priority to ROADMAP.

        Args:
            number: "20", "19.5", etc.
            title: "US-XXX - Feature Name"
            description: Full priority description
            dependencies: ["PRIORITY 18", "PRIORITY 19"]
            estimated_effort: "10-15 hours"
            status: "📝 Planned" (default)

        Returns:
            bool: True if add successful, False otherwise
        """
        # Normalize status to emoji
        status_map = {"Planned": "📝", "In Progress": "🔄", "Complete": "✅", "Blocked": "⏸️", "Manual Review": "🚧"}
        if status in status_map:
            status = status_map[status]

        # Generate priority section
        priority_section = f"\n### PRIORITY {number}: {title} {status}\n\n"
        priority_section += f"**Estimated effort**: {estimated_effort or 'TBD'}\n"
        priority_section += f"**Status**: {status}\n\n"
        priority_section += f"{description}\n"

        if dependencies:
            dep_str = ", ".join(dependencies)
            priority_section += f"\n**Dependencies**: {dep_str}\n"

        priority_section += "\n"

        # Read current content
        content = self.roadmap_path.read_text(encoding="utf-8")

        # Find insertion point (after last priority with number < new number)
        insertion_point = self._find_insertion_point(content, number)

        # Insert new priority
        updated_content = content[:insertion_point] + priority_section + content[insertion_point:]

        # Atomic write
        self._atomic_write(updated_content)

        # Invalidate parsed cache
        self._parsed = False

        logger.info(f"Added PRIORITY {number}: {title}")
        return True

    # Utility Methods

    def _parse_effort_hours(self, effort_str: Optional[str]) -> Optional[float]:
        """Parse effort string to hours.

        Args:
            effort_str: "10-15 hours", "2-3 days", etc.

        Returns:
            float: Estimated hours (midpoint of range) or None
        """
        if not effort_str:
            return None

        # Extract numbers
        numbers = re.findall(r"(\d+(?:\.\d+)?)", effort_str)
        if not numbers:
            return None

        # Calculate average
        values = [float(n) for n in numbers]
        avg = sum(values) / len(values)

        # Handle days vs hours
        if "day" in effort_str.lower():
            avg *= 8  # Convert days to hours

        return avg

    def _find_insertion_point(self, content: str, new_number: str) -> int:
        """Find insertion point for new priority.

        Args:
            content: ROADMAP content
            new_number: New priority number

        Returns:
            int: Insertion position
        """
        new_num_float = float(new_number)

        # Find all priority headers
        priority_pattern = r"^### PRIORITY (\d+(?:\.\d+)?):.*$"
        matches = list(re.finditer(priority_pattern, content, re.MULTILINE))

        # Find last priority with number < new number
        last_match = None
        for match in matches:
            existing_num = float(match.group(1))
            if existing_num < new_num_float:
                last_match = match

        if last_match:
            # Find end of that priority (next ### PRIORITY or end of file)
            start_search = last_match.end()
            next_priority = re.search(r"^### PRIORITY", content[start_search:], re.MULTILINE)

            if next_priority:
                return start_search + next_priority.start()
            else:
                return len(content)
        else:
            # Insert at beginning of priorities section
            # Find first priority
            if matches:
                return matches[0].start()
            else:
                # No priorities yet, append to end
                return len(content)

    def _atomic_write(self, content: str) -> None:
        """Atomically write content to ROADMAP.

        Args:
            content: Content to write
        """
        # Write to temporary file first
        temp_path = self.roadmap_path.with_suffix(".tmp")
        temp_path.write_text(content, encoding="utf-8")

        # Atomic rename
        temp_path.replace(self.roadmap_path)

        logger.debug(f"Atomically wrote to {self.roadmap_path}")


# Skill entry point
def run(operation: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        operation: Operation to perform
        parameters: Operation parameters

    Returns:
        dict: {"result": <result>, "error": <error_message>}
    """
    skill = RoadmapManagementSkill()
    return skill.execute(operation, parameters)
