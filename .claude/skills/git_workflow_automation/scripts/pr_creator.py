#!/usr/bin/env python3
"""
PR Creator: Create GitHub PRs with auto-generated descriptions.

This script creates GitHub Pull Requests with descriptions generated
from conventional commit history between branches.

Usage:
    # Auto mode (roadmap → main)
    python pr_creator.py --auto

    # Custom branches
    python pr_creator.py --from feature-branch --to main

    # With custom title
    python pr_creator.py --from roadmap --to main \\
        --title "feat: Complete Phase 0 Skills"

Author: code_developer
Date: 2025-10-19
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class PRInfo:
    """Pull request information."""

    title: str
    body: str
    from_branch: str
    to_branch: str
    commits: int
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None


class PRCreator:
    """Create GitHub PRs with auto-generated descriptions."""

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)

    def get_current_branch(self) -> str:
        """
        Get current git branch.

        Returns:
            Branch name
        """
        cmd = ["git", "branch", "--show-current"]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git branch failed: {e.stderr}")

    def get_commits_between_branches(self, from_branch: str, to_branch: str) -> List[str]:
        """
        Get commit messages between branches.

        Args:
            from_branch: Source branch
            to_branch: Target branch

        Returns:
            List of commit messages
        """
        # Use merge-base to find common ancestor
        cmd = ["git", "log", f"{to_branch}..{from_branch}", "--pretty=format:%s"]

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
            raise RuntimeError(f"Git log failed: {e.stderr}")

    def get_commit_details(self, from_branch: str, to_branch: str) -> List[Dict[str, str]]:
        """
        Get detailed commit information.

        Args:
            from_branch: Source branch
            to_branch: Target branch

        Returns:
            List of commit details
        """
        # Format: subject|body|hash
        cmd = [
            "git",
            "log",
            f"{to_branch}..{from_branch}",
            "--pretty=format:%s|%b|%h",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )

            commits = []
            for line in result.stdout.split("\n"):
                if not line.strip():
                    continue

                parts = line.split("|", 2)
                if len(parts) >= 3:
                    commits.append(
                        {
                            "subject": parts[0],
                            "body": parts[1],
                            "hash": parts[2],
                        }
                    )

            return commits

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git log failed: {e.stderr}")

    def parse_conventional_commits(self, commits: List[str]) -> Dict[str, List[str]]:
        """
        Parse conventional commits by type.

        Args:
            commits: List of commit messages

        Returns:
            Dict mapping commit type to list of subjects
        """
        categorized = {
            "feat": [],
            "fix": [],
            "refactor": [],
            "docs": [],
            "test": [],
            "perf": [],
            "chore": [],
            "other": [],
        }

        for commit in commits:
            # Extract type from conventional commit
            match = re.match(r"^(\w+)(?:\([^)]+\))?:\s*(.+)$", commit)
            if match:
                commit_type = match.group(1)
                subject = match.group(2)

                if commit_type in categorized:
                    categorized[commit_type].append(subject)
                else:
                    categorized["other"].append(commit)
            else:
                categorized["other"].append(commit)

        return categorized

    def extract_priority_references(self, commits: List[str]) -> Set[str]:
        """
        Extract priority references from commits.

        Args:
            commits: List of commit messages

        Returns:
            Set of priority identifiers
        """
        priorities = set()

        for commit in commits:
            # Look for US-XXX, PRIORITY X patterns
            us_matches = re.findall(r"US-\d+", commit, re.IGNORECASE)
            priorities.update(us_matches)

            priority_matches = re.findall(r"PRIORITY\s+\d+", commit, re.IGNORECASE)
            priorities.update(priority_matches)

        return priorities

    def extract_issue_references(self, commits: List[str]) -> Set[str]:
        """
        Extract GitHub issue references from commits.

        Args:
            commits: List of commit messages

        Returns:
            Set of issue numbers
        """
        issues = set()

        for commit in commits:
            # Look for #123, Closes #123, Fixes #123
            matches = re.findall(r"#(\d+)", commit)
            issues.update(matches)

        return issues

    def generate_pr_title(self, commits: List[str]) -> str:
        """
        Generate PR title from commits.

        Args:
            commits: List of commit messages

        Returns:
            PR title
        """
        if not commits:
            return "Update from branch"

        # Use first commit as title (usually most descriptive)
        first_commit = commits[0]

        # If it's a conventional commit, use it as-is
        if re.match(r"^\w+(?:\([^)]+\))?:", first_commit):
            return first_commit

        # Otherwise, try to generate a meaningful title
        return f"feat: {first_commit}"

    def generate_pr_body(
        self,
        commits: List[str],
        from_branch: str,
        to_branch: str,
        template: Optional[str] = None,
    ) -> str:
        """
        Generate PR body from commits.

        Args:
            commits: List of commit messages
            from_branch: Source branch
            to_branch: Target branch
            template: Custom template name

        Returns:
            PR body markdown
        """
        lines = []

        # Summary section
        lines.append("## Summary")
        lines.append("")

        # Parse commits by type
        categorized = self.parse_conventional_commits(commits)

        # Generate summary bullets
        summary_items = []
        for commit_type, subjects in categorized.items():
            if subjects and commit_type != "other":
                for subject in subjects:
                    summary_items.append(f"- {subject}")

        if summary_items:
            lines.extend(summary_items)
        else:
            lines.append(f"- Merge {from_branch} into {to_branch}")

        lines.append("")

        # Changes section
        lines.append("## Changes")
        lines.append("")

        if categorized["feat"]:
            lines.append("### Features")
            for subject in categorized["feat"]:
                lines.append(f"- {subject}")
            lines.append("")

        if categorized["fix"]:
            lines.append("### Bug Fixes")
            for subject in categorized["fix"]:
                lines.append(f"- {subject}")
            lines.append("")

        if categorized["refactor"]:
            lines.append("### Refactoring")
            for subject in categorized["refactor"]:
                lines.append(f"- {subject}")
            lines.append("")

        if categorized["docs"]:
            lines.append("### Documentation")
            for subject in categorized["docs"]:
                lines.append(f"- {subject}")
            lines.append("")

        if categorized["test"]:
            lines.append("### Tests")
            for subject in categorized["test"]:
                lines.append(f"- {subject}")
            lines.append("")

        # Commits section
        lines.append("## Commits")
        lines.append("")
        lines.append(f"Total commits: {len(commits)}")
        lines.append("")

        # Related work section
        priorities = self.extract_priority_references(commits)
        issues = self.extract_issue_references(commits)

        if priorities or issues:
            lines.append("## Related")
            lines.append("")

            if priorities:
                lines.append("Priorities: " + ", ".join(sorted(priorities)))
            if issues:
                lines.append("Issues: " + ", ".join(f"#{issue}" for issue in sorted(issues)))

            lines.append("")

        # Claude attribution
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")

        return "\n".join(lines)

    def create_pr(
        self,
        from_branch: Optional[str] = None,
        to_branch: str = "main",
        title: Optional[str] = None,
        body: Optional[str] = None,
        template: Optional[str] = None,
        draft: bool = False,
    ) -> PRInfo:
        """
        Create GitHub pull request.

        Args:
            from_branch: Source branch (None = current branch)
            to_branch: Target branch
            title: PR title (None = auto-generate)
            body: PR body (None = auto-generate)
            template: Template name for body
            draft: Create as draft PR

        Returns:
            PRInfo object
        """
        # Get source branch
        if from_branch is None:
            from_branch = self.get_current_branch()

        # Get commits
        commits = self.get_commits_between_branches(from_branch, to_branch)

        if not commits:
            raise ValueError(f"No commits between {to_branch} and {from_branch}")

        # Generate title if not provided
        if title is None:
            title = self.generate_pr_title(commits)

        # Generate body if not provided
        if body is None:
            body = self.generate_pr_body(commits, from_branch, to_branch, template)

        # Create PR using GitHub CLI
        cmd = [
            "gh",
            "pr",
            "create",
            "--base",
            to_branch,
            "--head",
            from_branch,
            "--title",
            title,
            "--body",
            body,
        ]

        if draft:
            cmd.append("--draft")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract PR URL from output
            pr_url = result.stdout.strip()

            # Extract PR number from URL
            pr_number = None
            match = re.search(r"/pull/(\d+)$", pr_url)
            if match:
                pr_number = int(match.group(1))

            return PRInfo(
                title=title,
                body=body,
                from_branch=from_branch,
                to_branch=to_branch,
                commits=len(commits),
                pr_url=pr_url,
                pr_number=pr_number,
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GitHub PR creation failed: {e.stderr}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create GitHub PRs with auto-generated descriptions")

    # Branch options
    parser.add_argument(
        "--from",
        dest="from_branch",
        help="Source branch (default: current branch)",
    )
    parser.add_argument(
        "--to",
        dest="to_branch",
        default="main",
        help="Target branch (default: main)",
    )

    # Auto mode
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Use default settings (roadmap → main)",
    )

    # Content options
    parser.add_argument(
        "--title",
        help="PR title (default: auto-generate from commits)",
    )
    parser.add_argument(
        "--body",
        help="PR body (default: auto-generate from commits)",
    )
    parser.add_argument(
        "--template",
        help="PR body template name",
    )

    # PR options
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create as draft PR",
    )

    # Other options
    parser.add_argument(
        "--codebase-root",
        default=".",
        help="Codebase root directory (default: current directory)",
    )

    args = parser.parse_args()

    try:
        creator = PRCreator(args.codebase_root)

        # Handle auto mode
        from_branch = args.from_branch
        to_branch = args.to_branch

        if args.auto:
            from_branch = "roadmap"
            to_branch = "main"

        # Create PR
        pr_info = creator.create_pr(
            from_branch=from_branch,
            to_branch=to_branch,
            title=args.title,
            body=args.body,
            template=args.template,
            draft=args.draft,
        )

        # Output success
        print(f"✅ PR created: #{pr_info.pr_number}")
        print(f"   Title: {pr_info.title}")
        print(f"   Commits: {pr_info.commits}")
        print(f"   URL: {pr_info.pr_url}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
