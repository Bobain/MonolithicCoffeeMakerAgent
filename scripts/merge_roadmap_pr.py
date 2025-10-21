#!/usr/bin/env python3
"""Automated PR merge script for roadmap updates.

This script automates the creation and merging of Pull Requests for
roadmap and documentation updates to the 'roadmap' branch on GitHub.

⚠️ IMPORTANT: Only use this for docs/roadmap/ROADMAP.md and docs/*.md updates!

Usage:
    python scripts/merge_roadmap_pr.py <branch-name> [--base roadmap|main]

Examples:
    # Merge to roadmap branch (default)
    python scripts/merge_roadmap_pr.py feature/roadmap-update

    # Merge to main branch
    python scripts/merge_roadmap_pr.py feature/roadmap-update --base main

Environment Variables Required:
    GITHUB_TOKEN: GitHub Personal Access Token with 'repo' scope

Safety Features:
    - Only merges if changes are in docs/ directory
    - Respects GitHub branch protection rules
    - Detects merge conflicts
    - Falls back to manual review if auto-merge fails
"""

import os
import sys
from typing import Optional

try:
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    print("❌ PyGithub not installed")
    print("\nInstall with: poetry add PyGithub")
    sys.exit(1)

# Add project to path for ConfigManager import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coffee_maker.config import ConfigManager


class RoadmapPRMerger:
    """Handles automated PR creation and merging for roadmap updates."""

    def __init__(self, repo_name: str = "Bobain/MonolithicCoffeeMakerAgent"):
        """Initialize the PR merger.

        Args:
            repo_name: GitHub repository in format 'owner/repo'
        """
        self.repo_name = repo_name

        try:
            token = ConfigManager.get_github_token()
        except Exception:
            print("❌ GITHUB_TOKEN environment variable not set")
            print("\nGet your token from: https://github.com/settings/tokens")
            print("Then set it:")
            print("  export GITHUB_TOKEN='your-token-here'")
            print("  # Or add to .env file")
            sys.exit(1)

        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def validate_branch_changes(self, branch_name: str, base_branch: str = "roadmap") -> tuple[bool, str]:
        """Validate that branch only contains documentation changes.

        Args:
            branch_name: Name of the feature branch
            base_branch: Base branch to compare against (default: roadmap)

        Returns:
            (is_valid, message) tuple
        """
        try:
            # Get the comparison with base branch
            comparison = self.repo.compare(base_branch, branch_name)

            # Check changed files
            changed_files = [f.filename for f in comparison.files]

            if not changed_files:
                return False, "No changes detected in branch"

            # Ensure all changes are in docs/
            non_doc_files = [f for f in changed_files if not f.startswith("docs/")]

            if non_doc_files:
                return (
                    False,
                    f"❌ Non-documentation files detected: {', '.join(non_doc_files)}\n\n⚠️  This script is ONLY for docs/ updates!",
                )

            return True, f"✅ All changes are in docs/ ({len(changed_files)} files)"

        except GithubException as e:
            return False, f"Failed to validate branch: {e}"

    def create_pr(
        self, branch_name: str, base_branch: str = "roadmap", title: Optional[str] = None, body: Optional[str] = None
    ) -> Optional[object]:
        """Create a Pull Request.

        Args:
            branch_name: Source branch name
            base_branch: Target branch name (default: roadmap)
            title: PR title (optional, auto-generated if not provided)
            body: PR description (optional, auto-generated if not provided)

        Returns:
            PR object if successful, None otherwise
        """
        # Validate changes first
        is_valid, message = self.validate_branch_changes(branch_name, base_branch)
        print(message)

        if not is_valid:
            return None

        # Generate title if not provided
        if not title:
            title = f"docs: Update roadmap and documentation ({branch_name})"

        # Generate body if not provided
        if not body:
            comparison = self.repo.compare(base_branch, branch_name)
            changed_files = [f.filename for f in comparison.files]

            body = f"""## Summary

Automated roadmap and documentation update targeting `{base_branch}` branch.

## Changes

Updated files:
{chr(10).join(f'- `{f}`' for f in changed_files)}

## Review Notes

- This is an automated documentation update
- All changes are in `docs/` directory
- Target branch: `{base_branch}`
- Safe to auto-merge

🤖 Auto-generated via merge_roadmap_pr.py script

---

**Process**: See COLLABORATION_METHODOLOGY.md section 9.3
            """

        try:
            pr = self.repo.create_pull(title=title, body=body, head=branch_name, base=base_branch)

            print(f"✅ PR created targeting '{base_branch}' branch: {pr.html_url}")
            print(f"   Number: #{pr.number}")
            print(f"   Title: {pr.title}")
            print(f"   Base: {base_branch} ← {branch_name}")

            return pr

        except GithubException as e:
            print(f"❌ Failed to create PR: {e}")
            return None

    def merge_pr(self, pr) -> bool:
        """Merge a Pull Request.

        Args:
            pr: PR object from GitHub API

        Returns:
            True if merged successfully, False otherwise
        """
        try:
            # Wait a moment for GitHub to process the PR
            import time

            time.sleep(2)

            # Refresh PR state
            pr.update()

            # Check if mergeable
            if pr.mergeable is False:
                print(f"⚠️  PR has merge conflicts - manual review required")
                print(f"   Please review and merge manually: {pr.html_url}")
                return False

            if pr.mergeable_state == "blocked":
                print(f"⚠️  PR is blocked by branch protection rules")
                print(f"   Please review and merge manually: {pr.html_url}")
                return False

            # Merge with squash strategy
            merge_result = pr.merge(merge_method="squash", commit_title=pr.title, commit_message=pr.body)

            if merge_result.merged:
                print(f"✅ PR merged successfully!")
                print(f"   Merge commit: {merge_result.sha}")
                return True
            else:
                print(f"⚠️  PR merge returned False - manual review required")
                print(f"   Please review: {pr.html_url}")
                return False

        except GithubException as e:
            print(f"⚠️  Failed to merge PR: {e}")
            print(f"   Please merge manually: {pr.html_url}")
            return False

    def process_branch(self, branch_name: str, base_branch: str = "roadmap", auto_merge: bool = True) -> bool:
        """Create PR and optionally auto-merge.

        Args:
            branch_name: Name of the feature branch
            base_branch: Target branch name (default: roadmap)
            auto_merge: Whether to automatically merge the PR

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*70}")
        print(f"Processing branch: {branch_name} → {base_branch}")
        print(f"{'='*70}\n")

        # Create PR
        pr = self.create_pr(branch_name, base_branch)
        if not pr:
            return False

        # Auto-merge if requested
        if auto_merge:
            print("\n⏳ Attempting auto-merge...")
            return self.merge_pr(pr)
        else:
            print("\n✅ PR created - manual merge required")
            print(f"   Review and merge: {pr.html_url}")
            return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/merge_roadmap_pr.py <branch-name> [--base roadmap|main] [--no-merge]")
        print("\nExamples:")
        print("  # Merge to roadmap branch (default)")
        print("  python scripts/merge_roadmap_pr.py feature/roadmap-update")
        print()
        print("  # Merge to main branch")
        print("  python scripts/merge_roadmap_pr.py feature/roadmap-update --base main")
        print()
        print("  # Create PR but don't auto-merge")
        print("  python scripts/merge_roadmap_pr.py feature/roadmap-update --no-merge")
        sys.exit(1)

    branch_name = sys.argv[1]

    # Parse base branch argument (default: roadmap)
    base_branch = "roadmap"
    if "--base" in sys.argv:
        base_index = sys.argv.index("--base")
        if base_index + 1 < len(sys.argv):
            base_branch = sys.argv[base_index + 1]

    # Optional: disable auto-merge with --no-merge flag
    auto_merge = "--no-merge" not in sys.argv

    merger = RoadmapPRMerger()
    success = merger.process_branch(branch_name, base_branch=base_branch, auto_merge=auto_merge)

    if success:
        print("\n🎉 Success!")
        if auto_merge:
            print("\n📝 Next steps:")
            print("  git checkout main")
            print("  git pull origin main")
            print(f"  git branch -d {branch_name}")
    else:
        print("\n⚠️  Process incomplete - see messages above")
        sys.exit(1)


if __name__ == "__main__":
    main()
