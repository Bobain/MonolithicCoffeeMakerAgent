"""Tests for git branch strategy (tag-based workflow).

This module tests the critical git strategy implementation that enforces:
1. All work happens on 'roadmap' branch
2. code_developer uses tags instead of branches
3. No branch switching allowed
4. Parallel agent operations are safe

CRITICAL: These tests ensure the safety mechanisms work correctly.
"""

import pytest
from unittest.mock import Mock, patch

from coffee_maker.autonomous.git_strategy import (
    AgentGitOps,
    CodeDeveloperGitOps,
    GitStrategy,
)


class TestGitStrategy:
    """Tests for core GitStrategy operations."""

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch name."""
        # Setup
        mock_run.return_value = Mock(stdout="roadmap\n")

        # Execute
        result = GitStrategy.get_current_branch()

        # Verify
        assert result == "roadmap"
        mock_run.assert_called_once_with(
            ["git", "branch", "--show-current"], capture_output=True, text=True, check=True
        )

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_verify_on_roadmap_branch_success(self, mock_run):
        """Test verification succeeds when on roadmap branch."""
        # Setup
        mock_run.return_value = Mock(stdout="roadmap\n")

        # Execute
        result = GitStrategy.verify_on_roadmap_branch()

        # Verify
        assert result is True

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_verify_on_roadmap_branch_failure(self, mock_run):
        """Test verification fails when on wrong branch."""
        # Setup
        mock_run.return_value = Mock(stdout="feature/some-branch\n")

        # Execute
        result = GitStrategy.verify_on_roadmap_branch()

        # Verify
        assert result is False

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_create_tag_success(self, mock_verify, mock_run):
        """Test successful tag creation."""
        # Setup
        mock_verify.return_value = True
        mock_run.return_value = Mock()

        # Execute
        result = GitStrategy.create_tag("feature/us-033-start", "Start US-033")

        # Verify
        assert result is True
        mock_run.assert_called_once_with(["git", "tag", "-a", "feature/us-033-start", "-m", "Start US-033"], check=True)

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_create_tag_fails_wrong_branch(self, mock_verify):
        """Test tag creation fails when not on roadmap branch."""
        # Setup
        mock_verify.return_value = False

        # Execute & Verify
        with pytest.raises(RuntimeError, match="Cannot create tag: not on roadmap branch"):
            GitStrategy.create_tag("feature/us-033-start", "Start US-033")

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.create_tag")
    def test_commit_with_tag(self, mock_create_tag, mock_verify, mock_run):
        """Test commit with tag creation."""
        # Setup
        mock_verify.return_value = True
        mock_run.return_value = Mock()

        # Execute
        result = GitStrategy.commit_with_tag("feat: Test commit", "feature/test-complete")

        # Verify
        assert result is True
        assert mock_run.call_count == 2  # git add . and git commit
        mock_create_tag.assert_called_once()

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_commit_with_tag_fails_wrong_branch(self, mock_verify):
        """Test commit fails when not on roadmap branch."""
        # Setup
        mock_verify.return_value = False

        # Execute & Verify
        with pytest.raises(RuntimeError, match="Cannot commit: not on roadmap branch"):
            GitStrategy.commit_with_tag("feat: Test commit")

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_list_tags(self, mock_run):
        """Test listing tags."""
        # Setup
        mock_run.return_value = Mock(stdout="feature/us-033-start\nfeature/us-033-complete\n")

        # Execute
        result = GitStrategy.list_tags("feature/*")

        # Verify
        assert result == ["feature/us-033-start", "feature/us-033-complete"]
        mock_run.assert_called_once()

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_get_latest_tag(self, mock_run):
        """Test getting latest tag."""
        # Setup
        mock_run.return_value = Mock(stdout="feature/us-033-start\nfeature/us-033-complete\n")

        # Execute
        result = GitStrategy.get_latest_tag("feature/*")

        # Verify
        assert result == "feature/us-033-complete"

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_push_with_tags(self, mock_verify, mock_run):
        """Test pushing with tags."""
        # Setup
        mock_verify.return_value = True
        mock_run.return_value = Mock()

        # Execute
        result = GitStrategy.push_with_tags()

        # Verify
        assert result is True
        assert mock_run.call_count == 2  # push branch and push tags


class TestCodeDeveloperGitOps:
    """Tests for code_developer git operations."""

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.create_tag")
    def test_start_feature(self, mock_create_tag):
        """Test starting a feature creates correct tag."""
        # Execute
        tag = CodeDeveloperGitOps.start_feature("us-033", "streamlit-app")

        # Verify
        assert tag == "feature/us-033-streamlit-app-start"
        mock_create_tag.assert_called_once_with("feature/us-033-streamlit-app-start", "Start us-033: streamlit-app")

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.create_tag")
    def test_complete_feature(self, mock_create_tag):
        """Test completing a feature creates correct tag."""
        # Execute
        tag = CodeDeveloperGitOps.complete_feature("us-033", "streamlit-app")

        # Verify
        assert tag == "feature/us-033-streamlit-app-complete"
        mock_create_tag.assert_called_once_with(
            "feature/us-033-streamlit-app-complete", "Complete us-033: streamlit-app"
        )

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.create_tag")
    def test_milestone_tag(self, mock_create_tag):
        """Test creating milestone tag."""
        # Execute
        tag = CodeDeveloperGitOps.milestone_tag("us-033", "phase-1-complete")

        # Verify
        assert tag == "feature/us-033-phase-1-complete"
        mock_create_tag.assert_called_once_with("feature/us-033-phase-1-complete", "us-033 milestone: phase-1-complete")


class TestAgentGitOps:
    """Tests for other agent git operations."""

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.commit_with_tag")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_commit_doc_update_success(self, mock_verify, mock_commit):
        """Test agent can commit doc updates."""
        # Setup
        mock_verify.return_value = True
        mock_commit.return_value = True

        # Execute
        result = AgentGitOps.commit_doc_update("project_manager", "ROADMAP.md", "Added US-034")

        # Verify
        assert result is True
        mock_commit.assert_called_once()
        args = mock_commit.call_args[0]
        assert "project_manager" in args[0]
        assert "ROADMAP.md" in args[0]

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_commit_doc_update_fails_wrong_branch(self, mock_verify):
        """Test agent commit fails on wrong branch."""
        # Setup
        mock_verify.return_value = False

        # Execute & Verify
        with pytest.raises(RuntimeError, match="must operate on roadmap branch"):
            AgentGitOps.commit_doc_update("project_manager", "ROADMAP.md", "Test")

    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.commit_with_tag")
    @patch("coffee_maker.autonomous.git_strategy.GitStrategy.verify_on_roadmap_branch")
    def test_commit_agent_work(self, mock_verify, mock_commit):
        """Test agent work commit with file tracking."""
        # Setup
        mock_verify.return_value = True
        mock_commit.return_value = True

        # Execute
        result = AgentGitOps.commit_agent_work(
            "project_manager", ["docs/ROADMAP.md", "docs/US-034-spec.md"], "Added US-034", "docs"
        )

        # Verify
        assert result is True
        mock_commit.assert_called_once()
        args = mock_commit.call_args[0]
        message = args[0]
        assert "project_manager" in message
        assert "docs/ROADMAP.md" in message
        assert "docs/US-034-spec.md" in message


class TestBranchSafetyIntegration:
    """Integration tests for branch safety."""

    def test_no_branch_switching_in_codebase(self):
        """Verify no branch switching commands in code (except in comments/strings)."""
        from pathlib import Path

        # Scan coffee_maker directory for branch switching commands
        project_root = Path(__file__).parent.parent.parent
        code_dir = project_root / "coffee_maker"

        forbidden_patterns = [
            "git checkout -b",
            "git switch ",
            "git checkout feature/",
            "create_branch(",  # Old method name
        ]

        allowed_files = [
            "git_strategy.py",  # This file documents what NOT to do
            "git_manager.py",  # Legacy file - to be deprecated (still used by daemon)
            "roadmap_cli.py",  # Contains example command in docstring
        ]

        violations = []

        for py_file in code_dir.rglob("*.py"):
            if any(allowed in str(py_file) for allowed in allowed_files):
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                if pattern in content:
                    # Check if it's in a comment or docstring
                    for line_num, line in enumerate(content.split("\n"), 1):
                        if pattern in line and not (line.strip().startswith("#") or '"""' in line or "'''" in line):
                            violations.append(f"{py_file}:{line_num}: {line.strip()}")

        assert len(violations) == 0, f"Found branch switching in code:\n" + "\n".join(violations)

    @patch("coffee_maker.autonomous.git_strategy.subprocess.run")
    def test_daemon_uses_tags(self, mock_run):
        """Verify daemon implementation uses tag-based workflow."""
        from pathlib import Path

        # Check daemon_implementation.py uses GitStrategy
        project_root = Path(__file__).parent.parent.parent
        daemon_file = project_root / "coffee_maker" / "autonomous" / "daemon_implementation.py"

        content = daemon_file.read_text()

        # Must import GitStrategy
        assert "from coffee_maker.autonomous.git_strategy import" in content

        # Must use tag operations
        assert "CodeDeveloperGitOps.start_feature" in content or "GitStrategy" in content

        # Must NOT create branches
        assert "create_branch" not in content or "# create_branch" in content  # Only in comments


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
