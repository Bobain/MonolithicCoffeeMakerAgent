"""Integration tests for architect continuous spec improvement workflow (US-049).

Tests cover end-to-end workflows:
- Full review workflow (daily + weekly)
- Metrics persistence across daemon restarts
- Report generation with real spec files
"""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.autonomous.architect_metrics import ArchitectMetrics
from coffee_maker.autonomous.architect_report_generator import WeeklyReportGenerator
from coffee_maker.autonomous.architect_review_triggers import ReviewTrigger


class TestArchitectWorkflow:
    """Integration tests for full architect review workflow."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def setup_environment(self, temp_dir):
        """Set up full environment with all components."""
        # Create necessary directories
        (temp_dir / "docs" / "roadmap").mkdir(parents=True)
        (temp_dir / "docs" / "architecture" / "specs").mkdir(parents=True)

        # Create ROADMAP.md
        roadmap_file = temp_dir / "docs" / "roadmap" / "ROADMAP.md"
        roadmap_file.write_text("# ROADMAP\n\nInitial content")

        # Create some spec files
        spec1 = temp_dir / "docs" / "architecture" / "specs" / "SPEC-009-test.md"
        spec1.write_text("# SPEC-009\n\nTest spec 1")

        spec2 = temp_dir / "docs" / "architecture" / "specs" / "SPEC-010-test.md"
        spec2.write_text("# SPEC-010\n\nTest spec 2")

        # Initialize components
        trigger = ReviewTrigger(data_dir=temp_dir)
        metrics = ArchitectMetrics(metrics_file=temp_dir / "architect_metrics.json")
        generator = WeeklyReportGenerator(metrics=metrics, output_dir=temp_dir / "docs" / "architecture")

        return {
            "temp_dir": temp_dir,
            "roadmap_file": roadmap_file,
            "trigger": trigger,
            "metrics": metrics,
            "generator": generator,
        }

    def test_full_review_workflow(self, setup_environment, monkeypatch):
        """Test complete daily and weekly review workflow."""
        env = setup_environment

        # Change to temp directory so ROADMAP.md is found
        monkeypatch.chdir(env["temp_dir"])

        # === STEP 1: Initial state - both reviews should trigger ===
        assert env["trigger"].should_run_daily_review() is True
        assert env["trigger"].should_run_weekly_review() is True

        # === STEP 2: Perform daily review ===
        env["trigger"].mark_review_completed("daily")

        # Daily review should not trigger immediately after
        assert env["trigger"].should_run_daily_review() is False

        # Weekly review should still trigger
        assert env["trigger"].should_run_weekly_review() is True

        # === STEP 3: Perform weekly review with metrics ===
        env["metrics"].record_simplification(
            spec_id="SPEC-009",
            original_hours=80.0,
            simplified_hours=16.0,
            description="Reused DeveloperStatus infrastructure",
        )

        env["metrics"].record_reuse(
            spec_id="SPEC-010",
            reused_components=["NotificationDB", "DeveloperStatus"],
            description="Leveraged existing notification system",
        )

        # Generate weekly report
        findings = {
            "specs_reviewed": ["SPEC-009", "SPEC-010"],
            "simplifications_made": [
                {
                    "spec_id": "SPEC-009",
                    "title": "Enhanced Communication",
                    "reduction_percent": 80.0,
                    "original_hours": 80.0,
                    "simplified_hours": 16.0,
                    "effort_saved": 64.0,
                    "description": "Reused DeveloperStatus infrastructure",
                }
            ],
            "reuse_opportunities": [
                {
                    "spec_id": "SPEC-010",
                    "components": ["NotificationDB", "DeveloperStatus"],
                }
            ],
            "recommendations": [
                "Create shared JSON file utility",
                "Extract validation logic",
            ],
        }

        report_path = env["generator"].generate_report(findings)

        # Mark weekly review completed
        env["trigger"].mark_review_completed("weekly")

        # === STEP 4: Verify results ===
        # Report file should exist
        assert report_path.exists()
        assert "WEEKLY_SPEC_REVIEW" in report_path.name

        # Report should contain key information
        report_content = report_path.read_text()
        assert "SPEC-009" in report_content
        assert "SPEC-010" in report_content
        assert "80.0%" in report_content  # Simplification rate
        assert "64.0 hours" in report_content  # Effort saved

        # Metrics should be persisted
        summary = env["metrics"].get_summary()
        assert summary["total_simplifications"] == 1
        assert summary["total_effort_saved"] == 64.0
        assert summary["total_reuse_opportunities"] == 1

        # Neither review should trigger immediately after
        assert env["trigger"].should_run_daily_review() is False
        assert env["trigger"].should_run_weekly_review() is False

    def test_metrics_persistence(self, setup_environment):
        """Test that metrics survive daemon restart (file-based persistence)."""
        env = setup_environment

        # === STEP 1: Record metrics with first instance ===
        metrics1 = env["metrics"]

        metrics1.record_simplification(
            spec_id="SPEC-001", original_hours=40.0, simplified_hours=10.0, description="Test 1"
        )

        metrics1.record_reuse(spec_id="SPEC-002", reused_components=["CompA", "CompB"], description="Test reuse")

        # Get summary
        summary1 = metrics1.get_summary()
        assert summary1["total_simplifications"] == 1
        assert summary1["total_reuse_opportunities"] == 1

        # === STEP 2: Create new instance (simulating daemon restart) ===
        metrics2 = ArchitectMetrics(metrics_file=env["temp_dir"] / "architect_metrics.json")

        # === STEP 3: Verify metrics persisted ===
        summary2 = metrics2.get_summary()

        assert summary2["total_simplifications"] == 1
        assert summary2["total_effort_saved"] == 30.0
        assert summary2["total_reuse_opportunities"] == 1
        assert summary2["specs_reviewed"] == 2

        # === STEP 4: Add more metrics with second instance ===
        metrics2.record_simplification(
            spec_id="SPEC-003", original_hours=60.0, simplified_hours=20.0, description="Test 2"
        )

        # === STEP 5: Verify cumulative metrics ===
        summary3 = metrics2.get_summary()

        assert summary3["total_simplifications"] == 2
        assert summary3["total_effort_saved"] == 70.0  # 30 + 40
        assert summary3["specs_reviewed"] == 3

    def test_report_generation_with_real_specs(self, setup_environment, monkeypatch):
        """Test report generation using actual spec files."""
        env = setup_environment

        # Change to temp directory
        monkeypatch.chdir(env["temp_dir"])

        # Create more realistic spec files
        specs_dir = env["temp_dir"] / "docs" / "architecture" / "specs"

        # Remove existing test specs
        for spec in specs_dir.glob("SPEC-*.md"):
            spec.unlink()

        # SPEC-009: Large simplification
        spec9 = specs_dir / "SPEC-009-enhanced-communication.md"
        spec9.write_text(
            """# SPEC-009: Enhanced Communication

## Estimated Effort
- Original: 80 hours (2 weeks)
- Simplified: 16 hours (2 days)
- Reduction: 80%

## Simplification Strategy
Reuse existing DeveloperStatus infrastructure instead of building new metrics system.
"""
        )

        # SPEC-010: Moderate simplification
        spec10 = specs_dir / "SPEC-010-user-listener-ui.md"
        spec10.write_text(
            """# SPEC-010: User Listener UI

## Estimated Effort
- Original: 24 hours
- Simplified: 12 hours
- Reduction: 50%

## Reused Components
- NotificationDB
- DeveloperStatus
"""
        )

        # Record metrics for these specs
        env["metrics"].record_simplification(
            spec_id="SPEC-009",
            original_hours=80.0,
            simplified_hours=16.0,
            description="Reused DeveloperStatus infrastructure, removed 6 modules",
        )

        env["metrics"].record_simplification(
            spec_id="SPEC-010",
            original_hours=24.0,
            simplified_hours=12.0,
            description="Leveraged existing NotificationDB, simplified UI to terminal-only",
        )

        env["metrics"].record_reuse(
            spec_id="SPEC-009",
            reused_components=["DeveloperStatus", "NotificationDB"],
            description="Reused status tracking infrastructure",
        )

        env["metrics"].record_reuse(
            spec_id="SPEC-010",
            reused_components=["NotificationDB", "DeveloperStatus"],
            description="Leveraged existing systems",
        )

        # Generate report
        spec_files = list(specs_dir.glob("SPEC-*.md"))
        assert len(spec_files) == 2  # SPEC-009 and SPEC-010

        findings = {
            "specs_reviewed": [s.stem for s in spec_files],
            "simplifications_made": [
                {
                    "spec_id": "SPEC-009",
                    "title": "Enhanced Communication",
                    "reduction_percent": 80.0,
                    "original_hours": 80.0,
                    "simplified_hours": 16.0,
                    "effort_saved": 64.0,
                    "description": "Reused DeveloperStatus infrastructure, removed 6 modules",
                },
                {
                    "spec_id": "SPEC-010",
                    "title": "User Listener UI",
                    "reduction_percent": 50.0,
                    "original_hours": 24.0,
                    "simplified_hours": 12.0,
                    "effort_saved": 12.0,
                    "description": "Leveraged existing NotificationDB",
                },
            ],
            "reuse_opportunities": [
                {
                    "spec_id": "SPEC-009",
                    "components": ["DeveloperStatus", "NotificationDB"],
                },
                {
                    "spec_id": "SPEC-010",
                    "components": ["NotificationDB", "DeveloperStatus"],
                },
            ],
            "recommendations": [
                "Create shared JSON file utility (used in 6 specs)",
                "Extract validation logic into reusable module",
                "Consider shared testing utilities for daemon tests",
            ],
        }

        report_path = env["generator"].generate_report(findings)

        # Verify report
        assert report_path.exists()

        content = report_path.read_text()

        # Check structure
        assert "# Weekly Spec Review" in content
        assert "## Summary" in content
        assert "## Metrics" in content
        assert "## Improvements Made This Week" in content
        assert "## Reuse Opportunities Identified" in content
        assert "## Recommendations" in content

        # Check content
        assert "Reviewed 2 specs" in content
        assert "SPEC-009" in content
        assert "SPEC-010" in content
        assert "80.0%" in content  # SPEC-009 reduction
        assert "50.0%" in content  # SPEC-010 reduction
        assert "64.0 hours" in content  # SPEC-009 effort saved
        assert "12.0 hours" in content  # SPEC-010 effort saved

        # Check summary metrics
        summary = env["metrics"].get_summary()
        assert summary["total_simplifications"] == 2
        assert summary["total_effort_saved"] == 76.0  # 64 + 12
        assert summary["avg_reduction_percent"] == 65.0  # (80 + 50) / 2
        assert summary["total_reuse_opportunities"] == 2
