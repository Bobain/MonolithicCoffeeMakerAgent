"""Integration tests for /summary and /calendar CLI commands.

US-017 Phase 2: CLI Integration

Tests cover:
- cmd_summary command functionality
- cmd_calendar command functionality
- Flag parsing and validation (--days, --limit, --format)
- Error handling (invalid parameters, missing ROADMAP)
- Output formatting (markdown vs text)
- Integration with StatusReportGenerator
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from argparse import Namespace

from coffee_maker.cli.roadmap_cli import cmd_summary, cmd_calendar
from coffee_maker.reports.status_report_generator import StoryCompletion, UpcomingStory


# ==================== FIXTURES ====================


@pytest.fixture
def sample_roadmap_file():
    """Create temporary ROADMAP.md file for integration testing."""
    content = """# Coffee Maker Agent - ROADMAP

### 🎯 [US-016] Technical Spec Generation

**Status**: ✅ COMPLETE (2025-10-15)
**Business Value**: Accurate delivery estimates
**Estimated Effort**: 4-5 days
**Actual Effort**: 3.75 days

**Key Features**:
- AI-assisted task breakdown
- Historical metrics integration
- Interactive approval workflow

---

### 🎯 [US-015] Estimation Metrics Tracking

**Status**: 🔄 In Progress
**Estimated Effort**: 3-4 days

---

### 🎯 [US-017] Summary & Calendar

**Status**: 📝 Planned
**Estimated Effort**: 5-7 days
**I want**: proactive delivery summaries and calendar
**So that**: users have better visibility

---
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def mock_completions():
    """Mock list of StoryCompletion objects."""
    return [
        StoryCompletion(
            story_id="US-016",
            title="Technical Spec Generation",
            completion_date=datetime(2025, 10, 15),
            business_value="Accurate delivery estimates",
            key_features=["AI-assisted task breakdown", "Historical metrics integration"],
            estimated_days=4.5,
            actual_days=3.75,
        ),
        StoryCompletion(
            story_id="US-014",
            title="Velocity Tracking",
            completion_date=datetime(2025, 10, 10),
            business_value="Data-driven planning",
            key_features=["Velocity calculation", "Metrics dashboard"],
            estimated_days=3.0,
            actual_days=2.5,
        ),
    ]


@pytest.fixture
def mock_upcoming():
    """Mock list of UpcomingStory objects."""
    return [
        UpcomingStory(
            story_id="US-017",
            title="Summary & Calendar",
            estimated_min_days=5.0,
            estimated_max_days=7.0,
            estimated_completion_date=datetime(2025, 10, 27),
            what_description="Proactive delivery summaries",
            impact_statement="Better visibility",
        ),
        UpcomingStory(
            story_id="US-018",
            title="Notification System",
            estimated_min_days=2.0,
            estimated_max_days=3.0,
            estimated_completion_date=datetime(2025, 10, 25),
            what_description="Real-time notifications",
            impact_statement="Faster feedback",
        ),
    ]


# ==================== CMD_SUMMARY TESTS ====================


def test_cmd_summary_default_parameters(sample_roadmap_file, mock_completions, capsys):
    """Test cmd_summary with default parameters (14 days, markdown format)."""
    args = Namespace(days=14, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=mock_completions,
        ):
            result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 0
    assert "US-016" in captured.out
    assert "Technical Spec Generation" in captured.out
    assert "Accurate delivery estimates" in captured.out
    assert "AI-assisted task breakdown" in captured.out


def test_cmd_summary_custom_days(sample_roadmap_file, mock_completions, capsys):
    """Test cmd_summary with custom --days parameter."""
    args = Namespace(days=7, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=mock_completions,
        ) as mock_get_completions:
            result = cmd_summary(args)

            # Verify get_recent_completions called with correct days parameter
            mock_get_completions.assert_called_once_with(days=7)

    capsys.readouterr()
    assert result == 0


def test_cmd_summary_text_format(sample_roadmap_file, mock_completions, capsys):
    """Test cmd_summary with text format (removes markdown formatting)."""
    args = Namespace(days=14, format="text")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=mock_completions,
        ):
            result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 0
    # Text format should have fewer markdown symbols
    assert "US-016" in captured.out
    assert "**" not in captured.out or captured.out.count("**") < 10


def test_cmd_summary_no_completions(sample_roadmap_file, capsys):
    """Test cmd_summary when no completions found."""
    args = Namespace(days=14, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=[],
        ):
            result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 0
    assert "No deliveries completed" in captured.out
    assert "Try increasing the time period" in captured.out


def test_cmd_summary_invalid_days(capsys):
    """Test cmd_summary with invalid --days parameter (zero or negative)."""
    args = Namespace(days=0, format="markdown")

    result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "--days must be greater than 0" in captured.out


def test_cmd_summary_invalid_format(sample_roadmap_file, capsys):
    """Test cmd_summary with invalid --format parameter."""
    args = Namespace(days=14, format="json")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "Invalid format" in captured.out


def test_cmd_summary_missing_roadmap(capsys):
    """Test cmd_summary when ROADMAP.md does not exist."""
    args = Namespace(days=14, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path("/nonexistent/ROADMAP.md")):
        result = cmd_summary(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "ROADMAP not found" in captured.out


# ==================== CMD_CALENDAR TESTS ====================


def test_cmd_calendar_default_parameters(sample_roadmap_file, mock_upcoming, capsys):
    """Test cmd_calendar with default parameters (3 items, markdown format)."""
    args = Namespace(limit=3, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=mock_upcoming,
        ):
            result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 0
    assert "US-017" in captured.out
    assert "Summary & Calendar" in captured.out
    assert "5-7 days" in captured.out
    assert "Proactive delivery summaries" in captured.out


def test_cmd_calendar_custom_limit(sample_roadmap_file, mock_upcoming, capsys):
    """Test cmd_calendar with custom --limit parameter."""
    args = Namespace(limit=5, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=mock_upcoming,
        ) as mock_get_upcoming:
            result = cmd_calendar(args)

            # Verify get_upcoming_deliverables called with correct limit
            mock_get_upcoming.assert_called_once_with(limit=5)

    capsys.readouterr()
    assert result == 0


def test_cmd_calendar_text_format(sample_roadmap_file, mock_upcoming, capsys):
    """Test cmd_calendar with text format (removes markdown formatting)."""
    args = Namespace(limit=3, format="text")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=mock_upcoming,
        ):
            result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 0
    assert "US-017" in captured.out
    # Text format should have fewer markdown symbols
    assert "**" not in captured.out or captured.out.count("**") < 10


def test_cmd_calendar_no_upcoming(sample_roadmap_file, capsys):
    """Test cmd_calendar when no upcoming deliverables found."""
    args = Namespace(limit=3, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=[],
        ):
            result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 0
    assert "No upcoming deliverables" in captured.out
    assert "Add estimated effort to stories" in captured.out


def test_cmd_calendar_invalid_limit(capsys):
    """Test cmd_calendar with invalid --limit parameter (zero or negative)."""
    args = Namespace(limit=0, format="markdown")

    result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "--limit must be greater than 0" in captured.out


def test_cmd_calendar_invalid_format(sample_roadmap_file, capsys):
    """Test cmd_calendar with invalid --format parameter."""
    args = Namespace(limit=3, format="xml")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "Invalid format" in captured.out


def test_cmd_calendar_missing_roadmap(capsys):
    """Test cmd_calendar when ROADMAP.md does not exist."""
    args = Namespace(limit=3, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path("/nonexistent/ROADMAP.md")):
        result = cmd_calendar(args)

    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.out
    assert "ROADMAP not found" in captured.out


# ==================== INTEGRATION TESTS ====================


def test_summary_and_calendar_work_together(sample_roadmap_file, mock_completions, mock_upcoming, capsys):
    """Test that summary and calendar commands can be used together."""
    # First run summary
    args_summary = Namespace(days=14, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=mock_completions,
        ):
            result1 = cmd_summary(args_summary)

    assert result1 == 0

    # Then run calendar
    args_calendar = Namespace(limit=3, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=mock_upcoming,
        ):
            result2 = cmd_calendar(args_calendar)

    assert result2 == 0

    captured = capsys.readouterr()
    # Should contain output from both commands
    assert "US-017" in captured.out


def test_summary_tip_mentions_calendar(sample_roadmap_file, mock_completions, capsys):
    """Test that summary command mentions calendar in tips."""
    args = Namespace(days=14, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_recent_completions",
            return_value=mock_completions,
        ):
            cmd_summary(args)

    captured = capsys.readouterr()
    assert "calendar" in captured.out.lower()


def test_calendar_tip_mentions_summary(sample_roadmap_file, mock_upcoming, capsys):
    """Test that calendar command mentions summary in tips."""
    args = Namespace(limit=3, format="markdown")

    with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", Path(sample_roadmap_file)):
        with patch(
            "coffee_maker.reports.status_report_generator.StatusReportGenerator.get_upcoming_deliverables",
            return_value=mock_upcoming,
        ):
            cmd_calendar(args)

    captured = capsys.readouterr()
    assert "summary" in captured.out.lower()
