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
from typing import Dict, Set, Optional
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
    # IMPORTANT: More specific patterns are checked first (longest match wins)
    OWNERSHIP_RULES: Dict[str, Set[str]] = {
        # ACE components own their specific subdirectories (MUST come before docs/)
        "docs/generator/": {"generator"},
        "docs/reflector/": {"reflector"},
        "docs/curator/": {"curator"},
        # architect owns architectural documentation (MUST come before docs/)
        "docs/architecture/": {"architect"},
        # project_manager owns strategic documentation (general docs/)
        "docs/roadmap/": {"project_manager"},  # STRATEGIC planning
        "docs/": {"project_manager"},  # General docs (after ACE exceptions)
        # code_developer owns technical configuration (including .claude/)
        ".claude/": {"code_developer"},  # Technical configs (agents, prompts, MCP)
        # code_developer owns implementation
        "coffee_maker/": {"code_developer"},
        "tests/": {"code_developer"},
        "scripts/": {"code_developer"},
        "pyproject.toml": {"code_developer"},
        # user_interpret owns conversation logs (moved from docs/)
        "data/user_interpret/": {"user_interpret"},
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
        if not cls.can_write(agent_name, file_path):
            owners = cls.get_owners(file_path)
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
    def validate_no_overlaps(cls) -> bool:
        """Validate no problematic overlaps in ownership rules.

        Overlaps are allowed as long as they follow the longest-match principle:
        - More specific paths (longer) take precedence over general paths
        - Example: docs/generator/ can override docs/ ownership

        This check ensures there are no AMBIGUOUS overlaps (same length with
        different owners).

        Returns:
            True if no problematic overlaps, False if ambiguous overlaps found

        Example:
            >>> DocumentOwnershipGuard.validate_no_overlaps()
            True
        """
        patterns = list(cls.OWNERSHIP_RULES.keys())

        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i + 1 :]:
                if cls._patterns_overlap(pattern1, pattern2):
                    owners1 = cls.OWNERSHIP_RULES[pattern1]
                    owners2 = cls.OWNERSHIP_RULES[pattern2]

                    # Only flag if SAME LENGTH (ambiguous) with different owners
                    # Different lengths are okay (longest match wins)
                    if len(pattern1) == len(pattern2) and owners1 != owners2:
                        logger.error(
                            f"❌ AMBIGUOUS OVERLAP DETECTED:\n"
                            f"   {pattern1} owned by {owners1}\n"
                            f"   {pattern2} owned by {owners2}\n"
                            f"   Same length patterns with different owners create ambiguity!"
                        )
                        return False
                    elif owners1 != owners2:
                        # Different lengths: okay, but log for visibility
                        logger.debug(
                            f"ℹ️ Hierarchical overlap (OK):\n"
                            f"   {pattern1} owned by {owners1}\n"
                            f"   {pattern2} owned by {owners2}\n"
                            f"   Longest match wins (no ambiguity)"
                        )

        logger.debug("✅ No ambiguous overlaps detected in ownership rules")
        return True

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
