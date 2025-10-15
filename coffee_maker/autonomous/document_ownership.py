"""Document ownership enforcement for multi-agent system.

CRITICAL: Prevents ownership conflicts by enforcing write permissions.

This module provides runtime enforcement of document ownership rules to prevent
multiple agents from writing to the same files, which would cause conflicts.

Example:
    # Check ownership before writing
    if DocumentOwnershipGuard.can_write("code_developer", "coffee_maker/cli/test.py"):
        write_file(...)

    # Assert ownership (raises exception if not owned)
    DocumentOwnershipGuard.assert_can_write("project_manager", "docs/ROADMAP.md")

    # Use decorator for automatic enforcement
    @requires_ownership("code_developer")
    def write_code(file_path):
        with open(file_path, 'w') as f:
            f.write(code)
"""

from pathlib import Path
from typing import Dict, Set, Optional, List
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class DocumentOwnershipGuard:
    """Enforce document ownership rules at runtime.

    This class maintains ownership rules and provides methods to check and enforce
    them. It's the single source of truth for "who can write what".

    The ownership rules are designed to prevent conflicts in a multi-agent system
    where multiple agents might try to modify the same files.
    """

    # Define ownership rules (SINGLE SOURCE OF TRUTH)
    # CRITICAL: NO OVERLAPS ALLOWED
    # An agent CANNOT own a parent directory if another agent owns a subdirectory
    # Each directory has EXACTLY ONE owner (enforced at runtime)
    OWNERSHIP_RULES: Dict[str, Set[str]] = {
        # ACE Framework directories (most specific first for longest-match)
        "docs/generator/": {"generator"},
        "docs/reflector/": {"reflector"},
        "docs/curator/": {"curator"},
        # Agent-specific docs directories
        "docs/architecture/": {"architect"},
        "docs/roadmap/": {"project_manager"},
        "docs/code-searcher/": {"project_manager"},  # project_manager writes code-searcher reports
        "docs/refacto/": {"code_sanitizer"},  # code-sanitizer owns refactoring recommendations
        "docs/templates/": {"project_manager"},
        "docs/tutorials/": {"project_manager"},
        "docs/user_interpret/": {"project_manager"},  # Meta-documentation about user_interpret
        # NO "docs/" entry - would create overlaps!
        # Each subdirectory must be explicitly owned
        # architect owns dependency management (NOT code_developer)
        "pyproject.toml": {"architect"},
        "poetry.lock": {"architect"},
        # code-sanitizer owns style guide
        ".gemini.styleguide.md": {"code_sanitizer"},
        # code_developer owns implementation
        "coffee_maker/": {"code_developer"},
        "tests/": {"code_developer"},
        "scripts/": {"code_developer"},
        ".claude/": {"code_developer"},
        ".pre-commit-config.yaml": {"code_developer"},
        # operational data (not docs)
        "data/user_interpret/": {"user_interpret"},
    }

    # SPECIAL: Shared write with clear field boundaries
    SHARED_WRITE_RULES: Dict[str, Dict[str, Set[str]]] = {
        "docs/roadmap/ROADMAP.md": {
            "strategic_updates": {"project_manager"},  # Add/remove priorities, descriptions
            "status_updates": {"code_developer"},  # Status fields only (Planned → In Progress → Complete)
        }
    }

    @classmethod
    def can_write(cls, agent_name: str, file_path: str) -> bool:
        """Check if agent can write to file.

        Args:
            agent_name: Name of agent attempting write
            file_path: Path to file (absolute or relative)

        Returns:
            True if agent owns the file, False otherwise

        Example:
            >>> DocumentOwnershipGuard.can_write("code_developer", "coffee_maker/test.py")
            True
            >>> DocumentOwnershipGuard.can_write("project_manager", "coffee_maker/test.py")
            False
        """
        path = Path(file_path).resolve()

        # Find ALL matching patterns and use the LONGEST (most specific) one
        matching_patterns = []
        for pattern, owners in cls.OWNERSHIP_RULES.items():
            if cls._matches_pattern(path, pattern):
                matching_patterns.append((pattern, owners))

        if not matching_patterns:
            # Default: deny (safer than allow)
            logger.warning(
                f"❌ No ownership rule for {file_path}, denying write by {agent_name}. "
                f"Add explicit rule to OWNERSHIP_RULES if this file should be writable."
            )
            return False

        # Use longest match (most specific pattern)
        # Sort by pattern length descending
        matching_patterns.sort(key=lambda x: len(x[0]), reverse=True)
        pattern, owners = matching_patterns[0]

        result = agent_name in owners
        if result:
            logger.debug(f"✅ {agent_name} CAN write to {file_path} (pattern: {pattern})")
        else:
            logger.debug(f"❌ {agent_name} CANNOT write to {file_path} (owned by: {', '.join(owners)})")
        return result

    @classmethod
    def assert_can_write(cls, agent_name: str, file_path: str):
        """Assert agent can write to file (raises exception if not).

        CRITICAL: This enforces the NO OVERLAPS rule at runtime.

        Args:
            agent_name: Name of agent attempting write
            file_path: Path to file

        Raises:
            PermissionError: If agent doesn't own the file

        Example:
            >>> DocumentOwnershipGuard.assert_can_write("code_developer", "coffee_maker/test.py")
            # No exception
            >>> DocumentOwnershipGuard.assert_can_write("assistant", "coffee_maker/test.py")
            PermissionError: OWNERSHIP VIOLATION: assistant cannot write to coffee_maker/test.py
        """
        owners = cls.get_owners(file_path)

        if agent_name not in owners:
            # Check if this is the special shared ROADMAP.md
            if file_path.endswith("docs/roadmap/ROADMAP.md"):
                # Allow project_manager and code_developer with field restrictions
                if agent_name in ["project_manager", "code_developer"]:
                    # WARN: Agent must respect field boundaries
                    logger.warning(f"{agent_name} can write to ROADMAP.md but ONLY their designated fields")
                    return

            raise PermissionError(
                f"❌ OWNERSHIP VIOLATION: {agent_name} cannot write to {file_path}\n"
                f"   Owned by: {', '.join(owners) if owners else 'UNKNOWN'}\n"
                f"   This is a critical architectural rule to prevent conflicts.\n"
                f"   See: .claude/CLAUDE.md - Agent Tool Ownership & Boundaries"
            )

    @classmethod
    def get_owners(cls, file_path: str) -> Set[str]:
        """Get owners for a file path.

        Args:
            file_path: Path to file

        Returns:
            Set of agent names that own this file, or empty set if no rule matches

        Example:
            >>> DocumentOwnershipGuard.get_owners("docs/ROADMAP.md")
            {'project_manager'}
            >>> DocumentOwnershipGuard.get_owners("coffee_maker/cli/test.py")
            {'code_developer'}
        """
        path = Path(file_path).resolve()

        # Find ALL matching patterns and use the LONGEST (most specific) one
        matching_patterns = []
        for pattern, owners in cls.OWNERSHIP_RULES.items():
            if cls._matches_pattern(path, pattern):
                matching_patterns.append((pattern, owners))

        if not matching_patterns:
            return set()

        # Use longest match (most specific pattern)
        matching_patterns.sort(key=lambda x: len(x[0]), reverse=True)
        _, owners = matching_patterns[0]
        return owners

    @classmethod
    def validate_no_overlaps(cls) -> List[str]:
        """Validate that no directory has overlapping ownership.

        CRITICAL: NO OVERLAPS ALLOWED
        - An agent CANNOT own a parent directory if another agent owns a subdirectory
        - This enables parallel operations without conflicts

        Returns:
            List of overlap violations (empty if no overlaps)

        Example:
            >>> violations = DocumentOwnershipGuard.validate_no_overlaps()
            >>> assert len(violations) == 0, "Overlaps detected!"
        """
        violations = []
        paths = sorted(cls.OWNERSHIP_RULES.keys())

        for i, path1 in enumerate(paths):
            for path2 in paths[i + 1 :]:
                # Check if path1 is parent of path2 or vice versa
                if path2.startswith(path1) or path1.startswith(path2):
                    owners1 = cls.OWNERSHIP_RULES[path1]
                    owners2 = cls.OWNERSHIP_RULES[path2]

                    # If different owners, this is an overlap violation
                    if owners1 != owners2:
                        violations.append(f"OVERLAP: {path1} (owned by {owners1}) and {path2} (owned by {owners2})")

        if violations:
            logger.error(f"❌ {len(violations)} ownership overlaps detected")
        else:
            logger.debug("✅ No overlaps detected in ownership rules")

        return violations

    @classmethod
    def _matches_pattern(cls, path: Path, pattern: str) -> bool:
        """Check if path matches pattern.

        Supports:
        - Directory patterns: "docs/" (matches anything under docs/)
        - Wildcard patterns: "*.md" (future enhancement)
        - Exact file matches: "pyproject.toml"

        Args:
            path: Resolved absolute path to check
            pattern: Pattern to match against (relative to project root)

        Returns:
            True if path matches pattern
        """
        # Get project root
        project_root = cls._get_project_root()
        if not project_root:
            # Fallback: use current directory
            project_root = Path.cwd()

        pattern_path = Path(pattern)

        # Directory patterns (e.g., "docs/", "coffee_maker/")
        if pattern.endswith("/"):
            pattern_dir = (project_root / pattern.rstrip("/")).resolve()
            try:
                # Check if path is under this directory
                path.relative_to(pattern_dir)
                return True
            except ValueError:
                return False

        # Exact file match (e.g., "pyproject.toml", ".claude/CLAUDE.md")
        try:
            full_pattern_path = (project_root / pattern_path).resolve()
            return path == full_pattern_path
        except Exception:
            return False

    @classmethod
    def _patterns_overlap(cls, pattern1: str, pattern2: str) -> bool:
        """Check if two patterns overlap.

        Two patterns overlap if:
        - One is a parent directory of the other
        - They refer to the same directory

        Args:
            pattern1: First pattern
            pattern2: Second pattern

        Returns:
            True if patterns overlap
        """
        # Simplified check for directory patterns
        p1 = Path(pattern1.rstrip("/"))
        p2 = Path(pattern2.rstrip("/"))

        # If one is parent of other, they overlap
        try:
            p1.relative_to(p2)
            return True
        except ValueError:
            pass

        try:
            p2.relative_to(p1)
            return True
        except ValueError:
            pass

        return False

    @classmethod
    def _get_project_root(cls) -> Optional[Path]:
        """Get project root directory (where .git is located).

        Returns:
            Path to project root, or None if not found
        """
        try:
            current = Path.cwd()
            # Walk up until we find .git
            for parent in [current] + list(current.parents):
                if (parent / ".git").exists():
                    return parent
            return None
        except Exception:
            return None


def requires_ownership(agent_name: str):
    """Decorator to enforce file ownership on write operations.

    Usage:
        @requires_ownership("code_developer")
        def write_code(file_path, code):
            with open(file_path, 'w') as f:
                f.write(code)

    Args:
        agent_name: Name of the agent performing the operation

    Raises:
        PermissionError: If agent doesn't own the file
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to find file_path in args or kwargs
            file_path = kwargs.get("file_path") or kwargs.get("path") or (args[0] if args else None)

            if file_path:
                DocumentOwnershipGuard.assert_can_write(agent_name, file_path)

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Module-level startup validation
def _validate_ownership_on_import():
    """Validate ownership rules on module import (startup check).

    CRITICAL: Catches overlaps at startup, before any operations run.
    """
    guard = DocumentOwnershipGuard()
    violations = guard.validate_no_overlaps()

    if violations:
        error_msg = "CRITICAL: Ownership overlaps detected:\n" + "\n".join(violations)
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info("✅ Ownership validation passed: NO overlaps detected")


# Run validation on import (catches configuration errors early)
_validate_ownership_on_import()
