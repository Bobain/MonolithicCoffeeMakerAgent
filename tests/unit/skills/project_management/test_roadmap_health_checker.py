"""Unit tests for ROADMAP Health Checker skill."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.skills.project_management import (
    HealthReport,
    Priority,
    RoadmapHealthChecker,
)


@pytest.fixture
def temp_roadmap():
    """Create a temporary ROADMAP.md for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        roadmap_dir = Path(tmpdir) / "docs" / "roadmap"
        roadmap_dir.mkdir(parents=True)
        roadmap_path = roadmap_dir / "ROADMAP.md"
        yield roadmap_path, Path(tmpdir)


@pytest.fixture
def sample_roadmap_content():
    """Sample ROADMAP.md content for testing."""
    return """# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-19
**Current Branch**: `roadmap`

## 🔴 TOP PRIORITY FOR code_developer (START HERE)

PRIORITY 15: Current work

---

### PRIORITY 1: Analytics ✅ Complete

**Status**: ✅ Complete

Analytics implementation completed.

---

### PRIORITY 2: Project Manager CLI ✅ Complete

**Status**: ✅ Complete

Project manager implemented.

---

### PRIORITY 3: code_developer ✅ Complete

**Status**: ✅ Complete

Code developer completed.

---

### PRIORITY 10: US-070 - ROADMAP Health Check 🔄 In Progress

**Status**: 🔄 In Progress

**Priority Level**: ⭐⭐⭐ HIGHEST

Implementing roadmap health check skill.

---

### PRIORITY 11: Feature X 📝 Planned

**Status**: 📝 Planned

New feature to implement.

---

### PRIORITY 12: Feature Y 📝 Planned

**Status**: 📝 Planned

Another planned feature.

---

### PRIORITY 13: Blocked Feature ⏸️ Blocked

**Status**: ⏸️ Blocked

This feature is blocked waiting for external approval.

---
"""


class TestRoadmapHealthChecker:
    """Test RoadmapHealthChecker class."""

    def test_initialization(self, temp_roadmap):
        """Test RoadmapHealthChecker initialization."""
        roadmap_path, project_root = temp_roadmap

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        assert checker.roadmap_path == roadmap_path
        assert checker.project_root == project_root

    def test_initialization_defaults(self):
        """Test RoadmapHealthChecker with default paths."""
        checker = RoadmapHealthChecker()

        assert checker.roadmap_path == Path.cwd() / "docs" / "roadmap" / "ROADMAP.md"
        assert checker.project_root == Path.cwd()

    def test_parse_roadmap_empty_file(self, temp_roadmap):
        """Test parsing empty ROADMAP."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text("# Empty ROADMAP\n", encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        assert priorities == []

    def test_parse_roadmap_with_priorities(self, temp_roadmap, sample_roadmap_content):
        """Test parsing ROADMAP with priorities."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Should find priorities 1, 2, 3, 10, 11, 12, 13
        assert len(priorities) >= 5

        # Check priority numbers
        numbers = [p.number for p in priorities]
        assert "1" in numbers
        assert "10" in numbers
        assert "11" in numbers

        # Check statuses
        statuses = [p.status for p in priorities]
        assert "✅" in statuses  # Complete
        assert "🔄" in statuses  # In Progress
        assert "📝" in statuses  # Planned
        assert "⏸️" in statuses  # Blocked

    def test_parse_roadmap_extracts_user_story_id(self, temp_roadmap, sample_roadmap_content):
        """Test parsing extracts US-XXX IDs."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Find priority 10 with US-070
        priority_10 = next((p for p in priorities if p.number == "10"), None)
        assert priority_10 is not None
        assert priority_10.user_story_id == "US-070"

    def test_calculate_velocity_no_completions(self, temp_roadmap, sample_roadmap_content):
        """Test velocity calculation with no recent completions."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Set all completed priorities to old dates
        for p in priorities:
            if p.status == "✅":
                p.last_updated_date = datetime.now() - timedelta(days=60)

        velocity = checker._calculate_velocity(priorities)

        assert velocity.last_7_days == 0
        assert velocity.last_30_days == 0
        assert velocity.average_per_week == 0.0

    def test_calculate_velocity_with_recent_completions(self, temp_roadmap, sample_roadmap_content):
        """Test velocity calculation with recent completions."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Set some completions to recent dates
        completed_priorities = [p for p in priorities if p.status == "✅"][:3]
        if len(completed_priorities) >= 3:
            completed_priorities[0].last_updated_date = datetime.now() - timedelta(days=2)
            completed_priorities[1].last_updated_date = datetime.now() - timedelta(days=5)
            completed_priorities[2].last_updated_date = datetime.now() - timedelta(days=15)

            velocity = checker._calculate_velocity(priorities)

            assert velocity.last_7_days == 2
            assert velocity.last_30_days == 3

    def test_calculate_metrics(self, temp_roadmap, sample_roadmap_content):
        """Test health metrics calculation."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Create mock velocity
        from coffee_maker.skills.project_management import VelocityMetrics

        velocity = VelocityMetrics(last_7_days=2, last_30_days=8, average_per_week=2.0, trend="stable")

        metrics = checker._calculate_metrics(priorities, velocity)

        assert metrics.total_priorities > 0
        assert metrics.completed_count >= 3  # Priorities 1, 2, 3
        assert metrics.in_progress_count >= 1  # Priority 10
        assert metrics.planned_count >= 2  # Priorities 11, 12
        assert metrics.blocked_count >= 1  # Priority 13
        assert 0.0 <= metrics.backlog_ratio <= 1.0

    def test_detect_blockers_explicit_blocked(self, temp_roadmap, sample_roadmap_content):
        """Test detection of explicitly blocked priorities."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Set blocked priority date
        blocked_priority = next((p for p in priorities if p.status == "⏸️"), None)
        if blocked_priority:
            blocked_priority.last_updated_date = datetime.now() - timedelta(days=10)

        blockers = checker._detect_blockers(priorities)

        # Should find at least one blocked priority
        assert len(blockers) >= 1

        # Check blocker info
        explicit_blockers = [b for b in blockers if b.blocker_type == "explicit_blocked"]
        assert len(explicit_blockers) >= 1

        blocker = explicit_blockers[0]
        assert blocker.severity in ["CRITICAL", "HIGH"]
        assert blocker.days_blocked >= 10

    def test_detect_blockers_stale_work(self, temp_roadmap, sample_roadmap_content):
        """Test detection of stale work (in progress but no updates)."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        priorities = checker._parse_roadmap()

        # Set in-progress priority to old date
        in_progress_priority = next((p for p in priorities if p.status == "🔄"), None)
        if in_progress_priority:
            in_progress_priority.last_updated_date = datetime.now() - timedelta(days=10)

        blockers = checker._detect_blockers(priorities)

        # Should find stale work
        stale_blockers = [b for b in blockers if b.blocker_type == "stale_work"]
        if stale_blockers:
            blocker = stale_blockers[0]
            assert blocker.severity in ["HIGH", "MEDIUM"]
            assert blocker.days_blocked >= 10

    def test_calculate_health_score_no_blockers(self, temp_roadmap):
        """Test health score with no blockers (should be high)."""
        roadmap_path, project_root = temp_roadmap

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        from coffee_maker.skills.project_management import HealthMetrics, VelocityMetrics

        velocity = VelocityMetrics(last_7_days=3, last_30_days=10, average_per_week=2.3, trend="stable")
        metrics = HealthMetrics(
            health_score=0,
            velocity=velocity,
            total_priorities=10,
            planned_count=3,
            in_progress_count=1,
            completed_count=6,
            blocked_count=0,
            stale_count=0,
            dependency_blocked_count=0,
            backlog_ratio=0.3,
        )

        score = checker._calculate_health_score(metrics, [])

        assert score >= 90  # Should be very healthy

    def test_calculate_health_score_with_critical_blockers(self, temp_roadmap):
        """Test health score with critical blockers (should be low)."""
        roadmap_path, project_root = temp_roadmap

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        from coffee_maker.skills.project_management import BlockerInfo, HealthMetrics, VelocityMetrics

        velocity = VelocityMetrics(last_7_days=1, last_30_days=4, average_per_week=0.9, trend="declining")
        metrics = HealthMetrics(
            health_score=0,
            velocity=velocity,
            total_priorities=10,
            planned_count=5,
            in_progress_count=2,
            completed_count=3,
            blocked_count=2,
            stale_count=1,
            dependency_blocked_count=0,
            backlog_ratio=0.5,
        )

        # Create critical blockers
        blockers = [
            BlockerInfo(
                priority=Priority(number="5", status="⏸️", title="Blocked Feature", description=""),
                blocker_type="explicit_blocked",
                severity="CRITICAL",
                days_blocked=10,
                description="Blocked for 10 days",
                recommendation="Escalate",
            ),
            BlockerInfo(
                priority=Priority(number="6", status="🔄", title="Stale Work", description=""),
                blocker_type="stale_work",
                severity="HIGH",
                days_blocked=9,
                description="Stale for 9 days",
                recommendation="Check status",
            ),
        ]

        score = checker._calculate_health_score(metrics, blockers)

        assert score < 70  # Should be low due to blockers

    def test_determine_health_status(self, temp_roadmap):
        """Test health status determination from score."""
        roadmap_path, project_root = temp_roadmap
        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        assert checker._determine_health_status(95) == "HEALTHY"
        assert checker._determine_health_status(85) == "HEALTHY"
        assert checker._determine_health_status(75) == "WARNING"
        assert checker._determine_health_status(65) == "WARNING"
        assert checker._determine_health_status(45) == "CRITICAL"

    def test_generate_recommendations_no_issues(self, temp_roadmap):
        """Test recommendation generation with no issues."""
        roadmap_path, project_root = temp_roadmap
        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        from coffee_maker.skills.project_management import HealthMetrics, VelocityMetrics

        velocity = VelocityMetrics(last_7_days=3, last_30_days=10, average_per_week=2.3, trend="stable")
        metrics = HealthMetrics(
            health_score=95,
            velocity=velocity,
            total_priorities=10,
            planned_count=3,
            in_progress_count=1,
            completed_count=6,
            blocked_count=0,
            stale_count=0,
            dependency_blocked_count=0,
            backlog_ratio=0.3,
        )

        recommendations = checker._generate_recommendations(metrics, [])

        assert len(recommendations) >= 1
        assert any("healthy" in r.lower() for r in recommendations)

    def test_generate_recommendations_with_blockers(self, temp_roadmap):
        """Test recommendation generation with blockers."""
        roadmap_path, project_root = temp_roadmap
        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        from coffee_maker.skills.project_management import BlockerInfo, HealthMetrics, VelocityMetrics

        velocity = VelocityMetrics(last_7_days=1, last_30_days=4, average_per_week=0.9, trend="declining")
        metrics = HealthMetrics(
            health_score=60,
            velocity=velocity,
            total_priorities=10,
            planned_count=5,
            in_progress_count=2,
            completed_count=3,
            blocked_count=1,
            stale_count=0,
            dependency_blocked_count=0,
            backlog_ratio=0.5,
        )

        blockers = [
            BlockerInfo(
                priority=Priority(number="5", status="⏸️", title="Blocked Feature", description=""),
                blocker_type="explicit_blocked",
                severity="CRITICAL",
                days_blocked=10,
                description="Blocked for 10 days",
                recommendation="Escalate to user",
            )
        ]

        recommendations = checker._generate_recommendations(metrics, blockers)

        assert len(recommendations) >= 2
        assert any("CRITICAL" in r for r in recommendations)

    def test_generate_report_markdown(self, temp_roadmap):
        """Test markdown report generation."""
        roadmap_path, project_root = temp_roadmap
        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)

        from coffee_maker.skills.project_management import HealthMetrics, VelocityMetrics

        velocity = VelocityMetrics(last_7_days=2, last_30_days=8, average_per_week=2.0, trend="stable")
        metrics = HealthMetrics(
            health_score=85,
            velocity=velocity,
            total_priorities=10,
            planned_count=3,
            in_progress_count=1,
            completed_count=6,
            blocked_count=0,
            stale_count=0,
            dependency_blocked_count=0,
            backlog_ratio=0.3,
        )

        report_md = checker._generate_report_markdown(metrics, [], ["Continue current pace"], "HEALTHY")

        # Check report structure
        assert "# ROADMAP Health Report" in report_md
        assert "HEALTHY" in report_md
        assert "**Total Priorities**: 10" in report_md
        assert "**Completed**: 6" in report_md
        assert "Continue current pace" in report_md

    def test_analyze_roadmap_full_integration(self, temp_roadmap, sample_roadmap_content):
        """Test full analyze_roadmap() integration."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        report = checker.analyze_roadmap()

        # Check report structure
        assert isinstance(report, HealthReport)
        assert report.health_status in ["HEALTHY", "WARNING", "CRITICAL"]
        assert 0 <= report.metrics.health_score <= 100
        assert report.execution_time_seconds > 0
        assert len(report.report_markdown) > 0

        # Check metrics
        assert report.metrics.total_priorities > 0
        assert report.metrics.completed_count >= 0
        assert report.metrics.planned_count >= 0

    def test_save_report(self, temp_roadmap, sample_roadmap_content):
        """Test saving health report to file."""
        roadmap_path, project_root = temp_roadmap
        roadmap_path.write_text(sample_roadmap_content, encoding="utf-8")

        checker = RoadmapHealthChecker(roadmap_path=roadmap_path, project_root=project_root)
        report = checker.analyze_roadmap()

        # Save report
        output_path = checker.save_report(report)

        # Check file was created
        assert output_path.exists()
        assert output_path.suffix == ".md"
        assert "roadmap-health" in output_path.name

        # Check content
        content = output_path.read_text(encoding="utf-8")
        assert "# ROADMAP Health Report" in content
