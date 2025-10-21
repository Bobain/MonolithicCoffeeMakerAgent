#!/usr/bin/env python3
"""
Semantic Tagger: Create semantic version tags with automatic version calculation.

This script creates git tags following semantic versioning and project
tagging conventions (wip-*, dod-verified-*, stable-v*).

Usage:
    # Auto-calculate version from commits
    python semantic_tagger.py --version-auto

    # Explicit version
    python semantic_tagger.py --version 1.3.0

    # Create WIP tag
    python semantic_tagger.py --type wip --name us-067

    # Create DoD verified tag
    python semantic_tagger.py --type dod-verified --name us-067

Author: code_developer
Date: 2025-10-19
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class VersionBump:
    """Version bump calculation result."""

    previous_version: str
    new_version: str
    bump_type: str  # major, minor, patch, none
    commits_analyzed: int
    feat_count: int
    fix_count: int
    breaking_count: int


@dataclass
class TagInfo:
    """Git tag information."""

    tag_name: str
    tag_type: str  # wip, dod-verified, stable
    version: Optional[str]
    message: str
    timestamp: str
    commits_included: int


class SemanticTagger:
    """Create semantic version tags with auto-calculation."""

    TAG_TYPES = {
        "wip": "Work in progress - implementation complete, tests passing",
        "dod-verified": "Definition of Done verified with Puppeteer",
        "stable": "Production release with semantic version",
    }

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)

    def get_latest_tag(self, tag_pattern: Optional[str] = None) -> Optional[str]:
        """
        Get the latest git tag.

        Args:
            tag_pattern: Pattern to filter tags (e.g., "stable-v*")

        Returns:
            Latest tag name or None
        """
        cmd = ["git", "describe", "--tags", "--abbrev=0"]

        if tag_pattern:
            cmd.extend(["--match", tag_pattern])

        try:
            result = subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def parse_version(self, version_string: str) -> Tuple[int, int, int]:
        """
        Parse semantic version string.

        Args:
            version_string: Version string (e.g., "v1.2.3" or "1.2.3")

        Returns:
            Tuple of (major, minor, patch)
        """
        # Remove 'v' prefix if present
        version_string = version_string.lstrip("v")

        # Extract version numbers
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_string)
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")

        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def get_commits_since_tag(self, tag_name: Optional[str] = None) -> List[str]:
        """
        Get commit messages since a tag.

        Args:
            tag_name: Tag to compare against (None = all commits)

        Returns:
            List of commit messages
        """
        if tag_name:
            cmd = ["git", "log", f"{tag_name}..HEAD", "--pretty=format:%s"]
        else:
            cmd = ["git", "log", "--pretty=format:%s"]

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

    def analyze_commits_for_version_bump(self, commits: List[str]) -> Tuple[str, int, int, int]:
        """
        Analyze commits to determine version bump type.

        Args:
            commits: List of commit messages

        Returns:
            Tuple of (bump_type, feat_count, fix_count, breaking_count)
        """
        feat_count = 0
        fix_count = 0
        breaking_count = 0

        for commit in commits:
            commit_lower = commit.lower()

            # Check for breaking changes
            if "breaking" in commit_lower or commit.endswith("!:"):
                breaking_count += 1
            # Check for features
            elif commit.startswith("feat"):
                feat_count += 1
            # Check for fixes
            elif commit.startswith("fix"):
                fix_count += 1

        # Determine bump type
        if breaking_count > 0:
            return "major", feat_count, fix_count, breaking_count
        elif feat_count > 0:
            return "minor", feat_count, fix_count, breaking_count
        elif fix_count > 0:
            return "patch", feat_count, fix_count, breaking_count
        else:
            return "none", feat_count, fix_count, breaking_count

    def calculate_next_version(self, current_version: Optional[str] = None) -> VersionBump:
        """
        Calculate next semantic version.

        Args:
            current_version: Current version (None = auto-detect from tags)

        Returns:
            VersionBump with calculation details
        """
        # Get current version
        if current_version is None:
            latest_stable = self.get_latest_tag("stable-v*")
            if latest_stable:
                current_version = latest_stable.replace("stable-", "")
            else:
                current_version = "v0.0.0"

        # Parse current version
        major, minor, patch = self.parse_version(current_version)

        # Get commits since last stable tag
        commits = self.get_commits_since_tag(
            f"stable-{current_version}" if not current_version.startswith("stable-") else current_version
        )

        # Analyze commits
        bump_type, feat_count, fix_count, breaking_count = self.analyze_commits_for_version_bump(commits)

        # Calculate new version
        if bump_type == "major":
            new_version = f"v{major + 1}.0.0"
        elif bump_type == "minor":
            new_version = f"v{major}.{minor + 1}.0"
        elif bump_type == "patch":
            new_version = f"v{major}.{minor}.{patch + 1}"
        else:
            new_version = current_version

        return VersionBump(
            previous_version=current_version,
            new_version=new_version,
            bump_type=bump_type,
            commits_analyzed=len(commits),
            feat_count=feat_count,
            fix_count=fix_count,
            breaking_count=breaking_count,
        )

    def generate_tag_message(
        self,
        tag_type: str,
        tag_name: str,
        version_bump: Optional[VersionBump] = None,
        custom_message: Optional[str] = None,
    ) -> str:
        """
        Generate tag message.

        Args:
            tag_type: Tag type (wip, dod-verified, stable)
            tag_name: Full tag name
            version_bump: Version bump info (for stable tags)
            custom_message: Custom message to include

        Returns:
            Tag message
        """
        lines = []

        # Title
        if tag_type == "wip":
            lines.append(f"WIP: {tag_name}")
            lines.append("")
            lines.append("Implementation complete, tests passing.")
        elif tag_type == "dod-verified":
            lines.append(f"DoD Verified: {tag_name}")
            lines.append("")
            lines.append("Definition of Done verification complete.")
        elif tag_type == "stable":
            lines.append(f"Release {tag_name}")
            lines.append("")
            if version_bump:
                lines.append(f"Version bump: {version_bump.previous_version} → {version_bump.new_version}")
                lines.append(f"Commits: {version_bump.commits_analyzed}")
                if version_bump.feat_count > 0:
                    lines.append(f"- Features: {version_bump.feat_count}")
                if version_bump.fix_count > 0:
                    lines.append(f"- Fixes: {version_bump.fix_count}")
                if version_bump.breaking_count > 0:
                    lines.append(f"- Breaking changes: {version_bump.breaking_count}")

        # Custom message
        if custom_message:
            lines.append("")
            lines.append(custom_message)

        # Timestamp
        lines.append("")
        lines.append(f"Tagged: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Claude attribution
        lines.append("")
        lines.append("🤖 Generated with Claude Code")

        return "\n".join(lines)

    def create_tag(
        self,
        tag_name: str,
        message: str,
        push: bool = False,
    ) -> TagInfo:
        """
        Create annotated git tag.

        Args:
            tag_name: Tag name
            message: Tag message
            push: Whether to push tag to remote

        Returns:
            TagInfo object
        """
        # Create annotated tag
        cmd = ["git", "tag", "-a", tag_name, "-m", message]

        try:
            subprocess.run(
                cmd,
                cwd=self.codebase_root,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git tag failed: {e.stderr}")

        # Push if requested
        if push:
            push_cmd = ["git", "push", "origin", tag_name]
            try:
                subprocess.run(
                    push_cmd,
                    cwd=self.codebase_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Git push failed: {e.stderr}")

        # Determine tag type
        if tag_name.startswith("wip-"):
            tag_type = "wip"
        elif tag_name.startswith("dod-verified-"):
            tag_type = "dod-verified"
        elif tag_name.startswith("stable-v"):
            tag_type = "stable"
        else:
            tag_type = "unknown"

        # Count commits included
        commits = self.get_commits_since_tag()

        return TagInfo(
            tag_name=tag_name,
            tag_type=tag_type,
            version=None,  # Could extract from tag_name if needed
            message=message,
            timestamp=datetime.now().isoformat(),
            commits_included=len(commits),
        )

    def create_wip_tag(self, priority_id: str, message: Optional[str] = None, push: bool = False) -> TagInfo:
        """
        Create WIP tag for priority.

        Args:
            priority_id: Priority identifier (e.g., "us-067")
            message: Custom message
            push: Whether to push tag

        Returns:
            TagInfo object
        """
        tag_name = f"wip-{priority_id.lower()}"
        tag_message = self.generate_tag_message("wip", tag_name, custom_message=message)

        return self.create_tag(tag_name, tag_message, push)

    def create_dod_verified_tag(self, priority_id: str, message: Optional[str] = None, push: bool = False) -> TagInfo:
        """
        Create DoD verified tag for priority.

        Args:
            priority_id: Priority identifier (e.g., "us-067")
            message: Custom message
            push: Whether to push tag

        Returns:
            TagInfo object
        """
        tag_name = f"dod-verified-{priority_id.lower()}"
        tag_message = self.generate_tag_message("dod-verified", tag_name, custom_message=message)

        return self.create_tag(tag_name, tag_message, push)

    def create_stable_tag(
        self,
        version: Optional[str] = None,
        auto_calculate: bool = False,
        message: Optional[str] = None,
        push: bool = False,
    ) -> TagInfo:
        """
        Create stable release tag.

        Args:
            version: Explicit version (e.g., "1.3.0")
            auto_calculate: Auto-calculate version from commits
            message: Custom message
            push: Whether to push tag

        Returns:
            TagInfo object
        """
        version_bump = None

        if auto_calculate:
            version_bump = self.calculate_next_version()
            version = version_bump.new_version
        elif version is None:
            raise ValueError("Must provide version or use --version-auto")

        # Ensure version starts with 'v'
        if not version.startswith("v"):
            version = f"v{version}"

        tag_name = f"stable-{version}"
        tag_message = self.generate_tag_message("stable", tag_name, version_bump, message)

        return self.create_tag(tag_name, tag_message, push)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create semantic version tags with auto-calculation")

    # Version options
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--version",
        help="Explicit version (e.g., 1.3.0 or v1.3.0)",
    )
    version_group.add_argument(
        "--version-auto",
        action="store_true",
        help="Auto-calculate version from commits",
    )

    # Tag type options
    parser.add_argument(
        "--type",
        choices=["wip", "dod-verified", "stable"],
        help="Tag type (required for wip/dod-verified)",
    )
    parser.add_argument(
        "--name",
        help="Priority identifier for wip/dod-verified tags (e.g., us-067)",
    )

    # Message options
    parser.add_argument(
        "--message",
        help="Custom tag message",
    )

    # Push option
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push tag to remote after creation",
    )

    # Other options
    parser.add_argument(
        "--codebase-root",
        default=".",
        help="Codebase root directory (default: current directory)",
    )

    args = parser.parse_args()

    try:
        tagger = SemanticTagger(args.codebase_root)

        # Create tag based on type
        if args.type == "wip":
            if not args.name:
                raise ValueError("--name required for WIP tags")
            tag_info = tagger.create_wip_tag(args.name, args.message, args.push)

        elif args.type == "dod-verified":
            if not args.name:
                raise ValueError("--name required for DoD verified tags")
            tag_info = tagger.create_dod_verified_tag(args.name, args.message, args.push)

        elif args.type == "stable" or args.version or args.version_auto:
            tag_info = tagger.create_stable_tag(
                version=args.version,
                auto_calculate=args.version_auto,
                message=args.message,
                push=args.push,
            )

        else:
            raise ValueError("Must specify --type (wip/dod-verified/stable) or --version/--version-auto")

        # Output success
        print(f"✅ Tag created: {tag_info.tag_name}")
        print(f"   Type: {tag_info.tag_type}")
        print(f"   Commits: {tag_info.commits_included}")
        if args.push:
            print(f"   Pushed: Yes")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
