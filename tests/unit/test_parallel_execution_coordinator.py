"""Tests for ParallelExecutionCoordinator."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coffee_maker.orchestrator.parallel_execution_coordinator import (
    ParallelExecutionCoordinator,
    ResourceMonitor,
    WorktreeConfig,
)


class TestResourceMonitor:
    """Tests for ResourceMonitor."""

    def test_resource_monitor_initialization(self):
        """Test ResourceMonitor initialization."""
        monitor = ResourceMonitor(max_cpu_percent=75.0, max_memory_percent=85.0)
        assert monitor.max_cpu_percent == 75.0
        assert monitor.max_memory_percent == 85.0

    def test_check_resources_available_success(self):
        """Test resource check when resources are available."""
        monitor = ResourceMonitor(max_cpu_percent=99.0, max_memory_percent=99.0)
        available, reason = monitor.check_resources_available()
        # Should always pass with 99% thresholds
        assert available is True
        assert "available" in reason.lower()

    def test_get_resource_status(self):
        """Test getting resource status."""
        monitor = ResourceMonitor()
        status = monitor.get_resource_status()

        assert "cpu_percent" in status
        assert "memory_percent" in status
        assert "memory_available_gb" in status
        assert "disk_percent" in status
        assert "disk_free_gb" in status

        assert isinstance(status["cpu_percent"], float)
        assert isinstance(status["memory_percent"], float)
        assert status["cpu_percent"] >= 0
        assert status["memory_percent"] >= 0


class TestWorktreeConfig:
    """Tests for WorktreeConfig dataclass."""

    def test_worktree_config_creation(self):
        """Test creating WorktreeConfig."""
        config = WorktreeConfig(priority_id=20, worktree_path=Path("/tmp/test-wt1"), branch_name="feature/us-020")

        assert config.priority_id == 20
        assert config.worktree_path == Path("/tmp/test-wt1")
        assert config.branch_name == "feature/us-020"
        assert config.status == "pending"
        assert config.process is None
        assert config.start_time is None
        assert config.end_time is None


class TestParallelExecutionCoordinator:
    """Tests for ParallelExecutionCoordinator."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            repo_path.mkdir()

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True, capture_output=True
            )

            # Create initial commit
            (repo_path / "README.md").write_text("# Test Repo")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

            # Create roadmap branch
            subprocess.run(["git", "checkout", "-b", "roadmap"], cwd=repo_path, check=True, capture_output=True)

            yield repo_path

    def test_coordinator_initialization(self, temp_git_repo):
        """Test coordinator initialization."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo, max_instances=2)

        assert coordinator.repo_root == temp_git_repo
        assert coordinator.max_instances == 2
        assert coordinator.auto_merge is True
        assert isinstance(coordinator.resource_monitor, ResourceMonitor)
        assert len(coordinator.worktrees) == 0

    def test_coordinator_initialization_no_git_repo(self):
        """Test coordinator initialization with non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a git repository"):
                ParallelExecutionCoordinator(repo_root=Path(tmpdir))

    def test_coordinator_max_instances_limit(self, temp_git_repo):
        """Test coordinator enforces max 3 instances."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo, max_instances=10)
        assert coordinator.max_instances == 3  # Should be clamped to 3

    def test_select_parallel_priorities_basic(self, temp_git_repo):
        """Test selecting parallel priorities."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        # Mock independent pairs
        independent_pairs = [(20, 21), (20, 22), (21, 22)]
        priority_ids = [20, 21, 22]

        selected = coordinator._select_parallel_priorities(priority_ids, independent_pairs, max_count=3)

        # All three should be selected since they're all independent
        assert len(selected) == 3
        assert set(selected) == {20, 21, 22}

    def test_select_parallel_priorities_with_conflicts(self, temp_git_repo):
        """Test selecting priorities when there are conflicts."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        # Mock independent pairs (20-21 conflict, 20-22 independent, 21-22 independent)
        independent_pairs = [(20, 22), (21, 22)]
        priority_ids = [20, 21, 22]

        selected = coordinator._select_parallel_priorities(priority_ids, independent_pairs, max_count=3)

        # Should select 20 first, then 22 (independent of 20), but NOT 21 (conflicts with 20)
        assert len(selected) >= 1
        assert 20 in selected  # First priority always selected

    def test_select_parallel_priorities_max_count(self, temp_git_repo):
        """Test selecting priorities respects max_count."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        # All independent
        independent_pairs = [(20, 21), (20, 22), (20, 23), (21, 22), (21, 23), (22, 23)]
        priority_ids = [20, 21, 22, 23]

        selected = coordinator._select_parallel_priorities(priority_ids, independent_pairs, max_count=2)

        # Should select only 2
        assert len(selected) == 2

    def test_validate_task_separation_success(self, temp_git_repo):
        """Test task separation validation success."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        # Create skill file with real implementation
        skill_path = temp_git_repo / ".claude" / "skills" / "architect" / "task-separator"
        skill_path.mkdir(parents=True, exist_ok=True)

        # Write a simple mock skill that returns expected results
        skill_code = """
def main(context):
    return {
        "independent_pairs": [(20, 21), (20, 22)],
        "conflicts": {},
        "task_file_map": {
            20: ["coffee_maker/skills/analyzer.py"],
            21: ["coffee_maker/cli/dashboard.py"],
            22: ["coffee_maker/orchestrator/coordinator.py"]
        }
    }
"""
        (skill_path / "task-separator.py").write_text(skill_code)

        result = coordinator._validate_task_separation([20, 21, 22])

        assert result["valid"] is True
        assert len(result["independent_pairs"]) == 2
        assert (20, 21) in result["independent_pairs"]

    def test_validate_task_separation_no_skill(self, temp_git_repo):
        """Test task separation validation when skill is missing."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        result = coordinator._validate_task_separation([20, 21, 22])

        assert result["valid"] is False
        assert "not found" in result["reason"].lower()

    def test_get_status(self, temp_git_repo):
        """Test getting coordinator status."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo, max_instances=2)

        status = coordinator.get_status()

        assert status["max_instances"] == 2
        assert status["active_worktrees"] == 0
        assert "worktrees" in status
        assert "resources" in status
        assert isinstance(status["worktrees"], list)

    def test_remove_worktree_with_force(self, temp_git_repo):
        """Test removing a worktree."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        # Create a worktree manually
        worktree_path = temp_git_repo.parent / "test-wt1"
        subprocess.run(
            ["git", "worktree", "add", "-b", "test-branch", str(worktree_path), "roadmap"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        assert worktree_path.exists()

        # Remove it
        coordinator._remove_worktree(worktree_path)

        # Should be gone
        assert not worktree_path.exists()

    def test_create_worktrees_success(self, temp_git_repo):
        """Test creating worktrees."""
        coordinator = ParallelExecutionCoordinator(repo_root=temp_git_repo)

        worktrees = coordinator._create_worktrees([20, 21])

        assert len(worktrees) == 2
        assert worktrees[0].priority_id == 20
        assert worktrees[1].priority_id == 21
        assert worktrees[0].branch_name == "feature/us-020"
        assert worktrees[1].branch_name == "feature/us-021"
        assert worktrees[0].status == "created"
        assert worktrees[1].status == "created"

        # Cleanup
        for worktree in worktrees:
            coordinator._remove_worktree(worktree.worktree_path)
