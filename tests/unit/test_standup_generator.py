"""Unit tests for StandupGenerator.

Tests cover:
- Daily standup generation
- Activity formatting for prompts
- Fallback summary generation
- Empty day handling
- Metrics calculation
"""

import pytest
import tempfile
import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from coffee_maker.autonomous.activity_db import (
    ActivityDB,
    ACTIVITY_TYPE_COMMIT,
    ACTIVITY_TYPE_TEST_RUN,
    ACTIVITY_TYPE_PR_CREATED,
    OUTCOME_SUCCESS,
)


@pytest.fixture
def mock_config():
    """Mock ConfigManager for tests."""
    with patch("coffee_maker.autonomous.standup_generator.ConfigManager") as mock_class:
        mock_instance = MagicMock()
        mock_instance.get_anthropic_api_key.return_value = "test-api-key"
        mock_class.return_value = mock_instance
        yield mock_class


@pytest.fixture
def temp_db_with_activities():
    """Create a temporary test database with sample activities."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_activity.db")
        db = ActivityDB(db_path=db_path)

        # Log sample activities
        db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Implement user authentication",
            priority_number="2.5",
            priority_name="CI Testing",
            metadata={"files_changed": 5, "lines_added": 120, "lines_removed": 30},
        )

        db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Add database migration",
            priority_number="2.5",
            priority_name="CI Testing",
            metadata={"files_changed": 2, "lines_added": 45},
        )

        db.log_activity(
            activity_type=ACTIVITY_TYPE_TEST_RUN,
            title="Tests: 47 passed, 0 failed",
            priority_number="2.5",
            priority_name="CI Testing",
            metadata={
                "passed": 47,
                "failed": 0,
                "skipped": 2,
                "duration_seconds": 12.5,
            },
            outcome=OUTCOME_SUCCESS,
        )

        db.log_activity(
            activity_type=ACTIVITY_TYPE_PR_CREATED,
            title="Created PR #42: Add CI testing",
            priority_number="2.5",
            priority_name="CI Testing",
            metadata={
                "pr_number": 42,
                "pr_url": "https://github.com/org/repo/pull/42",
                "branch": "feature/ci-testing",
            },
        )

        yield db


@pytest.fixture
def temp_db_empty():
    """Create a temporary test database with no activities."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_activity.db")
        yield ActivityDB(db_path=db_path)


class TestStandupGenerator:
    """Tests for StandupGenerator class."""

    def test_format_activities_for_prompt(self, temp_db_with_activities, mock_config):
        """Test formatting activities for Claude prompt."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_with_activities)

            activities = temp_db_with_activities.get_activities(limit=100)
            formatted = gen._format_activities_for_prompt(activities)

            # Should be valid JSON
            data = json.loads(formatted)
            assert len(data) >= 4  # We logged 4 activities

            # Check structure
            for item in data:
                assert "type" in item
                assert "title" in item
                assert "priority" in item
                assert "outcome" in item

    def test_generate_empty_summary(self, temp_db_empty, mock_config):
        """Test generating summary for a day with no activities."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_empty)

            today = date.today()
            summary = gen._generate_empty_summary(today)

            assert summary.date == today.isoformat()
            assert summary.metrics["total_activities"] == 0
            assert len(summary.activities) == 0
            assert "No development activities" in summary.summary_text

    def test_get_daily_standup_empty_day(self, temp_db_empty, mock_config):
        """Test generating daily standup for empty day."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_empty)

            today = date.today()
            summary = gen.generate_daily_standup(today)

            assert summary.date == today.isoformat()
            assert summary.metrics["total_activities"] == 0
            assert "No development activities" in summary.summary_text

    def test_generate_fallback_summary(self, temp_db_with_activities, mock_config):
        """Test fallback summary generation."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_with_activities)

            today = date.today()
            activities = temp_db_with_activities.get_activities(limit=100)
            metrics = temp_db_with_activities.get_daily_metrics(today)

            fallback = gen._generate_fallback_summary(today, activities, metrics)

            # Should contain key sections
            assert "Daily Standup" in fallback
            assert "Metrics" in fallback
            assert "Accomplishments" in fallback

            # Should not contain Claude-specific markers
            assert "[Placeholder]" not in fallback

    def test_summarize_activities_basic(self, temp_db_with_activities, mock_config):
        """Test basic activity summarization."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_with_activities)

            activities = temp_db_with_activities.get_activities(limit=100)
            summary = gen._summarize_activities_basic(activities)

            # Should mention priorities
            assert "2.5" in summary or "CI Testing" in summary
            # Should show activity counts
            assert "activities" in summary

    def test_summarize_activities_empty(self, temp_db_empty, mock_config):
        """Test summarizing empty activities."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic"):
            gen = StandupGenerator(db=temp_db_empty)

            summary = gen._summarize_activities_basic([])

            assert "No activities" in summary

    def test_generate_daily_standup_with_claude(self, temp_db_with_activities, mock_config):
        """Test daily standup generation with mocked Claude API."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        # Setup mock
        with patch("coffee_maker.autonomous.standup_generator.Anthropic") as mock_anthropic_class:
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="🤖 Test standup report")]
            mock_client.messages.create.return_value = mock_response

            gen = StandupGenerator(db=temp_db_with_activities)

            today = date.today()
            summary = gen.generate_daily_standup(today)

            # Should have called Claude API
            assert mock_client.messages.create.called

            # Should have generated summary
            assert summary.summary_text == "🤖 Test standup report"
            assert summary.date == today.isoformat()
            assert summary.metrics["commits"] >= 2

    def test_generate_daily_standup_claude_failure(self, temp_db_with_activities, mock_config):
        """Test fallback when Claude API fails."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic") as mock_anthropic_class:
            # Setup mock to raise exception
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client
            mock_client.messages.create.side_effect = Exception("API Error")

            gen = StandupGenerator(db=temp_db_with_activities)

            today = date.today()
            summary = gen.generate_daily_standup(today)

            # Should have fallen back to basic summary
            assert "Daily Standup" in summary.summary_text
            assert "AI summary unavailable" in summary.summary_text

    def test_daily_summary_structure(self, temp_db_with_activities, mock_config):
        """Test the structure of generated daily summary."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic") as mock_anthropic_class:
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test report")]
            mock_client.messages.create.return_value = mock_response

            gen = StandupGenerator(db=temp_db_with_activities)

            today = date.today()
            summary = gen.generate_daily_standup(today)

            # Check all required fields
            assert summary.date == today.isoformat()
            assert summary.summary_text == "Test report"
            assert isinstance(summary.metrics, dict)
            assert len(summary.activities) > 0
            assert summary.generated_at is not None

            # Check metrics structure
            assert "commits" in summary.metrics
            assert "test_runs" in summary.metrics
            assert "prs_created" in summary.metrics
            assert "successes" in summary.metrics

    def test_metrics_accuracy(self, temp_db_with_activities, mock_config):
        """Test that metrics accurately reflect activities."""
        from coffee_maker.autonomous.standup_generator import StandupGenerator

        with patch("coffee_maker.autonomous.standup_generator.Anthropic") as mock_anthropic_class:
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test")]
            mock_client.messages.create.return_value = mock_response

            gen = StandupGenerator(db=temp_db_with_activities)

            today = date.today()
            summary = gen.generate_daily_standup(today)

            # We logged 2 commits, 1 test run, 1 PR
            assert summary.metrics["commits"] == 2
            assert summary.metrics["test_runs"] == 1
            assert summary.metrics["prs_created"] == 1
            assert summary.metrics["total_activities"] == 4
