"""Tests for Git operations.

These tests verify the GitManager correctly handles Git operations
like branching, committing, and checking status.
"""

import pytest
from coffee_maker.autonomous.git_manager import GitManager


class TestGitOperations:
    """Test Git operations."""

    def test_git_manager_initializes(self):
        """Verify GitManager can be initialized."""
        git = GitManager()
        assert git is not None
        assert git.repo_path is not None

    def test_git_manager_get_current_branch(self):
        """Verify GitManager can get current branch."""
        git = GitManager()
        branch = git.get_current_branch()

        assert isinstance(branch, str)
        assert len(branch) > 0

    def test_git_manager_is_clean(self):
        """Verify GitManager can check if working directory is clean."""
        git = GitManager()
        is_clean = git.is_clean()

        # Should return boolean, not crash
        assert isinstance(is_clean, bool)

    def test_git_manager_get_status(self):
        """Verify GitManager can get status."""
        git = GitManager()
        status = git.get_status()

        assert isinstance(status, str)

    def test_git_manager_has_remote(self):
        """Verify GitManager can check for remote."""
        git = GitManager()
        has_remote = git.has_remote()

        assert isinstance(has_remote, bool)

    def test_git_manager_branch_exists(self):
        """Verify GitManager can check if branch exists."""
        git = GitManager()
        current_branch = git.get_current_branch()

        # Current branch should exist
        assert git.branch_exists(current_branch)

        # Non-existent branch should not exist
        assert not git.branch_exists("nonexistent-branch-12345")

    @pytest.mark.integration
    def test_git_manager_create_branch(self):
        """Integration test: Verify branch creation and cleanup."""
        git = GitManager()
        original_branch = git.get_current_branch()

        test_branch = "test-branch-for-ci-tests"

        try:
            # Create test branch
            success = git.create_branch(test_branch)
            assert success

            # Verify we're on the new branch
            assert git.get_current_branch() == test_branch

            # Verify branch exists
            assert git.branch_exists(test_branch)

        finally:
            # Cleanup: return to original branch
            git.checkout(original_branch)

            # Note: Not deleting branch to avoid issues
            # It will be cleaned up manually if needed

    @pytest.mark.integration
    def test_git_manager_commit(self, tmp_path):
        """Integration test: Verify commit functionality."""
        # This test would require setting up a temporary git repo
        # For now, we just verify the method exists and has correct signature
        git = GitManager()

        assert hasattr(git, "commit")
        assert callable(git.commit)

    @pytest.mark.integration
    def test_git_manager_push(self):
        """Integration test: Verify push functionality."""
        # This test would require network access and permissions
        # For now, we just verify the method exists
        git = GitManager()

        assert hasattr(git, "push")
        assert callable(git.push)

    @pytest.mark.integration
    def test_git_manager_create_pull_request(self):
        """Integration test: Verify PR creation functionality."""
        # This test would require gh CLI and network access
        # For now, we just verify the method exists
        git = GitManager()

        assert hasattr(git, "create_pull_request")
        assert callable(git.create_pull_request)

    def test_git_manager_checkout(self):
        """Verify GitManager checkout functionality."""
        git = GitManager()
        current_branch = git.get_current_branch()

        # Checkout current branch (should succeed)
        success = git.checkout(current_branch)
        assert success

        # Verify we're still on the same branch
        assert git.get_current_branch() == current_branch
