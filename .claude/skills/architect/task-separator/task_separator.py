"""Task Separator Skill for Architect.

Analyzes task independence for parallel execution safety.

Author: architect (implementing SPEC-108)
Date: 2025-10-19
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TaskSeparatorSkill:
    """Analyze task independence for parallel execution."""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.specs_dir = self.repo_root / "docs" / "architecture" / "specs"

    def execute(self, priority_ids: List[int]) -> Dict[str, Any]:
        """Analyze priorities for parallel execution safety."""
        try:
            # Build file impact map
            task_file_map = {}
            for priority_id in priority_ids:
                files = self._extract_file_impacts(priority_id)
                if files is None:
                    return {
                        "valid": False,
                        "reason": f"No spec found for PRIORITY {priority_id}",
                        "independent_pairs": [],
                        "conflicts": {},
                        "task_file_map": {},
                    }
                task_file_map[priority_id] = files

            # Detect conflicts
            conflicts = {}
            independent_pairs = []

            for i, priority_a in enumerate(priority_ids):
                for priority_b in priority_ids[i + 1 :]:
                    files_a = set(task_file_map[priority_a])
                    files_b = set(task_file_map[priority_b])
                    shared_files = files_a & files_b

                    pair = tuple(sorted([priority_a, priority_b]))

                    if shared_files:
                        conflicts[pair] = sorted(list(shared_files))
                    else:
                        independent_pairs.append(pair)

            if not independent_pairs:
                return {
                    "valid": False,
                    "reason": "No independent pairs - all tasks have file conflicts",
                    "independent_pairs": [],
                    "conflicts": conflicts,
                    "task_file_map": task_file_map,
                }

            return {
                "valid": True,
                "independent_pairs": independent_pairs,
                "conflicts": conflicts,
                "task_file_map": task_file_map,
            }

        except Exception as e:
            logger.error(f"Error in task separator: {e}", exc_info=True)
            return {
                "valid": False,
                "reason": f"Error: {e}",
                "independent_pairs": [],
                "conflicts": {},
                "task_file_map": {},
            }

    def _extract_file_impacts(self, priority_id):
        """Extract file impacts from spec.

        Args:
            priority_id: Can be int or string
        """
        spec_file = self._find_spec_file(priority_id)
        if not spec_file:
            return None

        try:
            content = spec_file.read_text()
        except Exception as e:
            logger.error(f"Error reading {spec_file}: {e}")
            return None

        file_paths = set()

        # Extract various file path patterns
        patterns = [
            r"```\w+\s+([\w/]+\.py)",  # Code blocks
            r"`([\w/]+\.py)`",  # Backticks
            r"-\s*\[\s*\]\s+.*?`([\w/]+\.py)`",  # Checklist items
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                file_paths.add(match.group(1))

        return sorted(list(file_paths))

    def _find_spec_file(self, priority_id):
        """Find spec file for priority.

        Args:
            priority_id: Can be int (38) or string ("038", "US-038")
        """
        # Handle both int and string priority IDs
        if isinstance(priority_id, int):
            patterns = [
                f"SPEC-{priority_id}-*.md",
                f"SPEC-{priority_id:03d}-*.md",
            ]
        else:
            # String priority_id (e.g., "038", "US-038")
            # Extract numeric part if it starts with letters
            numeric_part = priority_id
            if "-" in priority_id:
                numeric_part = priority_id.split("-")[1]

            patterns = [
                f"SPEC-{numeric_part}-*.md",
                f"SPEC-{int(numeric_part):03d}-*.md",
            ]

        for pattern in patterns:
            matches = list(self.specs_dir.glob(pattern))
            if matches:
                return matches[0]

        return None


def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """Skill entry point."""
    priority_ids = args.get("priority_ids", [])
    if not priority_ids:
        return {
            "valid": False,
            "reason": "No priority_ids provided",
            "independent_pairs": [],
            "conflicts": {},
            "task_file_map": {},
        }

    skill = TaskSeparatorSkill()
    return skill.execute(priority_ids)
