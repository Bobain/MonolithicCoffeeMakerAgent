"""Unit tests for DailyReportGenerator.

PRIORITY 9: Enhanced code_developer Communication & Daily Standup
Tests for daily report generation from existing data sources.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from coffee_maker.cli.daily_report_generator import DailyReportGenerator


class TestDailyReportGenerator:
    """Test suite for DailyReportGenerator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def generator(self, temp_dir):
        """Create DailyReportGenerator with temporary paths."""
        gen = DailyReportGenerator()
        gen.repo_root = temp_dir
        gen.status_file = temp_dir / "developer_status.json"
        gen.notifications_db = temp_dir / "notifications.db"
        gen._init_system_state_table()  # Initialize database table
        return gen

    def test_should_show_report_first_time(self, generator):
        """Test that report is shown first time (no interaction file)."""
        assert generator.should_show_report() is True

    def test_should_show_report_new_day(self, generator):
        """Test that report is shown on new day."""
        # Set last report to yesterday in database
        import sqlite3

        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        conn = sqlite3.connect(generator.notifications_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)",
            ("last_report_shown", yesterday, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        assert generator.should_show_report() is True

    def test_should_not_show_report_same_day(self, generator):
        """Test that report is not shown same day."""
        import sqlite3

        today = datetime.now().date().isoformat()
        conn = sqlite3.connect(generator.notifications_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)",
            ("last_report_shown", today, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        assert generator.should_show_report() is False

    def test_update_interaction_timestamp(self, generator):
        """Test updating interaction timestamp in database."""
        import sqlite3

        generator.update_interaction_timestamp()

        # Verify data in database
        conn = sqlite3.connect(generator.notifications_db)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM system_state WHERE key = ?", ("last_report_shown",))
        result = cursor.fetchone()
        assert result is not None
        last_report_shown = result[0]

        cursor.execute("SELECT value FROM system_state WHERE key = ?", ("last_check_in",))
        result = cursor.fetchone()
        assert result is not None

        conn.close()

        # Verify date is today
        today = datetime.now().date().isoformat()
        assert last_report_shown == today

    def test_collect_git_commits_empty(self, generator):
        """Test collecting commits with no repository."""
        # Should return empty list when git command fails
        commits = generator._collect_git_commits(datetime.now())
        assert isinstance(commits, list)

    def test_group_commits_by_priority(self, generator):
        """Test grouping commits by priority."""
        commits = [
            {
                "hash": "abc123",
                "author": "code_developer",
                "date": "2025-10-15",
                "message": "feat: PRIORITY 9 - Add daily report",
                "files_changed": 2,
                "lines_added": 50,
                "lines_removed": 10,
            },
            {
                "hash": "def456",
                "author": "code_developer",
                "date": "2025-10-15",
                "message": "fix: bug in PRIORITY 8",
                "files_changed": 1,
                "lines_added": 20,
                "lines_removed": 5,
            },
            {
                "hash": "ghi789",
                "author": "code_developer",
                "date": "2025-10-15",
                "message": "docs: Update README",
                "files_changed": 1,
                "lines_added": 10,
                "lines_removed": 0,
            },
        ]

        grouped = generator._group_commits_by_priority(commits)

        assert "PRIORITY 9" in grouped
        assert "PRIORITY 8" in grouped
        assert "Other" in grouped

        assert len(grouped["PRIORITY 9"]) == 1
        assert len(grouped["PRIORITY 8"]) == 1
        assert len(grouped["Other"]) == 1

    def test_calculate_stats(self, generator):
        """Test calculating statistics from commits."""
        commits = [
            {
                "files_changed": 2,
                "lines_added": 50,
                "lines_removed": 10,
            },
            {
                "files_changed": 1,
                "lines_added": 20,
                "lines_removed": 5,
            },
            {
                "files_changed": 3,
                "lines_added": 100,
                "lines_removed": 30,
            },
        ]

        stats = generator._calculate_stats(commits)

        assert stats["total_commits"] == 3
        assert stats["files_changed"] == 6
        assert stats["lines_added"] == 170
        assert stats["lines_removed"] == 45

    def test_calculate_stats_empty(self, generator):
        """Test calculating stats with no commits."""
        stats = generator._calculate_stats([])

        assert stats["total_commits"] == 0
        assert stats["files_changed"] == 0
        assert stats["lines_added"] == 0
        assert stats["lines_removed"] == 0

    def test_load_developer_status(self, generator):
        """Test loading developer status from JSON."""
        status_data = {
            "status": "working",
            "current_task": {
                "priority": "9",
                "name": "PRIORITY 9",
                "progress": 50,
            },
        }
        generator.status_file.parent.mkdir(parents=True, exist_ok=True)
        generator.status_file.write_text(json.dumps(status_data))

        loaded = generator._load_developer_status()

        assert loaded["status"] == "working"
        assert loaded["current_task"]["priority"] == "9"

    def test_load_developer_status_missing(self, generator):
        """Test loading status when file doesn't exist."""
        loaded = generator._load_developer_status()
        assert loaded == {}

    def test_load_developer_status_corrupted(self, generator):
        """Test loading status with corrupted JSON."""
        generator.status_file.parent.mkdir(parents=True, exist_ok=True)
        generator.status_file.write_text("invalid json {")

        loaded = generator._load_developer_status()
        assert loaded == {}

    def test_collect_blockers_empty(self, generator):
        """Test collecting blockers (MVP returns empty)."""
        blockers = generator._collect_blockers()
        assert blockers == []

    def test_format_as_markdown_no_activity(self, generator):
        """Test markdown formatting with no activity."""
        report = generator._format_as_markdown(
            since_date=datetime.now(),
            commits={},
            stats={
                "total_commits": 0,
                "files_changed": 0,
                "lines_added": 0,
                "lines_removed": 0,
            },
            status_data={},
            blockers=[],
        )

        assert "No activity yesterday" in report
        assert "📊" in report
        assert "🤖" in report

    def test_format_as_markdown_with_commits(self, generator):
        """Test markdown formatting with commits."""
        commits = {
            "PRIORITY 9": [
                {
                    "hash": "abc123",
                    "author": "code_developer",
                    "date": "2025-10-15",
                    "message": "feat: Add daily report",
                    "files_changed": 2,
                    "lines_added": 50,
                    "lines_removed": 10,
                }
            ]
        }

        report = generator._format_as_markdown(
            since_date=datetime.now(),
            commits=commits,
            stats={
                "total_commits": 1,
                "files_changed": 2,
                "lines_added": 50,
                "lines_removed": 10,
            },
            status_data={},
            blockers=[],
        )

        assert "PRIORITY 9" in report
        assert "feat: Add daily report" in report
        assert "Total Commits" in report and "1" in report
        assert "Files Modified" in report and "2" in report
        assert "+50" in report
        assert "-10" in report

    def test_format_as_markdown_with_current_task(self, generator):
        """Test markdown formatting with current task."""
        status_data = {
            "current_task": {
                "name": "PRIORITY 9: Enhanced Communication",
                "progress": 75,
            }
        }

        report = generator._format_as_markdown(
            since_date=datetime.now(),
            commits={},
            stats={
                "total_commits": 0,
                "files_changed": 0,
                "lines_added": 0,
                "lines_removed": 0,
            },
            status_data=status_data,
            blockers=[],
        )

        assert "Today's Focus" in report
        assert "PRIORITY 9: Enhanced Communication" in report
        assert "75%" in report

    def test_generate_report_complete(self, generator):
        """Test complete report generation."""
        # Create status file
        status_data = {
            "current_task": {
                "name": "PRIORITY 9",
                "progress": 50,
            }
        }
        generator.status_file.parent.mkdir(parents=True, exist_ok=True)
        generator.status_file.write_text(json.dumps(status_data))

        # Generate report
        report = generator.generate_report(since_date=datetime.now() - timedelta(hours=1))

        # Verify report structure
        assert isinstance(report, str)
        assert "code_developer Daily Report" in report
        assert "📊" in report or "Overall Stats" in report

    def test_generate_report_with_dates(self, generator):
        """Test report generation with specific dates."""
        since = datetime.now() - timedelta(days=2)
        until = datetime.now() - timedelta(days=1)

        report = generator.generate_report(since_date=since, until_date=until)

        assert isinstance(report, str)
        assert len(report) > 0


class TestDailyReportModule:
    """Test module-level functions."""

    def test_should_show_report_function(self):
        """Test module-level should_show_report function."""
        from coffee_maker.cli.daily_report_generator import should_show_report

        # Function should exist and return boolean
        result = should_show_report()
        assert isinstance(result, bool)

    def test_show_daily_report_function(self):
        """Test module-level show_daily_report function."""
        from coffee_maker.cli.daily_report_generator import show_daily_report

        # Function should not raise exception
        # (It will show report to console, which is fine for testing)
        try:
            # Mock the console output to avoid actual printing
            with patch("coffee_maker.cli.daily_report_generator.console"):
                show_daily_report()
        except Exception as e:
            pytest.fail(f"show_daily_report raised exception: {e}")
