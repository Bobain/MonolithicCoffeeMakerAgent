#!/usr/bin/env python3
"""
Git Workflow Automation CLI

Usage:
    # Generate commit message
    python git_workflow.py commit --priority "US-067" --description "..."

    # Create semantic version tag
    python git_workflow.py tag --type wip --name us-067

    # Create pull request
    python git_workflow.py pr --title "Implement US-067" --priority "US-067"

    # Full workflow (commit + tag + pr)
    python git_workflow.py workflow --priority "US-067" --description "..."
"""

import argparse
import json
import sys
from pathlib import Path

# Add coffee_maker to path
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from claude.skills.git_workflow import (
    CommitMessageGenerator,
    PullRequestCreator,
    SemanticVersioner,
)


def cmd_commit(args: argparse.Namespace) -> int:
    """Generate and optionally create commit.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    generator = CommitMessageGenerator(repo_path=args.repo_path)

    # Generate commit message
    commit_msg = generator.generate(
        priority_name=args.priority,
        priority_description=args.description,
        diff_since=args.diff_since,
        staged_only=args.staged_only,
        override_type=args.type,
        override_scope=args.scope,
    )

    # Output format
    if args.format == "json":
        result = {
            "type": commit_msg.type,
            "scope": commit_msg.scope,
            "subject": commit_msg.subject,
            "body": commit_msg.body,
            "footer": commit_msg.footer,
            "full_message": commit_msg.format(),
        }
        print(json.dumps(result, indent=2))
    else:
        # Text format (ready for git commit -m)
        print(commit_msg.format())

    # Optionally create commit
    if args.create:
        import subprocess

        try:
            # Stage files if requested
            if args.stage_all:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=args.repo_path,
                    check=True,
                )

            # Create commit
            subprocess.run(
                ["git", "commit", "-m", commit_msg.format()],
                cwd=args.repo_path,
                check=True,
            )
            print(f"\n✅ Commit created successfully", file=sys.stderr)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to create commit: {e}", file=sys.stderr)
            return 1

    return 0


def cmd_tag(args: argparse.Namespace) -> int:
    """Create semantic version tag.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    versioner = SemanticVersioner(repo_path=args.repo_path)

    # Calculate version bump if auto
    if args.auto_version:
        bump = versioner.calculate_version_bump(
            since_tag=args.since_tag,
            override_version=None,
        )
        print(f"Version bump: {bump.current_version} → {bump.new_version}")
        print(f"Reason: {bump.reason}")
        print()

    # Create tag
    tag_result = versioner.create_tag(
        tag_type=args.type,
        name=args.name,
        message=args.message,
        version=args.version,
    )

    if tag_result.created:
        print(f"✅ Tag created: {tag_result.tag_name}")
        print(f"\nMessage:\n{tag_result.message}")

        # Optionally push tag
        if args.push:
            import subprocess

            try:
                subprocess.run(
                    ["git", "push", "origin", tag_result.tag_name],
                    cwd=args.repo_path,
                    check=True,
                )
                print(f"\n✅ Tag pushed to remote")
                return 0
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Failed to push tag: {e}", file=sys.stderr)
                return 1
    else:
        print(f"❌ Failed to create tag: {tag_result.tag_name}", file=sys.stderr)
        return 1

    return 0


def cmd_pr(args: argparse.Namespace) -> int:
    """Create pull request.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    creator = PullRequestCreator(repo_path=args.repo_path)

    # Create PR
    pr_result = creator.create(
        title=args.title,
        priority_name=args.priority,
        priority_description=args.description,
        dod_report_path=args.dod_report,
        base_branch=args.base,
        head_branch=args.head,
        auto_body=not args.custom_body,
        custom_body=args.custom_body,
    )

    if pr_result.created:
        print(f"✅ Pull request created: #{pr_result.number}")
        print(f"URL: {pr_result.url}")
        print()
        print(f"Title: {pr_result.title}")
        return 0
    else:
        print(f"❌ Failed to create pull request", file=sys.stderr)
        return 1


def cmd_workflow(args: argparse.Namespace) -> int:
    """Execute full workflow: commit + tag + PR.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    # Step 1: Generate and create commit
    print("Step 1: Creating commit...")
    generator = CommitMessageGenerator(repo_path=args.repo_path)
    commit_msg = generator.generate(
        priority_name=args.priority,
        priority_description=args.description,
        staged_only=False,
    )

    import subprocess

    try:
        # Stage all files
        subprocess.run(["git", "add", "."], cwd=args.repo_path, check=True)

        # Create commit
        subprocess.run(
            ["git", "commit", "-m", commit_msg.format()],
            cwd=args.repo_path,
            check=True,
        )
        print(f"✅ Commit created: {commit_msg.subject}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create commit: {e}", file=sys.stderr)
        return 1

    # Step 2: Create WIP tag
    print("\nStep 2: Creating WIP tag...")
    versioner = SemanticVersioner(repo_path=args.repo_path)
    tag_name = args.priority.lower().replace(" ", "-") if args.priority else "wip"
    tag_result = versioner.create_tag(tag_type="wip", name=tag_name)

    if tag_result.created:
        print(f"✅ Tag created: {tag_result.tag_name}")
    else:
        print(f"⚠️  Tag creation skipped (may already exist)")

    # Step 3: Push to remote
    print("\nStep 3: Pushing to remote...")
    try:
        subprocess.run(
            ["git", "push", "origin", "roadmap"],
            cwd=args.repo_path,
            check=True,
        )
        if tag_result.created:
            subprocess.run(
                ["git", "push", "origin", tag_result.tag_name],
                cwd=args.repo_path,
                check=True,
            )
        print(f"✅ Pushed to remote")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push: {e}", file=sys.stderr)
        return 1

    # Step 4: Create PR (if requested)
    if args.create_pr:
        print("\nStep 4: Creating pull request...")
        creator = PullRequestCreator(repo_path=args.repo_path)
        pr_title = args.title or f"Implement {args.priority}"

        pr_result = creator.create(
            title=pr_title,
            priority_name=args.priority,
            priority_description=args.description,
            dod_report_path=args.dod_report,
        )

        if pr_result.created:
            print(f"✅ Pull request created: #{pr_result.number}")
            print(f"URL: {pr_result.url}")
        else:
            print(f"⚠️  PR creation skipped (may already exist)")

    print("\n✅ Workflow complete!")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Git Workflow Automation - Conventional commits, semantic versioning, PR creation"
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path.cwd(),
        help="Path to git repository (default: current directory)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Generate conventional commit message")
    commit_parser.add_argument("--priority", help="Priority identifier (e.g., US-067)")
    commit_parser.add_argument("--description", help="Priority description")
    commit_parser.add_argument("--diff-since", help="Diff since commit (default: HEAD)")
    commit_parser.add_argument("--staged-only", action="store_true", help="Only analyze staged files")
    commit_parser.add_argument(
        "--type",
        choices=["feat", "fix", "refactor", "docs", "test", "perf", "chore"],
        help="Override commit type",
    )
    commit_parser.add_argument("--scope", help="Override scope")
    commit_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    commit_parser.add_argument("--create", action="store_true", help="Create commit (not just generate message)")
    commit_parser.add_argument("--stage-all", action="store_true", help="Stage all files before commit")

    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Create semantic version tag")
    tag_parser.add_argument(
        "--type",
        choices=["wip", "dod-verified", "stable"],
        required=True,
        help="Tag type",
    )
    tag_parser.add_argument("--name", required=True, help="Tag name/identifier")
    tag_parser.add_argument("--message", help="Custom tag message")
    tag_parser.add_argument("--version", help="Version for stable tags (e.g., 1.3.0)")
    tag_parser.add_argument(
        "--auto-version",
        action="store_true",
        help="Auto-calculate version from commits",
    )
    tag_parser.add_argument("--since-tag", help="Calculate version since tag")
    tag_parser.add_argument("--push", action="store_true", help="Push tag to remote")

    # PR command
    pr_parser = subparsers.add_parser("pr", help="Create pull request")
    pr_parser.add_argument("--title", required=True, help="PR title")
    pr_parser.add_argument("--priority", help="Priority identifier")
    pr_parser.add_argument("--description", help="Priority description")
    pr_parser.add_argument("--dod-report", help="Path to DoD verification report")
    pr_parser.add_argument("--base", default="main", help="Base branch (default: main)")
    pr_parser.add_argument("--head", default="roadmap", help="Head branch (default: roadmap)")
    pr_parser.add_argument("--custom-body", help="Custom PR body (overrides auto)")

    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Execute full workflow (commit + tag + push + PR)")
    workflow_parser.add_argument("--priority", required=True, help="Priority identifier (e.g., US-067)")
    workflow_parser.add_argument("--description", help="Priority description")
    workflow_parser.add_argument("--title", help="PR title (default: from priority)")
    workflow_parser.add_argument("--dod-report", help="Path to DoD verification report")
    workflow_parser.add_argument("--create-pr", action="store_true", help="Create PR after commit/tag/push")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "commit":
        return cmd_commit(args)
    elif args.command == "tag":
        return cmd_tag(args)
    elif args.command == "pr":
        return cmd_pr(args)
    elif args.command == "workflow":
        return cmd_workflow(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
