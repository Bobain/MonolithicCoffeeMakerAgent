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


def extract_file_patterns_from_text(text: str) -> List[str]:
    """Extract file patterns from text.

    Args:
        text: Text to search for file patterns

    Returns:
        List of file path patterns found (including globs with *)
    """
    file_paths = set()
    patterns = [
        r"```\w+\s+([\w/]+(?:\*|\.py))",  # Code blocks (*.py or with *)
        r"`([\w/]+(?:\*|\.py))`",  # Backticks (*.py or with *)
        r"-\s*\[\s*\]\s+.*?`([\w/]+(?:\*|\.py))`",  # Checklist items
        r"\b([\w/]+/\*)",  # Directory globs (word boundary followed by path/*)
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            file_paths.add(match.group(1))

    return sorted(list(file_paths))


def find_spec_file(priority_id: Any) -> Path | None:
    """Find spec file for priority ID.

    Args:
        priority_id: Priority ID (int, string, or US-XXX format)

    Returns:
        Path to spec file or None if not found
    """
    skill = TaskSeparatorSkill()
    return skill._find_spec_file(priority_id)


def files_conflict(file1: str, file2: str) -> bool:
    """Check if two file paths conflict (exact match or glob pattern match).

    Args:
        file1: First file path (may include glob patterns with *)
        file2: Second file path (may include glob patterns with *)

    Returns:
        True if files conflict, False otherwise
    """
    # Exact match
    if file1 == file2:
        return True

    # Check glob patterns
    import fnmatch

    # If file1 is a glob pattern, check if file2 matches it
    if "*" in file1:
        if fnmatch.fnmatch(file2, file1):
            return True

    # If file2 is a glob pattern, check if file1 matches it
    if "*" in file2:
        if fnmatch.fnmatch(file1, file2):
            return True

    return False


def build_file_map(priority_ids: List[int]) -> Dict[int, List[str]]:
    """Build map of priority IDs to file paths.

    Args:
        priority_ids: List of priority IDs

    Returns:
        Dictionary mapping priority IDs to list of file paths
    """
    task_file_map = {}
    skill = TaskSeparatorSkill()
    for priority_id in priority_ids:
        files = skill._extract_file_impacts(priority_id)
        # Include entry even if files is None or empty
        if files is None:
            task_file_map[priority_id] = []
        else:
            task_file_map[priority_id] = files
    return task_file_map


def find_conflicts(task_file_map: Dict[int, set]) -> Dict[tuple, List[str]]:
    """Find file conflicts between tasks (including glob pattern matches).

    Args:
        task_file_map: Map of priority IDs to sets of file paths

    Returns:
        Dictionary of (priority_a, priority_b) tuples to list of conflicting files
    """
    conflicts = {}
    priority_ids = list(task_file_map.keys())

    for i, priority_a in enumerate(priority_ids):
        for priority_b in priority_ids[i + 1 :]:
            files_a = (
                task_file_map[priority_a]
                if isinstance(task_file_map[priority_a], list)
                else list(task_file_map[priority_a])
            )
            files_b = (
                task_file_map[priority_b]
                if isinstance(task_file_map[priority_b], list)
                else list(task_file_map[priority_b])
            )

            # Check for conflicts including glob patterns
            conflicting_files = []
            for file_a in files_a:
                for file_b in files_b:
                    if files_conflict(file_a, file_b):
                        # Add both files to the conflict list
                        if file_a not in conflicting_files:
                            conflicting_files.append(file_a)
                        if file_b not in conflicting_files:
                            conflicting_files.append(file_b)

            if conflicting_files:
                pair = tuple(sorted([priority_a, priority_b]))
                conflicts[pair] = sorted(conflicting_files)

    return conflicts


def find_safe_pairs(task_file_map: Dict[int, set]) -> List[tuple]:
    """Find pairs of tasks that can run safely in parallel (no glob conflicts).

    Args:
        task_file_map: Map of priority IDs to sets of file paths

    Returns:
        List of (priority_a, priority_b) tuples that have no conflicts
    """
    independent_pairs = []
    priority_ids = list(task_file_map.keys())

    for i, priority_a in enumerate(priority_ids):
        for priority_b in priority_ids[i + 1 :]:
            files_a = (
                task_file_map[priority_a]
                if isinstance(task_file_map[priority_a], list)
                else list(task_file_map[priority_a])
            )
            files_b = (
                task_file_map[priority_b]
                if isinstance(task_file_map[priority_b], list)
                else list(task_file_map[priority_b])
            )

            # Check for any conflicts (including glob patterns)
            has_conflict = False
            for file_a in files_a:
                for file_b in files_b:
                    if files_conflict(file_a, file_b):
                        has_conflict = True
                        break
                if has_conflict:
                    break

            if not has_conflict:
                pair = tuple(sorted([priority_a, priority_b]))
                independent_pairs.append(pair)

    return independent_pairs


def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """Skill entry point."""
    priority_ids = args.get("priority_ids", [])
    if not priority_ids:
        return {
            "error": "No priority_ids provided",
            "valid": False,
            "reason": "No priority_ids provided",
            "independent_pairs": [],
            "conflicts": {},
            "task_file_map": {},
        }

    skill = TaskSeparatorSkill()
    return skill.execute(priority_ids)
