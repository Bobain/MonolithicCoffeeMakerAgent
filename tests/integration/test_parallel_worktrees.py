"""Integration tests for parallel execution with worktrees."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator


@pytest.fixture
def test_git_repo():
    """Create a test git repository with proper structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-coffee-maker"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True, capture_output=True)

        # Create basic structure
        (repo_path / "coffee_maker").mkdir()
        (repo_path / "coffee_maker" / "__init__.py").write_text("")
        (repo_path / "tests").mkdir()
        (repo_path / "tests" / "__init__.py").write_text("")

        # Create docs structure
        (repo_path / "docs").mkdir()
        (repo_path / "docs" / "architecture").mkdir()
        (repo_path / "docs" / "architecture" / "specs").mkdir()

        # Create task-separator skill
        skill_path = repo_path / ".claude" / "skills" / "architect" / "task-separator"
        skill_path.mkdir(parents=True, exist_ok=True)

        # Write a simple skill that returns test results
        skill_code = '''
def main(context):
    """Mock task separator for testing."""
    priority_ids = context.get("priority_ids", [])

    # Mock file map
    task_file_map = {}
    for pid in priority_ids:
        task_file_map[pid] = [f"coffee_maker/module_{pid}.py"]

    # All tasks are independent (different files)
    independent_pairs = []
    for i, p1 in enumerate(priority_ids):
        for p2 in priority_ids[i + 1:]:
            independent_pairs.append((p1, p2))

    return {
        "independent_pairs": independent_pairs,
        "conflicts": {},
        "task_file_map": task_file_map
    }
'''
        (skill_path / "task_separator.py").write_text(skill_code)

        # Create initial commit
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

        # Create roadmap branch
        subprocess.run(["git", "checkout", "-b", "roadmap"], cwd=repo_path, check=True, capture_output=True)

        yield repo_path


class TestParallelWorktreeIntegration:
    """Integration tests for parallel worktree execution."""

    def test_create_and_cleanup_worktrees(self, test_git_repo):
        """Test creating and cleaning up worktrees."""
        coordinator = ParallelExecutionCoordinator(repo_root=test_git_repo, max_instances=2)

        # Create worktrees
        worktrees = coordinator._create_worktrees([100, 101])

        assert len(worktrees) == 2
        assert all(wt.worktree_path.exists() for wt in worktrees)
        assert all(wt.status == "created" for wt in worktrees)

        # Check branches were created
        result = subprocess.run(
            ["git", "branch", "--list"], cwd=test_git_repo, check=True, capture_output=True, text=True
        )
        assert "feature/us-100" in result.stdout
        assert "feature/us-101" in result.stdout

        # Cleanup
        coordinator._cleanup_worktrees(worktrees)

        # Verify cleanup
        assert all(not wt.worktree_path.exists() for wt in worktrees)

    def test_task_validation_integration(self, test_git_repo):
        """Test task validation with real skill."""
        coordinator = ParallelExecutionCoordinator(repo_root=test_git_repo)

        # Validate tasks
        result = coordinator._validate_task_separation([100, 101, 102])

        assert result["valid"] is True
        assert "independent_pairs" in result
        assert len(result["independent_pairs"]) > 0
        assert "task_file_map" in result

    def test_select_parallel_priorities_integration(self, test_git_repo):
        """Test selecting parallel priorities end-to-end."""
        coordinator = ParallelExecutionCoordinator(repo_root=test_git_repo, max_instances=2)

        # Validate tasks
        validation = coordinator._validate_task_separation([100, 101, 102])
        assert validation["valid"] is True

        # Select priorities
        selected = coordinator._select_parallel_priorities(
            [100, 101, 102], validation["independent_pairs"], max_count=2
        )

        # Should select 2 priorities
        assert len(selected) == 2
        assert all(pid in [100, 101, 102] for pid in selected)

    def test_worktree_isolation(self, test_git_repo):
        """Test that worktrees are properly isolated."""
        coordinator = ParallelExecutionCoordinator(repo_root=test_git_repo)

        # Create worktrees
        worktrees = coordinator._create_worktrees([100, 101])

        try:
            # Create different files in each worktree
            (worktrees[0].worktree_path / "file1.txt").write_text("worktree 1")
            (worktrees[1].worktree_path / "file2.txt").write_text("worktree 2")

            # Verify files exist in their respective worktrees
            assert (worktrees[0].worktree_path / "file1.txt").exists()
            assert (worktrees[1].worktree_path / "file2.txt").exists()

            # Verify files DON'T exist in other worktrees
            assert not (worktrees[0].worktree_path / "file2.txt").exists()
            assert not (worktrees[1].worktree_path / "file1.txt").exists()
            assert not (test_git_repo / "file1.txt").exists()
            assert not (test_git_repo / "file2.txt").exists()

        finally:
            coordinator._cleanup_worktrees(worktrees)

    def test_get_status_integration(self, test_git_repo):
        """Test getting status with active worktrees."""
        coordinator = ParallelExecutionCoordinator(repo_root=test_git_repo, max_instances=3)

        # Initial status
        status = coordinator.get_status()
        assert status["max_instances"] == 3
        assert status["active_worktrees"] == 0
        assert len(status["worktrees"]) == 0

        # Create worktrees
        worktrees = coordinator._create_worktrees([100, 101])
        coordinator.worktrees = worktrees

        # Status with worktrees
        status = coordinator.get_status()
        assert len(status["worktrees"]) == 2
        assert all("priority_id" in wt for wt in status["worktrees"])
        assert all("branch" in wt for wt in status["worktrees"])
        assert all("worktree_path" in wt for wt in status["worktrees"])

        # Cleanup
        coordinator._cleanup_worktrees(worktrees)
