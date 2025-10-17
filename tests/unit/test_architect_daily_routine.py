"""Unit tests for ArchitectDailyRoutine (CFR-011 enforcement).

Tests verify:
1. CFR011ViolationError exceptions are raised correctly
2. Tracking file is created and persisted
3. Report reading is tracked
4. Codebase analysis frequency is enforced
5. Status methods return correct information
"""

import json
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

from coffee_maker.autonomous.architect_daily_routine import (
    ArchitectDailyRoutine,
    CFR011ViolationError,
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        status_file = temp_path / "architect_integration_status.json"
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()

        yield status_file, docs_dir


@pytest.fixture
def routine(temp_dirs):
    """Create ArchitectDailyRoutine with temporary directories."""
    status_file, docs_dir = temp_dirs
    return ArchitectDailyRoutine(status_file=status_file, docs_dir=docs_dir)


class TestCFR011ViolationError:
    """Test CFR011ViolationError exception."""

    def test_exception_creation(self):
        """Test creating CFR011ViolationError."""
        msg = "Test violation message"
        exc = CFR011ViolationError(msg)
        assert exc.message == msg
        assert str(exc) == msg

    def test_exception_is_exception(self):
        """Test CFR011ViolationError is an Exception."""
        exc = CFR011ViolationError("test")
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised(self):
        """Test CFR011ViolationError can be raised and caught."""
        with pytest.raises(CFR011ViolationError) as exc_info:
            raise CFR011ViolationError("test message")
        assert "test message" in str(exc_info.value)


class TestArchitectDailyRoutineInitialization:
    """Test ArchitectDailyRoutine initialization."""

    def test_init_creates_status_file_if_missing(self, temp_dirs):
        """Test that missing status file is created."""
        status_file, docs_dir = temp_dirs
        assert not status_file.exists()

        routine = ArchitectDailyRoutine(status_file=status_file, docs_dir=docs_dir)

        assert routine.status_file == status_file
        assert routine.docs_dir == docs_dir

    def test_init_loads_existing_status_file(self, temp_dirs):
        """Test that existing status file is loaded."""
        status_file, docs_dir = temp_dirs

        # Create initial status file
        initial_status = {
            "last_code_searcher_read": "2025-10-16",
            "last_codebase_analysis": "2025-10-15",
            "reports_read": ["report1.md", "report2.md"],
            "action_items_total": 5,
            "specs_created": 2,
            "specs_updated": 3,
            "next_analysis_due": "2025-10-22",
        }
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, "w") as f:
            json.dump(initial_status, f)

        routine = ArchitectDailyRoutine(status_file=status_file, docs_dir=docs_dir)

        assert routine._status["last_code_searcher_read"] == "2025-10-16"
        assert routine._status["last_codebase_analysis"] == "2025-10-15"
        assert routine._status["reports_read"] == ["report1.md", "report2.md"]


class TestFindNewReports:
    """Test finding new code-searcher reports."""

    def test_find_audit_reports(self, routine, temp_dirs):
        """Test finding *_AUDIT*.md files."""
        _, docs_dir = temp_dirs

        # Create audit reports
        (docs_dir / "SECURITY_AUDIT2025-10-17.md").write_text("# Security Audit")
        (docs_dir / "QUALITY_AUDIT2025-10-16.md").write_text("# Quality Audit")

        reports = routine._find_new_code_searcher_reports()

        assert "SECURITY_AUDIT2025-10-17.md" in reports
        assert "QUALITY_AUDIT2025-10-16.md" in reports

    def test_find_analysis_reports(self, routine, temp_dirs):
        """Test finding *_ANALYSIS*.md files."""
        _, docs_dir = temp_dirs

        # Create analysis reports
        (docs_dir / "CODE_QUALITY_ANALYSIS2025-10-17.md").write_text("# Code Quality")
        (docs_dir / "DEPENDENCY_ANALYSIS2025-10-17.md").write_text("# Dependencies")

        reports = routine._find_new_code_searcher_reports()

        assert "CODE_QUALITY_ANALYSIS2025-10-17.md" in reports
        assert "DEPENDENCY_ANALYSIS2025-10-17.md" in reports

    def test_find_codebase_summary_reports(self, routine, temp_dirs):
        """Test finding CODEBASE_ANALYSIS_SUMMARY*.md files."""
        _, docs_dir = temp_dirs

        # Create summary report
        (docs_dir / "CODEBASE_ANALYSIS_SUMMARY2025-10-17.md").write_text("# Summary")

        reports = routine._find_new_code_searcher_reports()

        assert "CODEBASE_ANALYSIS_SUMMARY2025-10-17.md" in reports

    def test_filters_already_read_reports(self, routine, temp_dirs):
        """Test that already-read reports are filtered out."""
        _, docs_dir = temp_dirs
        routine.status_file

        # Create reports
        (docs_dir / "AUDIT2025-10-17.md").write_text("# Audit")
        (docs_dir / "ANALYSIS2025-10-17.md").write_text("# Analysis")

        # Mark one as read
        routine._status["reports_read"] = ["AUDIT2025-10-17.md"]
        routine._save_status()

        reports = routine._find_new_code_searcher_reports()

        assert "AUDIT2025-10-17.md" not in reports
        assert "ANALYSIS2025-10-17.md" in reports

    def test_returns_empty_list_when_no_reports(self, routine):
        """Test returns empty list when no reports exist."""
        reports = routine._find_new_code_searcher_reports()
        assert reports == []


class TestReportTracking:
    """Test tracking report reading."""

    def test_mark_reports_read(self, routine, temp_dirs):
        """Test marking reports as read."""
        status_file, _ = temp_dirs

        routine._mark_reports_read(["report1.md", "report2.md"])

        # Verify status file was updated
        with open(status_file) as f:
            status = json.load(f)
        assert "report1.md" in status["reports_read"]
        assert "report2.md" in status["reports_read"]
        assert status["last_code_searcher_read"] == date.today().isoformat()

    def test_mark_reports_read_accumulates(self, routine, temp_dirs):
        """Test that marking reports accumulates them."""
        status_file, _ = temp_dirs

        routine._mark_reports_read(["report1.md"])
        routine._mark_reports_read(["report2.md"])

        with open(status_file) as f:
            status = json.load(f)
        assert "report1.md" in status["reports_read"]
        assert "report2.md" in status["reports_read"]

    def test_has_read_reports(self, routine):
        """Test checking if reports have been read."""
        routine._status["reports_read"] = ["report1.md", "report2.md"]

        assert routine._has_read_reports(["report1.md", "report2.md"])
        assert not routine._has_read_reports(["report1.md", "report3.md"])
        assert not routine._has_read_reports(["report3.md"])


class TestCodebaseAnalysisTracking:
    """Test tracking codebase analysis."""

    def test_mark_codebase_analysis_complete(self, routine, temp_dirs):
        """Test marking codebase analysis as complete."""
        status_file, _ = temp_dirs

        routine._mark_codebase_analysis_complete()

        with open(status_file) as f:
            status = json.load(f)
        assert status["last_codebase_analysis"] == date.today().isoformat()
        assert status["next_analysis_due"] == (date.today() + timedelta(days=7)).isoformat()

    def test_get_last_codebase_analysis(self, routine):
        """Test retrieving last analysis date."""
        today = date.today().isoformat()
        routine._status["last_codebase_analysis"] = today
        routine._save_status()

        result = routine.get_last_codebase_analysis()
        assert result == date.today()

    def test_get_last_codebase_analysis_none(self, routine):
        """Test returns None when no analysis has been done."""
        result = routine.get_last_codebase_analysis()
        assert result is None


class TestCFR011Enforcement:
    """Test CFR-011 enforcement checks."""

    def test_enforce_passes_when_compliant(self, routine, temp_dirs):
        """Test enforce_cfr_011 passes when compliant."""
        status_file, _ = temp_dirs

        # Mark today as read and analyzed
        routine._status["last_code_searcher_read"] = date.today().isoformat()
        routine._status["last_codebase_analysis"] = date.today().isoformat()
        routine._save_status()

        # Should not raise
        routine.enforce_cfr_011()

    def test_enforce_raises_when_unread_reports(self, routine, temp_dirs):
        """Test enforce raises when unread reports exist."""
        status_file, docs_dir = temp_dirs

        # Create unread report
        (docs_dir / "AUDIT2025-10-17.md").write_text("# Audit")

        # Mark yesterday as read
        routine._status["last_code_searcher_read"] = (date.today() - timedelta(days=1)).isoformat()
        routine._status["last_codebase_analysis"] = date.today().isoformat()
        routine._save_status()

        with pytest.raises(CFR011ViolationError) as exc_info:
            routine.enforce_cfr_011()

        assert "CFR-011 VIOLATION" in str(exc_info.value)
        assert "AUDIT2025-10-17.md" in str(exc_info.value)
        assert "daily-integration" in str(exc_info.value)

    def test_enforce_raises_when_no_analysis(self, routine):
        """Test enforce raises when no codebase analysis done."""
        routine._status["last_code_searcher_read"] = date.today().isoformat()
        routine._status["last_codebase_analysis"] = None
        routine._save_status()

        with pytest.raises(CFR011ViolationError) as exc_info:
            routine.enforce_cfr_011()

        assert "CFR-011 VIOLATION" in str(exc_info.value)
        assert "never been analyzed" in str(exc_info.value)
        assert "analyze-codebase" in str(exc_info.value)

    def test_enforce_raises_when_analysis_stale(self, routine):
        """Test enforce raises when codebase analysis >7 days old."""
        old_date = (date.today() - timedelta(days=8)).isoformat()

        routine._status["last_code_searcher_read"] = date.today().isoformat()
        routine._status["last_codebase_analysis"] = old_date
        routine._save_status()

        with pytest.raises(CFR011ViolationError) as exc_info:
            routine.enforce_cfr_011()

        assert "CFR-011 VIOLATION" in str(exc_info.value)
        assert "8 days since" in str(exc_info.value)
        assert "analyze-codebase" in str(exc_info.value)

    def test_enforce_passes_with_today_read_and_7_day_old_analysis(self, routine):
        """Test enforce passes when reports read today and analysis exactly 7 days old."""
        seven_days_ago = (date.today() - timedelta(days=7)).isoformat()

        routine._status["last_code_searcher_read"] = date.today().isoformat()
        routine._status["last_codebase_analysis"] = seven_days_ago
        routine._save_status()

        # Should not raise (7 days is acceptable, >7 is not)
        routine.enforce_cfr_011()


class TestPublicMethods:
    """Test public workflow methods."""

    def test_mark_daily_integration_complete(self, routine, temp_dirs):
        """Test marking daily integration complete."""
        status_file, docs_dir = temp_dirs

        # Create some reports
        (docs_dir / "AUDIT2025-10-17.md").write_text("# Audit")
        (docs_dir / "ANALYSIS2025-10-17.md").write_text("# Analysis")

        routine.mark_daily_integration_complete()

        with open(status_file) as f:
            status = json.load(f)
        assert "AUDIT2025-10-17.md" in status["reports_read"]
        assert "ANALYSIS2025-10-17.md" in status["reports_read"]

    def test_mark_codebase_analysis_complete(self, routine, temp_dirs):
        """Test marking codebase analysis complete."""
        status_file, _ = temp_dirs

        routine.mark_codebase_analysis_complete()

        with open(status_file) as f:
            status = json.load(f)
        assert status["last_codebase_analysis"] == date.today().isoformat()

    def test_get_unread_reports(self, routine, temp_dirs):
        """Test getting list of unread reports."""
        _, docs_dir = temp_dirs

        (docs_dir / "AUDIT2025-10-17.md").write_text("# Audit")
        (docs_dir / "ANALYSIS2025-10-17.md").write_text("# Analysis")

        reports = routine.get_unread_reports()

        assert len(reports) == 2
        assert "AUDIT2025-10-17.md" in reports
        assert "ANALYSIS2025-10-17.md" in reports


class TestStatusSummary:
    """Test status summary generation."""

    def test_get_status_summary_initial_state(self, routine):
        """Test status summary for initial state."""
        summary = routine.get_status_summary()

        assert "Architect Daily Integration Status" in summary
        assert "Never" in summary

    def test_get_status_summary_with_dates(self, routine):
        """Test status summary with dates filled in."""
        routine._status["last_code_searcher_read"] = "2025-10-16"
        routine._status["last_codebase_analysis"] = "2025-10-15"
        routine._status["reports_read"] = ["report1.md", "report2.md"]
        routine._save_status()

        summary = routine.get_status_summary()

        assert "2025-10-16" in summary
        assert "2025-10-15" in summary

    def test_get_status_summary_shows_recent_reports(self, routine):
        """Test status summary shows recent reports."""
        reports = [f"report{i}.md" for i in range(10)]
        routine._status["reports_read"] = reports
        routine._save_status()

        summary = routine.get_status_summary()

        # Should show last 5
        for i in range(5, 10):
            assert f"report{i}.md" in summary


class TestDateMethods:
    """Test date retrieval methods."""

    def test_get_last_code_searcher_read_valid(self, routine):
        """Test getting valid last read date."""
        today_str = date.today().isoformat()
        routine._status["last_code_searcher_read"] = today_str
        routine._save_status()

        result = routine.get_last_code_searcher_read()

        assert result == date.today()

    def test_get_last_code_searcher_read_none(self, routine):
        """Test returns None when never read."""
        result = routine.get_last_code_searcher_read()

        assert result is None
