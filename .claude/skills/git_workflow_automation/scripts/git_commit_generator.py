#!/usr/bin/env python3
"""
Git Commit Generator: Generate conventional commit messages from git diffs.

This script analyzes git diffs and generates conventional commit messages
following the Conventional Commits specification with auto-detection of
commit type and scope.

Usage:
    # Generate from unstaged changes
    python git_commit_generator.py

    # Generate from staged changes
    python git_commit_generator.py --diff-staged

    # Generate from changes since specific commit
    python git_commit_generator.py --diff-since HEAD~3

    # Override auto-detected type and scope
    python git_commit_generator.py --type refactor --scope daemon

Author: code_developer
Date: 2025-10-19
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CommitMessage:
    """Generated conventional commit message."""

    type: str  # feat, fix, refactor, docs, test, perf, chore
    scope: Optional[str]  # Component/module affected
    subject: str  # Short description
    body: List[str]  # Detailed changes
    footer: List[str]  # Links, references, metadata
    breaking_change: bool = False

    def format(self) -> str:
        """Format as conventional commit message."""
        # Header: type(scope): subject
        header = f"{self.type}"
        if self.scope:
            header += f"({self.scope})"
        if self.breaking_change:
            header += "!"
        header += f": {self.subject}"

        # Body
        body_text = "\n".join(self.body) if self.body else ""

        # Footer with standard Claude Code attribution
        footer_lines = self.footer.copy() if self.footer else []
        footer_lines.append("")
        footer_lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")
        footer_lines.append("")
        footer_lines.append("Co-Authored-By: Claude <noreply@anthropic.com>")
        footer_text = "\n".join(footer_lines)

        # Combine parts
        parts = [header]
        if body_text:
            parts.extend(["", body_text])
        if footer_text:
            parts.extend(["", footer_text])

        return "\n".join(parts)


class GitCommitGenerator:
    """Generate conventional commit messages from git diffs."""

    # Conventional commit types
    COMMIT_TYPES = {
        "feat": "New feature",
        "fix": "Bug fix",
        "refactor": "Code restructuring without behavior change",
        "docs": "Documentation changes",
        "test": "Test additions or modifications",
        "perf": "Performance improvements",
        "chore": "Build/deps/config changes",
        "style": "Code style changes (formatting)",
        "ci": "CI/CD changes",
    }

    # Scope mapping based on directory structure
    SCOPE_PATTERNS = {
        r"^coffee_maker/autonomous/": "daemon",
        r"^coffee_maker/cli/": "cli",
        r"^coffee_maker/utils/": "utils",
        r"^coffee_maker/skills/": "skills",
        r"^docs/architecture/specs/": "specs",
        r"^docs/architecture/decisions/": "adrs",
        r"^docs/architecture/guidelines/": "guidelines",
        r"^docs/roadmap/": "roadmap",
        r"^tests/": "tests",
        r"^\.claude/skills/": "skills",
        r"^\.claude/commands/": "commands",
        r"^\.claude/agents/": "agents",
    }

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)

    def get_git_diff(self, diff_since: Optional[str] = None, staged_only: bool = False) -> str:
        """
        Get git diff output.

        Args:
            diff_since: Commit to diff against (e.g., "HEAD~1")
            staged_only: Only show staged changes

        Returns:
            Git diff output
        """
        cmd = ["git", "diff"]

        if staged_only:
            cmd.append("--staged")
        elif diff_since:
            cmd.append(diff_since)

        # Add options for better analysis
        cmd.extend(["--stat", "--numstat", "--summary"])

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git diff failed: {e.stderr}")

    def get_changed_files(self, diff_since: Optional[str] = None, staged_only: bool = False) -> List[str]:
        """
        Get list of changed files.

        Args:
            diff_since: Commit to diff against
            staged_only: Only show staged changes

        Returns:
            List of changed file paths
        """
        cmd = ["git", "diff", "--name-only"]

        if staged_only:
            cmd.append("--staged")
        elif diff_since:
            cmd.append(diff_since)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return [line.strip() for line in result.stdout.split("\n") if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git diff failed: {e.stderr}")

    def detect_commit_type(self, files: List[str]) -> str:
        """
        Auto-detect commit type from changed files.

        Args:
            files: List of changed file paths

        Returns:
            Commit type (feat, fix, docs, test, etc.)
        """
        # Count files by category
        categories = {
            "docs": 0,
            "test": 0,
            "config": 0,
            "code": 0,
        }

        for file_path in files:
            path_lower = file_path.lower()

            if path_lower.endswith((".md", ".rst", ".txt")):
                categories["docs"] += 1
            elif "test" in path_lower or path_lower.endswith(("_test.py", "test_.py")):
                categories["test"] += 1
            elif path_lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".cfg")):
                categories["config"] += 1
            elif path_lower.endswith(".py"):
                categories["code"] += 1

        # Determine type based on majority
        if categories["docs"] > 0 and categories["code"] == 0:
            return "docs"
        elif categories["test"] > 0 and categories["code"] == 0:
            return "test"
        elif categories["config"] > 0 and categories["code"] == 0:
            return "chore"
        else:
            # Default to feat for code changes (conservative choice)
            # User can override with --type if it's a fix or refactor
            return "feat"

    def detect_scope(self, files: List[str]) -> Optional[str]:
        """
        Auto-detect scope from changed files.

        Args:
            files: List of changed file paths

        Returns:
            Scope string or None
        """
        scope_counts: Dict[str, int] = {}

        for file_path in files:
            for pattern, scope in self.SCOPE_PATTERNS.items():
                if re.match(pattern, file_path):
                    scope_counts[scope] = scope_counts.get(scope, 0) + 1
                    break

        if not scope_counts:
            return None

        # Return most common scope
        return max(scope_counts.items(), key=lambda x: x[1])[0]

    def generate_subject(self, files: List[str], commit_type: str, scope: Optional[str]) -> str:
        """
        Generate commit subject line.

        Args:
            files: List of changed files
            commit_type: Commit type
            scope: Scope (or None)

        Returns:
            Subject line
        """
        # Try to generate meaningful subject based on context
        if commit_type == "docs":
            if any("SPEC-" in f for f in files):
                return "Add technical specification"
            elif any("ADR-" in f for f in files):
                return "Add architectural decision record"
            elif any("GUIDELINE-" in f for f in files):
                return "Add implementation guideline"
            else:
                return "Update documentation"

        elif commit_type == "test":
            return "Add test coverage"

        elif commit_type == "chore":
            if any("pyproject.toml" in f for f in files):
                return "Update dependencies"
            elif any(".pre-commit" in f for f in files):
                return "Update pre-commit hooks"
            else:
                return "Update configuration"

        elif scope == "skills":
            # Try to extract skill name
            skill_names = set()
            for file_path in files:
                if "skills/" in file_path:
                    parts = file_path.split("skills/")
                    if len(parts) > 1:
                        skill_name = parts[1].split("/")[0]
                        skill_names.add(skill_name)

            if skill_names:
                if len(skill_names) == 1:
                    return f"Implement {skill_names.pop()} skill"
                else:
                    return f"Implement multiple skills"

        # Generic subjects
        if commit_type == "feat":
            return "Add new feature"
        elif commit_type == "fix":
            return "Fix bug"
        elif commit_type == "refactor":
            return "Refactor code"
        elif commit_type == "perf":
            return "Improve performance"
        else:
            return "Update code"

    def generate_body(self, files: List[str], diff_output: str) -> List[str]:
        """
        Generate commit body with bullet points.

        Args:
            files: List of changed files
            diff_output: Full git diff output

        Returns:
            List of body lines
        """
        body_lines = []

        # Group files by category
        categories: Dict[str, List[str]] = {
            "Implementation": [],
            "Tests": [],
            "Documentation": [],
            "Configuration": [],
        }

        for file_path in files:
            file_name = Path(file_path).name
            path_lower = file_path.lower()

            if "test" in path_lower:
                categories["Tests"].append(file_name)
            elif path_lower.endswith((".md", ".rst")):
                categories["Documentation"].append(file_name)
            elif path_lower.endswith((".json", ".yaml", ".yml", ".toml")):
                categories["Configuration"].append(file_name)
            else:
                categories["Implementation"].append(file_name)

        # Generate bullet points
        for category, file_list in categories.items():
            if file_list:
                if len(file_list) == 1:
                    body_lines.append(f"- {category}: {file_list[0]}")
                else:
                    body_lines.append(f"- {category}: {len(file_list)} files modified")

        return body_lines

    def generate_footer(self, priority_id: Optional[str] = None, issue_id: Optional[str] = None) -> List[str]:
        """
        Generate commit footer with metadata.

        Args:
            priority_id: Priority identifier (e.g., "US-067")
            issue_id: GitHub issue number

        Returns:
            List of footer lines
        """
        footer_lines = []

        if priority_id:
            footer_lines.append(f"Implements: {priority_id}")

        if issue_id:
            footer_lines.append(f"Closes: #{issue_id}")

        return footer_lines

    def generate_commit_message(
        self,
        diff_since: Optional[str] = None,
        staged_only: bool = False,
        commit_type: Optional[str] = None,
        scope: Optional[str] = None,
        subject: Optional[str] = None,
        priority_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        breaking_change: bool = False,
    ) -> CommitMessage:
        """
        Generate conventional commit message.

        Args:
            diff_since: Commit to diff against
            staged_only: Only use staged changes
            commit_type: Override auto-detected type
            scope: Override auto-detected scope
            subject: Override auto-generated subject
            priority_id: Priority identifier
            issue_id: GitHub issue number
            breaking_change: Mark as breaking change

        Returns:
            CommitMessage object
        """
        # Get changed files
        files = self.get_changed_files(diff_since, staged_only)

        if not files:
            raise ValueError("No changes detected")

        # Get diff for body generation
        diff_output = self.get_git_diff(diff_since, staged_only)

        # Auto-detect type and scope if not provided
        final_type = commit_type or self.detect_commit_type(files)
        final_scope = scope or self.detect_scope(files)
        final_subject = subject or self.generate_subject(files, final_type, final_scope)

        # Generate body and footer
        body = self.generate_body(files, diff_output)
        footer = self.generate_footer(priority_id, issue_id)

        return CommitMessage(
            type=final_type,
            scope=final_scope,
            subject=final_subject,
            body=body,
            footer=footer,
            breaking_change=breaking_change,
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate conventional commit messages from git diffs")

    # Diff options
    parser.add_argument(
        "--diff-since",
        help="Generate from changes since commit (e.g., HEAD~1, main)",
    )
    parser.add_argument(
        "--diff-staged",
        action="store_true",
        help="Generate from staged changes only",
    )

    # Override options
    parser.add_argument(
        "--type",
        choices=list(GitCommitGenerator.COMMIT_TYPES.keys()),
        help="Override auto-detected commit type",
    )
    parser.add_argument(
        "--scope",
        help="Override auto-detected scope",
    )
    parser.add_argument(
        "--subject",
        help="Override auto-generated subject",
    )

    # Metadata options
    parser.add_argument(
        "--priority",
        help="Priority identifier (e.g., US-067)",
    )
    parser.add_argument(
        "--issue",
        help="GitHub issue number",
    )
    parser.add_argument(
        "--breaking",
        action="store_true",
        help="Mark as breaking change",
    )

    # Output options
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--codebase-root",
        default=".",
        help="Codebase root directory (default: current directory)",
    )

    args = parser.parse_args()

    try:
        generator = GitCommitGenerator(args.codebase_root)

        message = generator.generate_commit_message(
            diff_since=args.diff_since,
            staged_only=args.diff_staged,
            commit_type=args.type,
            scope=args.scope,
            subject=args.subject,
            priority_id=args.priority,
            issue_id=args.issue,
            breaking_change=args.breaking,
        )

        if args.format == "json":
            print(json.dumps(asdict(message), indent=2))
        else:
            print(message.format())

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
