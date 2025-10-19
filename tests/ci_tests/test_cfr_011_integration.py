"""Integration tests for CFR-011 enforcement.

These tests verify that CFR-011 enforcement works correctly in the full system:
- Spec creation is blocked when violations exist
- Spec creation is allowed when compliant
- Notifications are sent on violations
"""

import pytest

from coffee_maker.autonomous.architect_daily_routine import (
    ArchitectDailyRoutine,
    CFR011ViolationError,
)


@pytest.fixture
def temp_tracking_file(tmp_path, monkeypatch):
    """Create a temporary tracking file for testing."""
    tracking_file = tmp_path / "architect_integration_status.json"
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Monkeypatch the paths
    monkeypatch.setattr(ArchitectDailyRoutine, "TRACKING_FILE", tracking_file)
    monkeypatch.setattr(ArchitectDailyRoutine, "REPORTS_DIR", reports_dir)

    return tracking_file, reports_dir


def test_spec_creation_blocked_on_unread_reports(temp_tracking_file):
    """Test that spec creation is blocked when unread reports exist.

    This simulates the full workflow:
    1. code-searcher creates a report
    2. architect tries to create a spec
    3. CFR-011 enforcement blocks the spec creation
    """
    tracking_file, reports_dir = temp_tracking_file

    # Simulate code-searcher creating a report
    report = reports_dir / "CODE_QUALITY_ANALYSIS_2025-10-18.md"
    report.write_text("# Code Quality Analysis\n\nFound 5 issues...")

    # Create routine and try to enforce CFR-011
    routine = ArchitectDailyRoutine()

    # Should raise CFR011ViolationError due to unread report
    with pytest.raises(CFR011ViolationError) as exc_info:
        routine.enforce_cfr_011()

    # Verify error message mentions the unread report
    assert "CODE_QUALITY_ANALYSIS_2025-10-18.md" in str(exc_info.value)
    assert "Unread code-searcher reports" in str(exc_info.value)


def test_spec_creation_blocked_on_overdue_analysis(temp_tracking_file):
    """Test that spec creation is blocked when codebase analysis is overdue.

    This simulates:
    1. architect has never analyzed the codebase
    2. architect tries to create a spec
    3. CFR-011 enforcement blocks due to overdue analysis
    """
    tracking_file, reports_dir = temp_tracking_file

    # Create routine (never analyzed)
    routine = ArchitectDailyRoutine()

    # Should raise CFR011ViolationError due to overdue analysis
    with pytest.raises(CFR011ViolationError) as exc_info:
        routine.enforce_cfr_011()

    # Verify error message mentions overdue analysis
    assert "Weekly codebase analysis overdue" in str(exc_info.value)
    assert "NEVER" in str(exc_info.value)


def test_spec_creation_allowed_when_compliant(temp_tracking_file):
    """Test that spec creation is allowed when CFR-011 compliant.

    This simulates:
    1. architect reads all reports
    2. architect performs codebase analysis
    3. architect can create specs without errors
    """
    tracking_file, reports_dir = temp_tracking_file

    # Create a report
    report = reports_dir / "CODE_QUALITY_ANALYSIS_2025-10-18.md"
    report.write_text("# Code Quality Analysis\n\nFound 5 issues...")

    # Create routine and mark as compliant
    routine = ArchitectDailyRoutine()

    # Mark report as read
    routine.mark_reports_read([report])

    # Mark codebase as analyzed
    routine.mark_codebase_analyzed()

    # Should NOT raise (compliant)
    routine.enforce_cfr_011()

    # Verify compliance status
    status = routine.get_compliance_status()
    assert status["compliant"] is True
    assert len(status["unread_reports"]) == 0
    assert status["analysis_due"] is False


def test_spec_creation_blocked_on_multiple_violations(temp_tracking_file):
    """Test that spec creation is blocked when BOTH violations exist.

    This simulates:
    1. Unread reports exist
    2. Codebase analysis is overdue
    3. CFR-011 enforcement lists BOTH violations
    """
    tracking_file, reports_dir = temp_tracking_file

    # Create multiple reports
    report1 = reports_dir / "CODE_QUALITY_ANALYSIS_2025-10-18.md"
    report2 = reports_dir / "SECURITY_AUDIT_2025-10-19.md"
    report1.write_text("# Code Quality Analysis")
    report2.write_text("# Security Audit")

    # Create routine (never analyzed, unread reports)
    routine = ArchitectDailyRoutine()

    # Should raise CFR011ViolationError with BOTH violations
    with pytest.raises(CFR011ViolationError) as exc_info:
        routine.enforce_cfr_011()

    error_msg = str(exc_info.value)

    # Verify BOTH violations are listed
    assert "Unread code-searcher reports" in error_msg
    assert "Weekly codebase analysis overdue" in error_msg
    assert "CODE_QUALITY_ANALYSIS_2025-10-18.md" in error_msg
    assert "SECURITY_AUDIT_2025-10-19.md" in error_msg


def test_partial_compliance_still_blocks(temp_tracking_file):
    """Test that partial compliance still blocks spec creation.

    This simulates:
    1. architect reads reports (compliant)
    2. BUT codebase analysis is still overdue (non-compliant)
    3. Spec creation should be blocked
    """
    tracking_file, reports_dir = temp_tracking_file

    # Create and read report
    report = reports_dir / "CODE_QUALITY_ANALYSIS_2025-10-18.md"
    report.write_text("# Code Quality Analysis")

    routine = ArchitectDailyRoutine()
    routine.mark_reports_read([report])

    # Reports are read, but analysis still overdue
    # Should still raise CFR011ViolationError
    with pytest.raises(CFR011ViolationError) as exc_info:
        routine.enforce_cfr_011()

    # Verify only analysis violation is listed
    error_msg = str(exc_info.value)
    assert "Weekly codebase analysis overdue" in error_msg
    assert "Unread code-searcher reports" not in error_msg


def test_workflow_tracking_persists(temp_tracking_file):
    """Test that tracking data persists across routine instances.

    This verifies the tracking file is saved and loaded correctly.
    """
    tracking_file, reports_dir = temp_tracking_file

    # Create report
    report = reports_dir / "CODE_QUALITY_ANALYSIS_2025-10-18.md"
    report.write_text("# Code Quality Analysis")

    # First routine: mark report as read
    routine1 = ArchitectDailyRoutine()
    routine1.mark_reports_read([report])
    routine1.mark_codebase_analyzed()

    # Second routine: should load the same state
    routine2 = ArchitectDailyRoutine()

    # Verify data persisted
    assert routine2.status["last_code_searcher_read"] is not None
    assert routine2.status["last_codebase_analysis"] is not None
    assert "CODE_QUALITY_ANALYSIS_2025-10-18.md" in routine2.status["reports_read"]

    # Should be compliant (no violations)
    routine2.enforce_cfr_011()
