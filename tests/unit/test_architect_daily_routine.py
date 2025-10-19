"""Unit tests for ArchitectDailyRoutine (CFR-011 enforcement).

Tests verify:
1. CFR011ViolationError exceptions are raised correctly
2. Tracking file is created and persisted
3. Report reading is tracked
4. Codebase analysis frequency is enforced
5. Status methods return correct information
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from coffee_maker.autonomous.architect_daily_routine import ArchitectDailyRoutine, CFR011ViolationError


@pytest.fixture
def temp_dirs(monkeypatch):
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Override class constants
        tracking_file = temp_path / "data" / "architect_integration_status.json"
        reports_dir = temp_path / "docs" / "code-searcher"

        monkeypatch.setattr(ArchitectDailyRoutine, "TRACKING_FILE", tracking_file)
        monkeypatch.setattr(ArchitectDailyRoutine, "REPORTS_DIR", reports_dir)

        # Create reports directory
        reports_dir.mkdir(parents=True, exist_ok=True)

        yield temp_path, reports_dir


@pytest.fixture
def routine(temp_dirs):
    """Create ArchitectDailyRoutine with temporary directories."""
    return ArchitectDailyRoutine()


def test_get_unread_reports_empty(routine, temp_dirs):
    """Test when no reports exist."""
    unread = routine.get_unread_reports()
    assert unread == []


def test_get_unread_reports_some_unread(routine, temp_dirs):
    """Test when some reports are unread."""
    _, reports_dir = temp_dirs

    # Create reports
    report1 = reports_dir / "ANALYSIS_2025-10-17.md"
    report2 = reports_dir / "AUDIT_2025-10-18.md"
    report1.write_text("Report 1")
    report2.write_text("Report 2")

    # Mark report1 as read
    routine.mark_reports_read([report1])

    # Get unread
    unread = routine.get_unread_reports()

    assert len(unread) == 1
    assert unread[0].name == "AUDIT_2025-10-18.md"


def test_enforce_cfr_011_violation_unread_reports(routine, temp_dirs):
    """Test CFR-011 enforcement with unread reports."""
    _, reports_dir = temp_dirs

    report = reports_dir / "ANALYSIS.md"
    report.write_text("Report")

    with pytest.raises(CFR011ViolationError, match="Unread code-searcher reports"):
        routine.enforce_cfr_011()


def test_enforce_cfr_011_violation_analysis_due(routine):
    """Test CFR-011 enforcement when weekly analysis due."""
    # Never analyzed
    with pytest.raises(CFR011ViolationError, match="Weekly codebase analysis overdue"):
        routine.enforce_cfr_011()


def test_enforce_cfr_011_compliant(routine):
    """Test CFR-011 enforcement when compliant."""
    # Mark as analyzed today
    routine.mark_codebase_analyzed()

    # Should not raise
    routine.enforce_cfr_011()


def test_mark_reports_read(routine, temp_dirs):
    """Test marking reports as read."""
    _, reports_dir = temp_dirs

    report1 = reports_dir / "report1.md"
    report2 = reports_dir / "report2.md"
    report1.write_text("Report 1")
    report2.write_text("Report 2")

    routine.mark_reports_read([report1, report2])

    # Verify status was updated
    assert "report1.md" in routine.status["reports_read"]
    assert "report2.md" in routine.status["reports_read"]
    assert routine.status["last_code_searcher_read"] == datetime.now().strftime("%Y-%m-%d")


def test_is_codebase_analysis_due_never_analyzed(routine):
    """Test codebase analysis is due when never analyzed."""
    assert routine.is_codebase_analysis_due() is True


def test_is_codebase_analysis_due_recent(routine):
    """Test codebase analysis is not due when recent."""
    routine.mark_codebase_analyzed()
    assert routine.is_codebase_analysis_due() is False


def test_is_codebase_analysis_due_old(routine):
    """Test codebase analysis is due when >7 days old."""
    # Set last analysis to 8 days ago
    eight_days_ago = datetime.now() - timedelta(days=8)
    routine.status["last_codebase_analysis"] = eight_days_ago.strftime("%Y-%m-%d")
    routine._save_status()

    assert routine.is_codebase_analysis_due() is True


def test_get_compliance_status_compliant(routine):
    """Test compliance status when compliant."""
    routine.mark_codebase_analyzed()

    status = routine.get_compliance_status()

    assert status["compliant"] is True
    assert status["analysis_due"] is False
    assert len(status["unread_reports"]) == 0


def test_get_compliance_status_not_compliant(routine, temp_dirs):
    """Test compliance status when not compliant."""
    _, reports_dir = temp_dirs

    # Create unread report
    report = reports_dir / "ANALYSIS.md"
    report.write_text("Report")

    status = routine.get_compliance_status()

    assert status["compliant"] is False
    assert len(status["unread_reports"]) == 1
    assert status["analysis_due"] is True


def test_increment_refactoring_specs(routine):
    """Test incrementing refactoring specs count."""
    assert routine.status["refactoring_specs_created"] == 0

    routine.increment_refactoring_specs()
    assert routine.status["refactoring_specs_created"] == 1

    routine.increment_refactoring_specs(3)
    assert routine.status["refactoring_specs_created"] == 4


def test_increment_specs_updated(routine):
    """Test incrementing specs updated count."""
    assert routine.status["specs_updated"] == 0

    routine.increment_specs_updated()
    assert routine.status["specs_updated"] == 1

    routine.increment_specs_updated(2)
    assert routine.status["specs_updated"] == 3
