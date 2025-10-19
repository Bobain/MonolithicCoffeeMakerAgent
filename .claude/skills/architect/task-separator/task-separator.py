"""
Task Separator Skill for architect.

Automated task separation analysis: extract files → build map → find conflicts → report.

Author: code_developer (implementing SPEC-108)
Date: 2025-10-19
Related: SPEC-108, US-108, PRIORITY 23
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute task separation analysis.

    Args:
        context: Context data containing 'priority_ids' field

    Returns:
        Dict with independent_pairs, conflicts, and task_file_map
    """
    priority_ids = context.get("priority_ids", [])

    if not priority_ids:
        return {"independent_pairs": [], "conflicts": {}, "task_file_map": {}, "error": "No priority_ids provided"}

    print(f"Analyzing task separation for priorities: {priority_ids}")

    # Step 1: Build file map (priority -> files)
    task_file_map = build_file_map(priority_ids)
    print(f"  Built file map for {len(task_file_map)} priorities")

    # Step 2: Find safe pairs (no file overlap)
    independent_pairs = find_safe_pairs(task_file_map)
    print(f"  Found {len(independent_pairs)} independent pairs")

    # Step 3: Find conflicts (file overlaps)
    conflicts = find_conflicts(task_file_map)
    print(f"  Found {len(conflicts)} conflicting pairs")

    return {
        "independent_pairs": independent_pairs,
        "conflicts": {str(k): v for k, v in conflicts.items()},  # Serialize tuple keys
        "task_file_map": {k: list(v) for k, v in task_file_map.items()},  # Convert sets to lists
    }


def build_file_map(priority_ids: List[int]) -> Dict[int, Set[str]]:
    """Build map of priority -> files from technical specs.

    Args:
        priority_ids: List of PRIORITY numbers

    Returns:
        Map of priority_id -> set of file patterns
    """
    file_map = {}

    for priority_id in priority_ids:
        files = extract_files_from_spec(priority_id)
        file_map[priority_id] = files

    return file_map


def extract_files_from_spec(priority_id: int) -> Set[str]:
    """Extract file patterns from technical spec.

    Args:
        priority_id: PRIORITY number

    Returns:
        Set of file patterns (paths or globs)
    """
    # Look for technical spec
    spec_path = find_spec_file(priority_id)

    if not spec_path:
        print(f"  ⚠️  No spec found for PRIORITY {priority_id}")
        return set()

    # Read spec and extract file patterns
    try:
        with open(spec_path, "r") as f:
            content = f.read()

        files = extract_file_patterns_from_text(content)
        print(f"  ✅ PRIORITY {priority_id}: {len(files)} file patterns")
        return files

    except Exception as e:
        print(f"  ❌ Error reading spec for PRIORITY {priority_id}: {e}")
        return set()


def find_spec_file(priority_id: int) -> Path | None:
    """Find technical spec file for priority.

    Args:
        priority_id: PRIORITY number

    Returns:
        Path to spec file, or None if not found
    """
    # Check for SPEC-{priority_id}-*.md in docs/architecture/specs/
    specs_dir = Path("docs/architecture/specs")

    if not specs_dir.exists():
        return None

    # Try SPEC-{priority_id:03d}-*.md
    pattern = f"SPEC-{priority_id:03d}-*.md"
    matches = list(specs_dir.glob(pattern))

    if matches:
        return matches[0]

    # Try SPEC-{priority_id}-*.md (without zero-padding)
    pattern = f"SPEC-{priority_id}-*.md"
    matches = list(specs_dir.glob(pattern))

    if matches:
        return matches[0]

    return None


def extract_file_patterns_from_text(text: str) -> Set[str]:
    """Extract file patterns from spec text.

    Looks for:
    - **File**: `path/to/file.py`
    - **Files to Create**: path/to/file.py
    - Bullet points with .py files
    - Code blocks with file paths

    Args:
        text: Spec file content

    Returns:
        Set of file patterns
    """
    patterns = set()

    # Pattern 1: **File**: `path/to/file.py`
    matches = re.findall(r"\*\*File\*\*:\s*`([^`]+)`", text)
    patterns.update(matches)

    # Pattern 2: **Files to Create**: - `path/to/file.py`
    matches = re.findall(r"\*\*Files to Create\*\*:.*?-\s*`([^`]+)`", text, re.DOTALL)
    patterns.update(matches)

    # Pattern 3: Bullet points with .py files
    matches = re.findall(r"[-*]\s+`([^`]*\.py[^`]*)`", text)
    patterns.update(matches)

    # Pattern 4: Common paths in markdown code blocks
    matches = re.findall(r"```[a-z]*\n([^\n]*\.py[^\n]*)\n", text)
    patterns.update(matches)

    # Pattern 5: Paths with coffee_maker/ or tests/
    matches = re.findall(r"(coffee_maker/[^\s,;)]+\.py)", text)
    patterns.update(matches)
    matches = re.findall(r"(tests/[^\s,;)]+\.py)", text)
    patterns.update(matches)

    # Pattern 6: Directory patterns (coffee_maker/module/*)
    matches = re.findall(r"(coffee_maker/[^\s,;)]+/\*)", text)
    patterns.update(matches)
    matches = re.findall(r"(tests/[^\s,;)]+/\*)", text)
    patterns.update(matches)

    # Clean up patterns (remove backticks, quotes, trailing punctuation)
    cleaned = set()
    for pattern in patterns:
        pattern = pattern.strip("`\"',.;:)")
        if pattern:
            cleaned.add(pattern)

    return cleaned


def find_safe_pairs(task_file_map: Dict[int, Set[str]]) -> List[Tuple[int, int]]:
    """Find pairs of tasks with zero file overlap.

    Args:
        task_file_map: Map of priority_id -> file patterns

    Returns:
        List of (priority_a, priority_b) tuples that are safe to run in parallel
    """
    safe_pairs = []
    priority_ids = sorted(task_file_map.keys())

    for i, priority_a in enumerate(priority_ids):
        for priority_b in priority_ids[i + 1 :]:
            files_a = task_file_map[priority_a]
            files_b = task_file_map[priority_b]

            # Check for direct overlap
            overlap = files_a & files_b

            # Check for glob pattern conflicts
            has_conflict = False
            for file_a in files_a:
                for file_b in files_b:
                    if files_conflict(file_a, file_b):
                        has_conflict = True
                        break
                if has_conflict:
                    break

            if not overlap and not has_conflict:
                safe_pairs.append((priority_a, priority_b))

    return safe_pairs


def find_conflicts(task_file_map: Dict[int, Set[str]]) -> Dict[Tuple[int, int], List[str]]:
    """Find pairs of tasks with file conflicts.

    Args:
        task_file_map: Map of priority_id -> file patterns

    Returns:
        Map of (priority_a, priority_b) -> list of conflicting files
    """
    conflicts = {}
    priority_ids = sorted(task_file_map.keys())

    for i, priority_a in enumerate(priority_ids):
        for priority_b in priority_ids[i + 1 :]:
            files_a = task_file_map[priority_a]
            files_b = task_file_map[priority_b]

            # Check for direct overlap
            overlap = files_a & files_b

            # Check for glob pattern conflicts
            glob_conflicts = []
            for file_a in files_a:
                for file_b in files_b:
                    if file_a != file_b and files_conflict(file_a, file_b):
                        glob_conflicts.append(f"{file_a} ↔ {file_b}")

            if overlap or glob_conflicts:
                conflict_list = list(overlap) + glob_conflicts
                conflicts[(priority_a, priority_b)] = conflict_list

    return conflicts


def files_conflict(pattern_a: str, pattern_b: str) -> bool:
    """Check if two file patterns conflict.

    Args:
        pattern_a: First file pattern (path or glob)
        pattern_b: Second file pattern (path or glob)

    Returns:
        True if patterns conflict (overlap)
    """
    # Exact match
    if pattern_a == pattern_b:
        return True

    # Check if one is a glob pattern matching the other
    if "*" in pattern_a:
        # pattern_a is glob, check if pattern_b matches
        glob_prefix = pattern_a.replace("*", "")
        if pattern_b.startswith(glob_prefix):
            return True

    if "*" in pattern_b:
        # pattern_b is glob, check if pattern_a matches
        glob_prefix = pattern_b.replace("*", "")
        if pattern_a.startswith(glob_prefix):
            return True

    # Check directory overlap
    # e.g., coffee_maker/orchestrator/* conflicts with coffee_maker/orchestrator/coordinator.py
    parts_a = pattern_a.split("/")
    parts_b = pattern_b.split("/")

    # If one is a wildcard directory and the other is a file in that directory
    for i, (part_a, part_b) in enumerate(zip(parts_a, parts_b)):
        if part_a == "*" or part_b == "*":
            # Check if the prefix matches
            if parts_a[:i] == parts_b[:i]:
                return True

    return False


if __name__ == "__main__":
    # Example usage
    result = main({"priority_ids": [20, 21, 22, 23]})
    print(json.dumps(result, indent=2))
