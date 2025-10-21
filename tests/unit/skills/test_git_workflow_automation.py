"""
Unit tests for git-workflow-automation skill scripts.

Tests the core functionality of git commit generation, semantic versioning,
and PR creation.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent.parent / ".claude" / "skills" / "git-workflow-automation" / "scripts"
sys.path.insert(0, str(scripts_dir))

from git_commit_generator import CommitMessage, GitCommitGenerator
from pr_creator import PRCreator
from semantic_tagger import SemanticTagger, VersionBump


class TestGitCommitGenerator:
    """Test git commit message generation."""

    def test_detect_commit_type_docs(self):
        """Test detection of docs commit type."""
        generator = GitCommitGenerator()
        files = ["docs/README.md", "docs/GUIDE.md"]
        assert generator.detect_commit_type(files) == "docs"

    def test_detect_commit_type_test(self):
        """Test detection of test commit type."""
        generator = GitCommitGenerator()
        files = ["tests/test_feature.py", "tests/test_utils.py"]
        assert generator.detect_commit_type(files) == "test"

    def test_detect_commit_type_config(self):
        """Test detection of config commit type."""
        generator = GitCommitGenerator()
        files = ["pyproject.toml", "config.yaml"]
        assert generator.detect_commit_type(files) == "chore"

    def test_detect_commit_type_code(self):
        """Test detection of code commit type (defaults to feat)."""
        generator = GitCommitGenerator()
        files = ["coffee_maker/api/routes.py", "coffee_maker/utils/helpers.py"]
        assert generator.detect_commit_type(files) == "feat"

    def test_detect_scope_daemon(self):
        """Test scope detection for daemon files."""
        generator = GitCommitGenerator()
        files = ["coffee_maker/autonomous/daemon.py", "coffee_maker/autonomous/mixins.py"]
        assert generator.detect_scope(files) == "daemon"

    def test_detect_scope_skills(self):
        """Test scope detection for skills files."""
        generator = GitCommitGenerator()
        files = [".claude/skills/test-skill/SKILL.md"]
        assert generator.detect_scope(files) == "skills"

    def test_detect_scope_tests(self):
        """Test scope detection for test files."""
        generator = GitCommitGenerator()
        files = ["tests/unit/test_feature.py", "tests/integration/test_api.py"]
        assert generator.detect_scope(files) == "tests"

    def test_detect_scope_no_match(self):
        """Test scope detection with no pattern match."""
        generator = GitCommitGenerator()
        files = ["random_file.py"]
        assert generator.detect_scope(files) is None

    def test_detect_scope_multiple_files(self):
        """Test scope detection with multiple scopes (returns most common)."""
        generator = GitCommitGenerator()
        files = [
            "coffee_maker/autonomous/daemon.py",
            "coffee_maker/autonomous/mixins.py",
            "coffee_maker/cli/commands.py",
        ]
        # daemon appears twice, cli once - should return daemon
        assert generator.detect_scope(files) == "daemon"

    def test_generate_subject_docs_spec(self):
        """Test subject generation for spec documentation."""
        generator = GitCommitGenerator()
        files = ["docs/architecture/specs/SPEC-067-git-workflow.md"]
        subject = generator.generate_subject(files, "docs", "specs")
        assert "specification" in subject.lower()

    def test_generate_subject_docs_adr(self):
        """Test subject generation for ADR documentation."""
        generator = GitCommitGenerator()
        files = ["docs/architecture/decisions/ADR-013-dependency-management.md"]
        subject = generator.generate_subject(files, "docs", "adrs")
        assert "decision record" in subject.lower()

    def test_generate_subject_test(self):
        """Test subject generation for tests."""
        generator = GitCommitGenerator()
        files = ["tests/test_feature.py"]
        subject = generator.generate_subject(files, "test", "tests")
        assert "test" in subject.lower()

    def test_generate_subject_skills(self):
        """Test subject generation for skills."""
        generator = GitCommitGenerator()
        files = [".claude/skills/test-skill/SKILL.md"]
        subject = generator.generate_subject(files, "feat", "skills")
        assert "skill" in subject.lower()

    def test_generate_body(self):
        """Test body generation with categorized files."""
        generator = GitCommitGenerator()
        files = [
            "coffee_maker/api/routes.py",
            "tests/test_api.py",
            "docs/API.md",
        ]
        body = generator.generate_body(files, "")

        # Should have bullet points for different categories
        assert any("Implementation" in line for line in body)
        assert any("Tests" in line for line in body)
        assert any("Documentation" in line for line in body)

    def test_generate_footer_with_priority(self):
        """Test footer generation with priority reference."""
        generator = GitCommitGenerator()
        footer = generator.generate_footer(priority_id="US-067")
        assert any("US-067" in line for line in footer)

    def test_generate_footer_with_issue(self):
        """Test footer generation with issue reference."""
        generator = GitCommitGenerator()
        footer = generator.generate_footer(issue_id="123")
        assert any("#123" in line for line in footer)

    def test_commit_message_format(self):
        """Test conventional commit message formatting."""
        message = CommitMessage(
            type="feat",
            scope="api",
            subject="Add pagination support",
            body=["- Implement offset/limit parameters", "- Add validation"],
            footer=["Implements: US-067"],
            breaking_change=False,
        )

        formatted = message.format()

        # Check header
        assert formatted.startswith("feat(api): Add pagination support")

        # Check body
        assert "- Implement offset/limit parameters" in formatted
        assert "- Add validation" in formatted

        # Check footer
        assert "Implements: US-067" in formatted
        assert "🤖 Generated with" in formatted
        assert "Co-Authored-By: Claude" in formatted

    def test_commit_message_format_breaking_change(self):
        """Test breaking change formatting."""
        message = CommitMessage(
            type="feat",
            scope="api",
            subject="Change API structure",
            body=["- Restructure endpoints"],
            footer=[],
            breaking_change=True,
        )

        formatted = message.format()
        assert formatted.startswith("feat(api)!: Change API structure")

    def test_commit_message_format_no_scope(self):
        """Test formatting without scope."""
        message = CommitMessage(
            type="docs",
            scope=None,
            subject="Update README",
            body=[],
            footer=[],
            breaking_change=False,
        )

        formatted = message.format()
        assert formatted.startswith("docs: Update README")


class TestSemanticTagger:
    """Test semantic versioning and tagging."""

    def test_parse_version(self):
        """Test version string parsing."""
        tagger = SemanticTagger()

        # With 'v' prefix
        major, minor, patch = tagger.parse_version("v1.2.3")
        assert (major, minor, patch) == (1, 2, 3)

        # Without 'v' prefix
        major, minor, patch = tagger.parse_version("1.2.3")
        assert (major, minor, patch) == (1, 2, 3)

    def test_parse_version_invalid(self):
        """Test parsing invalid version string."""
        tagger = SemanticTagger()
        with pytest.raises(ValueError):
            tagger.parse_version("invalid")

    def test_analyze_commits_for_version_bump_major(self):
        """Test version bump analysis for major release."""
        tagger = SemanticTagger()
        commits = [
            "feat: Add feature",
            "fix: Fix bug",
            "feat!: Breaking change",
        ]

        bump_type, feat_count, fix_count, breaking_count = tagger.analyze_commits_for_version_bump(commits)

        assert bump_type == "major"
        assert breaking_count == 1

    def test_analyze_commits_for_version_bump_minor(self):
        """Test version bump analysis for minor release."""
        tagger = SemanticTagger()
        commits = [
            "feat: Add feature",
            "fix: Fix bug",
            "docs: Update docs",
        ]

        bump_type, feat_count, fix_count, breaking_count = tagger.analyze_commits_for_version_bump(commits)

        assert bump_type == "minor"
        assert feat_count == 1

    def test_analyze_commits_for_version_bump_patch(self):
        """Test version bump analysis for patch release."""
        tagger = SemanticTagger()
        commits = [
            "fix: Fix bug",
            "fix: Another fix",
        ]

        bump_type, feat_count, fix_count, breaking_count = tagger.analyze_commits_for_version_bump(commits)

        assert bump_type == "patch"
        assert fix_count == 2

    def test_analyze_commits_for_version_bump_none(self):
        """Test version bump analysis with no version-affecting commits."""
        tagger = SemanticTagger()
        commits = [
            "docs: Update documentation",
            "test: Add tests",
            "chore: Update config",
        ]

        bump_type, feat_count, fix_count, breaking_count = tagger.analyze_commits_for_version_bump(commits)

        assert bump_type == "none"

    def test_generate_tag_message_wip(self):
        """Test WIP tag message generation."""
        tagger = SemanticTagger()
        message = tagger.generate_tag_message("wip", "wip-us-067")

        assert "WIP: wip-us-067" in message
        assert "Implementation complete" in message
        assert "🤖 Generated with" in message

    def test_generate_tag_message_dod_verified(self):
        """Test DoD verified tag message generation."""
        tagger = SemanticTagger()
        message = tagger.generate_tag_message("dod-verified", "dod-verified-us-067")

        assert "DoD Verified: dod-verified-us-067" in message
        assert "Definition of Done" in message

    def test_generate_tag_message_stable(self):
        """Test stable release tag message generation."""
        tagger = SemanticTagger()
        version_bump = VersionBump(
            previous_version="v1.2.0",
            new_version="v1.3.0",
            bump_type="minor",
            commits_analyzed=5,
            feat_count=2,
            fix_count=1,
            breaking_count=0,
        )
        message = tagger.generate_tag_message("stable", "stable-v1.3.0", version_bump)

        assert "Release stable-v1.3.0" in message
        assert "v1.2.0 → v1.3.0" in message
        assert "Commits: 5" in message
        assert "Features: 2" in message
        assert "Fixes: 1" in message

    def test_generate_tag_message_custom(self):
        """Test tag message with custom message."""
        tagger = SemanticTagger()
        custom_msg = "This is a custom message"
        message = tagger.generate_tag_message("wip", "wip-test", custom_message=custom_msg)

        assert custom_msg in message


class TestPRCreator:
    """Test PR creation."""

    def test_parse_conventional_commits(self):
        """Test parsing conventional commits by type."""
        creator = PRCreator()
        commits = [
            "feat: Add feature",
            "feat(api): Add API endpoint",
            "fix: Fix bug",
            "fix(auth): Fix authentication",
            "docs: Update docs",
            "test: Add tests",
            "chore: Update config",
            "Random commit without type",
        ]

        categorized = creator.parse_conventional_commits(commits)

        assert len(categorized["feat"]) == 2
        assert len(categorized["fix"]) == 2
        assert len(categorized["docs"]) == 1
        assert len(categorized["test"]) == 1
        assert len(categorized["chore"]) == 1
        assert len(categorized["other"]) == 1

    def test_extract_priority_references(self):
        """Test extracting priority references from commits."""
        creator = PRCreator()
        commits = [
            "feat: Add feature (US-067)",
            "fix: Fix bug for PRIORITY 5",
            "docs: Update docs US-068",
        ]

        priorities = creator.extract_priority_references(commits)

        assert "US-067" in priorities
        assert "US-068" in priorities
        assert "PRIORITY 5" in priorities or "PRIORITY  5" in priorities

    def test_extract_issue_references(self):
        """Test extracting GitHub issue references from commits."""
        creator = PRCreator()
        commits = [
            "feat: Add feature (#123)",
            "fix: Fix bug (Closes #456)",
            "docs: Update docs Fixes #789",
        ]

        issues = creator.extract_issue_references(commits)

        assert "123" in issues
        assert "456" in issues
        assert "789" in issues

    def test_generate_pr_title_conventional(self):
        """Test PR title generation from conventional commit."""
        creator = PRCreator()
        commits = [
            "feat(api): Add pagination support",
            "fix(api): Handle edge cases",
        ]

        title = creator.generate_pr_title(commits)
        assert title == "feat(api): Add pagination support"

    def test_generate_pr_title_fallback(self):
        """Test PR title generation fallback for non-conventional commit."""
        creator = PRCreator()
        commits = ["Add pagination support"]

        title = creator.generate_pr_title(commits)
        assert title.startswith("feat:")

    def test_generate_pr_body(self):
        """Test PR body generation."""
        creator = PRCreator()
        commits = [
            "feat: Add feature",
            "fix: Fix bug",
            "docs: Update docs",
        ]

        body = creator.generate_pr_body(commits, "roadmap", "main")

        # Check structure
        assert "## Summary" in body
        assert "## Changes" in body
        assert "## Commits" in body
        assert "🤖 Generated with" in body

        # Check content
        assert "Add feature" in body
        assert "Fix bug" in body
        assert "Update docs" in body

    def test_generate_pr_body_with_references(self):
        """Test PR body generation with priority and issue references."""
        creator = PRCreator()
        commits = [
            "feat: Add feature (US-067) (#123)",
            "fix: Fix bug (US-068)",
        ]

        body = creator.generate_pr_body(commits, "roadmap", "main")

        assert "## Related" in body
        assert "US-067" in body
        assert "US-068" in body
        assert "#123" in body


def test_scripts_have_shebang():
    """Test that all scripts have proper shebang."""
    scripts = [
        scripts_dir / "git_commit_generator.py",
        scripts_dir / "semantic_tagger.py",
        scripts_dir / "pr_creator.py",
    ]

    for script in scripts:
        with open(script) as f:
            first_line = f.readline()
            assert first_line.startswith("#!/usr/bin/env python3")


def test_scripts_have_docstrings():
    """Test that all scripts have module docstrings."""
    scripts = [
        scripts_dir / "git_commit_generator.py",
        scripts_dir / "semantic_tagger.py",
        scripts_dir / "pr_creator.py",
    ]

    for script in scripts:
        with open(script) as f:
            content = f.read()
            # Check for triple-quoted docstring
            assert '"""' in content[:500]  # Should be near top of file
