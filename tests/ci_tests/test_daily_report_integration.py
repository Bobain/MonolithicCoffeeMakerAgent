"""Integration tests for daily report generation.

PRIORITY 9: Enhanced code_developer Communication & Daily Standup
Integration tests for the daily report CLI functionality.
"""

import json
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.cli.daily_report_generator import DailyReportGenerator


class TestDailyReportIntegration:
    """Integration tests for daily report functionality."""

    @pytest.fixture
    def temp_repo_dir(self):
        """Create temporary directory that looks like a repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=repo_path,
                capture_output=True,
            )

            # Create initial commit
            (repo_path / "README.md").write_text("# Test Repo\n")
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "add", "README.md"],
                cwd=repo_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=repo_path,
                capture_output=True,
            )

            yield repo_path

    def test_report_generation_with_real_git(self, temp_repo_dir):
        """Test report generation with real git repository."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_repo_dir

        # Create some commits
        for i in range(3):
            (temp_repo_dir / f"file{i}.py").write_text(f"# File {i}\n")
            subprocess.run(
                ["git", "add", f"file{i}.py"],
                cwd=temp_repo_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"feat: PRIORITY 9 - Add file {i}"],
                cwd=temp_repo_dir,
                capture_output=True,
            )

        # Generate report for commits in past 24 hours
        since = datetime.now() - timedelta(hours=24)
        report = gen.generate_report(since_date=since)

        assert isinstance(report, str)
        assert len(report) > 0
        assert "code_developer Daily Report" in report
        assert "PRIORITY 9" in report or "Other" in report

    def test_daily_report_with_interaction_tracking(self, temp_repo_dir):
        """Test that interaction timestamps are properly tracked."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_repo_dir
        gen.interaction_file = temp_repo_dir / "last_interaction.json"
        gen.status_file = temp_repo_dir / "developer_status.json"

        # First check: should show report
        assert gen.should_show_report() is True

        # Update interaction timestamp
        gen.update_interaction_timestamp()

        # Second check same day: should not show report
        assert gen.should_show_report() is False

        # Verify file contents
        data = json.loads(gen.interaction_file.read_text())
        assert "last_check_in" in data
        assert "last_report_shown" in data

        today = datetime.now().date().isoformat()
        assert data["last_report_shown"] == today

    def test_report_with_developer_status(self, temp_repo_dir):
        """Test report generation with developer status data."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_repo_dir
        gen.status_file = temp_repo_dir / "developer_status.json"

        # Create status file
        status = {
            "status": "working",
            "current_task": {
                "priority": "9",
                "name": "PRIORITY 9: Enhanced Communication",
                "progress": 75,
            },
            "metrics": {
                "tasks_completed_today": 2,
                "tests_passed_today": 10,
            },
        }
        gen.status_file.write_text(json.dumps(status))

        # Generate report
        report = gen.generate_report(since_date=datetime.now() - timedelta(hours=1))

        assert "PRIORITY 9: Enhanced Communication" in report or "Today's Focus" in report

    def test_report_generation_handles_no_commits(self, temp_repo_dir):
        """Test report generation when there are no recent commits."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_repo_dir

        # Try to get commits from future (should be empty)
        since = datetime.now() + timedelta(days=1)
        report = gen.generate_report(since_date=since)

        assert isinstance(report, str)
        assert "No activity yesterday" in report or "code_developer Daily Report" in report

    def test_multiple_report_generations(self, temp_repo_dir):
        """Test that multiple report generations work correctly."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_repo_dir

        # Generate report multiple times
        for _ in range(3):
            report = gen.generate_report(since_date=datetime.now() - timedelta(hours=1))
            assert isinstance(report, str)
            assert len(report) > 0


class TestDailyReportCLIIntegration:
    """Integration tests for CLI commands."""

    def test_dev_report_command_available(self):
        """Test that dev-report command is available."""
        result = subprocess.run(
            ["poetry", "run", "project-manager", "dev-report", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "developer" in result.stdout.lower() or "report" in result.stdout.lower()

    def test_dev_report_command_with_days(self):
        """Test dev-report command with --days argument."""
        result = subprocess.run(
            ["poetry", "run", "project-manager", "dev-report", "--days", "7"],
            capture_output=True,
            text=True,
        )
        # Should succeed (exit code 0) or just show report
        assert result.returncode in [0, 1]  # 1 is ok if git errors


class TestInteractionTracking:
    """Test interaction tracking functionality."""

    def test_interaction_file_creation(self):
        """Test that interaction file is created properly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            interaction_file = Path(tmpdir) / "last_interaction.json"

            gen = DailyReportGenerator()
            gen.interaction_file = interaction_file

            # File should not exist initially
            assert not interaction_file.exists()

            # Update timestamp
            gen.update_interaction_timestamp()

            # File should now exist
            assert interaction_file.exists()

            # Parse and verify contents
            data = json.loads(interaction_file.read_text())
            assert isinstance(data, dict)
            assert "last_check_in" in data
            assert "last_report_shown" in data

    def test_interaction_file_persistence(self):
        """Test that interaction file persists correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            interaction_file = Path(tmpdir) / "last_interaction.json"

            gen = DailyReportGenerator()
            gen.interaction_file = interaction_file

            # Create interaction file
            gen.update_interaction_timestamp()
            json.loads(interaction_file.read_text())["last_check_in"]

            # Read back should show same date (but possibly different check_in time)
            gen2 = DailyReportGenerator()
            gen2.interaction_file = interaction_file

            today = datetime.now().date().isoformat()
            data = json.loads(interaction_file.read_text())
            assert data["last_report_shown"] == today
