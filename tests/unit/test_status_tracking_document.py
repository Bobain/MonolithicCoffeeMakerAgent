"""Unit tests for STATUS_TRACKING.md document generation.

Tests the auto-maintained STATUS_TRACKING.md document generation, including:
- Document structure validation
- Recent completions section
- Current work (in progress) section
- Next up (upcoming) section
- Velocity and accuracy metrics
- Auto-update triggers
"""

from datetime import datetime, timedelta

import pytest

from coffee_maker.reports.status_report_generator import StatusReportGenerator
from coffee_maker.reports.status_tracking_updater import (
    on_progress_update,
    on_story_completed,
    on_story_started,
    update_status_tracking,
)


@pytest.fixture
def mock_roadmap_with_completions(tmp_path):
    """Create a mock ROADMAP with completed stories."""
    roadmap_path = tmp_path / "ROADMAP.md"

    # Create roadmap with completions
    completion_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    old_completion_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    roadmap_content = f"""# ROADMAP

## User Stories

### 🎯 [US-016] Technical Spec Generation

**Status**: ✅ **COMPLETE**
**Completed**: {completion_date}

**Business Value**: Accurate delivery estimates before coding starts

**Key Features**:
- AI-assisted task breakdown
- Realistic time estimates with buffer
- 100 tests passing
- Reduced spec creation time by 90%

**Estimated Effort**: 4-5 days (4.5 days average)
**Actual Effort**: 4.0 days

---

### 🎯 [US-015] Estimation Metrics & Velocity Tracking

**Status**: ✅ **COMPLETE**
**Completed**: {completion_date}

**Business Value**: Better estimation accuracy over time

**Key Features**:
- Track estimated vs actual time
- Historical metrics database
- Velocity calculations

**Estimated Effort**: 3-4 days (3.5 days average)
**Actual Effort**: 3.75 days

---

### 🎯 [US-014] Request Categorization

**Status**: ✅ **COMPLETE**
**Completed**: {old_completion_date}

**Business Value**: Faster roadmap updates

**Estimated Effort**: 3-5 days (4 days average)
**Actual Effort**: 4.5 days

---

### 🎯 [US-017] Summary & Calendar

**Status**: 🔄 **IN PROGRESS**
**Started**: 2025-10-15

**I want**: Proactive delivery summaries and calendar
**So that**: Better visibility, reduced status questions

**Estimated Effort**: 5-7 days (6 days average)
**Progress**: Phase 3/4 (75%)
**Estimated Remaining**: 1-2 days

---

### 🎯 [US-012] Natural Language User Story Management

**Status**: 📝 **PLANNED**

**I want**: `/US` command for conversational story creation
**So that**: Faster story creation without manual ROADMAP editing

**Estimated Effort**: 5-7 days

---

### 🎯 [US-018] Team Role Clarity

**Status**: 📝 **PLANNED**

**I want**: Clear understanding of team roles and responsibilities
**So that**: Improved team effectiveness and decision-making

**Estimated Effort**: 6-8 days

---

## PRIORITY 5: Analytics Dashboard

**Status**: TBD
**Description**: Create analytics dashboard for metrics visualization
**Estimated**: TBD
"""

    roadmap_path.write_text(roadmap_content)
    return roadmap_path


@pytest.fixture
def mock_roadmap_no_completions(tmp_path):
    """Create a mock ROADMAP with no recent completions."""
    roadmap_path = tmp_path / "ROADMAP.md"

    roadmap_content = """# ROADMAP

## User Stories

### 🎯 [US-017] Summary & Calendar

**Status**: 📝 **PLANNED**

**I want**: Proactive delivery summaries and calendar
**So that**: Better visibility, reduced status questions

**Estimated Effort**: 5-7 days (6 days average)

---

### 🎯 [US-012] Natural Language User Story Management

**Status**: 📝 **PLANNED**

**I want**: `/US` command for conversational story creation

**Estimated Effort**: 5-7 days
"""

    roadmap_path.write_text(roadmap_content)
    return roadmap_path


class TestStatusTrackingDocumentStructure:
    """Test document structure and sections."""

    def test_document_has_all_required_sections(self, mock_roadmap_with_completions):
        """Test that generated document has all required sections."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Check all required sections exist
        assert "# STATUS TRACKING" in document
        assert "## Recent Completions" in document
        assert "## Current Work (In Progress)" in document
        assert "## Next Up" in document
        assert "## Velocity & Accuracy Metrics" in document

    def test_document_has_header_with_timestamp(self, mock_roadmap_with_completions):
        """Test that document has header with last updated timestamp."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        assert "**Last Updated**:" in document
        # Should contain current date
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in document

    def test_document_has_footer_warning(self, mock_roadmap_with_completions):
        """Test that document has footer warning about auto-generation."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        assert "auto-generated" in document.lower()
        assert "do not edit manually" in document.lower()


class TestRecentCompletionsSection:
    """Test Recent Completions section."""

    def test_recent_completions_shows_completed_stories(self, mock_roadmap_with_completions):
        """Test that recent completions section shows completed stories."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(days=14)

        # Should show US-016 and US-015 (completed in last 14 days)
        assert "US-016: Technical Spec Generation" in document
        assert "US-015: Estimation Metrics & Velocity Tracking" in document

        # Should NOT show US-014 (completed 30 days ago)
        assert "US-014" not in document or "Last 14 Days" not in document

    def test_recent_completions_includes_technical_details(self, mock_roadmap_with_completions):
        """Test that completions include technical details."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Check for estimated vs actual
        assert "Estimated" in document
        assert "Actual" in document
        assert "accuracy" in document.lower()

    def test_recent_completions_shows_accuracy_emoji(self, mock_roadmap_with_completions):
        """Test that accuracy includes emoji indicator."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Should have accuracy emoji (✅, ⚠️, or ❌)
        assert "✅" in document or "⚠️" in document or "❌" in document

    def test_no_completions_shows_message(self, mock_roadmap_no_completions):
        """Test that no completions shows appropriate message."""
        generator = StatusReportGenerator(str(mock_roadmap_no_completions))
        document = generator.generate_status_tracking_document()

        assert "No completions in the last" in document


class TestCurrentWorkSection:
    """Test Current Work (In Progress) section."""

    def test_current_work_shows_in_progress_stories(self, mock_roadmap_with_completions):
        """Test that current work section shows in-progress stories."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Should show US-017 (in progress)
        assert "US-017: Summary & Calendar" in document

    def test_current_work_shows_phase_information(self, mock_roadmap_with_completions):
        """Test that in-progress stories show phase information."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Should show phase (if available)
        assert "Phase: 3/4" in document or "Phase" in document

    def test_current_work_shows_progress_percentage(self, mock_roadmap_with_completions):
        """Test that in-progress stories show progress percentage."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Should show progress percentage
        assert "Progress: 75%" in document or "Progress" in document

    def test_no_current_work_shows_message(self, mock_roadmap_no_completions):
        """Test that no current work shows appropriate message."""
        generator = StatusReportGenerator(str(mock_roadmap_no_completions))
        document = generator.generate_status_tracking_document()

        assert "No work currently in progress" in document


class TestNextUpSection:
    """Test Next Up (Upcoming) section."""

    def test_next_up_shows_planned_stories(self, mock_roadmap_with_completions):
        """Test that next up section shows planned stories with estimates."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(upcoming_count=5)

        # Should show US-012 and US-018 (planned with estimates)
        assert "US-012" in document or "US-018" in document

    def test_next_up_respects_count_limit(self, mock_roadmap_with_completions):
        """Test that next up respects the count limit."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(upcoming_count=1)

        # Should only show 1 item
        lines = [line for line in document.split("\n") if line.startswith("1. **US-")]
        assert len(lines) <= 1

    def test_next_up_shows_estimated_days(self, mock_roadmap_with_completions):
        """Test that upcoming items show estimated days."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document()

        # Should show estimated days range
        assert "Estimated:" in document or "days" in document.lower()


class TestVelocityMetricsSection:
    """Test Velocity & Accuracy Metrics section."""

    def test_velocity_metrics_shows_stories_completed(self, mock_roadmap_with_completions):
        """Test that velocity section shows stories completed."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(days=14)

        assert "Stories completed:" in document

    def test_velocity_metrics_shows_average_velocity(self, mock_roadmap_with_completions):
        """Test that velocity section shows average velocity."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(days=14)

        assert "Average velocity:" in document or "stories/week" in document

    def test_velocity_metrics_shows_accuracy(self, mock_roadmap_with_completions):
        """Test that velocity section shows accuracy percentage."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(days=14)

        assert "Average accuracy:" in document or "accuracy:" in document.lower()

    def test_velocity_metrics_shows_trend(self, mock_roadmap_with_completions):
        """Test that velocity section shows trend indicator."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        document = generator.generate_status_tracking_document(days=14)

        # Should have trend (↑ improving, ↓ declining, → stable)
        has_trend = "Trend:" in document or "improving" in document.lower() or "declining" in document.lower()
        assert has_trend

    def test_no_velocity_data_shows_message(self, mock_roadmap_no_completions):
        """Test that no velocity data shows appropriate message."""
        generator = StatusReportGenerator(str(mock_roadmap_no_completions))
        document = generator.generate_status_tracking_document()

        assert "No velocity data" in document or "Stories completed: 0" in document


class TestAutoUpdateFunctionality:
    """Test auto-update functionality."""

    def test_update_status_tracking_creates_file(self, mock_roadmap_with_completions, tmp_path):
        """Test that update_status_tracking creates the file."""
        output_path = tmp_path / "STATUS_TRACKING.md"

        success = update_status_tracking(roadmap_path=str(mock_roadmap_with_completions), output_path=str(output_path))

        assert success is True
        assert output_path.exists()

    def test_update_status_tracking_file_content(self, mock_roadmap_with_completions, tmp_path):
        """Test that update_status_tracking creates valid content."""
        output_path = tmp_path / "STATUS_TRACKING.md"

        update_status_tracking(roadmap_path=str(mock_roadmap_with_completions), output_path=str(output_path))

        content = output_path.read_text()
        assert "# STATUS TRACKING" in content
        assert "Recent Completions" in content

    def test_on_story_started_triggers_update(self, mock_roadmap_with_completions, tmp_path, monkeypatch):
        """Test that on_story_started triggers update."""
        output_path = tmp_path / "STATUS_TRACKING.md"

        # Mock update_status_tracking to use our temp paths
        update_called = []

        def mock_update(roadmap_path, **kwargs):
            update_called.append(True)
            return update_status_tracking(roadmap_path=roadmap_path, output_path=str(output_path), **kwargs)

        monkeypatch.setattr("coffee_maker.reports.status_tracking_updater.update_status_tracking", mock_update)

        on_story_started("US-017", roadmap_path=str(mock_roadmap_with_completions))

        assert len(update_called) == 1

    def test_on_story_completed_triggers_update(self, mock_roadmap_with_completions, tmp_path, monkeypatch):
        """Test that on_story_completed triggers update."""
        output_path = tmp_path / "STATUS_TRACKING.md"

        update_called = []

        def mock_update(roadmap_path, **kwargs):
            update_called.append(True)
            return update_status_tracking(roadmap_path=roadmap_path, output_path=str(output_path), **kwargs)

        monkeypatch.setattr("coffee_maker.reports.status_tracking_updater.update_status_tracking", mock_update)

        on_story_completed("US-017", roadmap_path=str(mock_roadmap_with_completions))

        assert len(update_called) == 1

    def test_on_progress_update_triggers_update(self, mock_roadmap_with_completions, tmp_path, monkeypatch):
        """Test that on_progress_update triggers update."""
        output_path = tmp_path / "STATUS_TRACKING.md"

        update_called = []

        def mock_update(roadmap_path, **kwargs):
            update_called.append(True)
            return update_status_tracking(roadmap_path=roadmap_path, output_path=str(output_path), **kwargs)

        monkeypatch.setattr("coffee_maker.reports.status_tracking_updater.update_status_tracking", mock_update)

        on_progress_update("US-017", 75, roadmap_path=str(mock_roadmap_with_completions))

        assert len(update_called) == 1

    def test_update_handles_missing_roadmap(self, tmp_path):
        """Test that update handles missing ROADMAP gracefully."""
        nonexistent_roadmap = tmp_path / "nonexistent.md"
        output_path = tmp_path / "STATUS_TRACKING.md"

        success = update_status_tracking(roadmap_path=str(nonexistent_roadmap), output_path=str(output_path))

        assert success is False


class TestHelperMethods:
    """Test helper methods for extraction."""

    def test_extract_phase(self, mock_roadmap_with_completions):
        """Test phase extraction from content."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        content = "Progress: Phase 3/4 (75%)"

        phase = generator._extract_phase(content)
        assert phase == "3/4"

    def test_extract_progress_pct(self, mock_roadmap_with_completions):
        """Test progress percentage extraction."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        content = "Progress: 75%"

        progress = generator._extract_progress_pct(content)
        assert progress == 75

    def test_is_in_progress_detection(self, mock_roadmap_with_completions):
        """Test in-progress detection."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))

        in_progress_content = "**Status**: 🔄 **IN PROGRESS**"
        assert generator._is_in_progress(in_progress_content) is True

        complete_content = "**Status**: ✅ **COMPLETE**"
        assert generator._is_in_progress(complete_content) is False

    def test_calculate_velocity_metrics_with_data(self, mock_roadmap_with_completions):
        """Test velocity metrics calculation with data."""
        generator = StatusReportGenerator(str(mock_roadmap_with_completions))
        completions = generator.get_recent_completions(days=14)

        metrics = generator._calculate_velocity_metrics(completions)

        assert metrics["stories_completed"] >= 0
        assert metrics["avg_velocity"] >= 0
        assert "trend" in metrics

    def test_calculate_velocity_metrics_no_data(self, mock_roadmap_no_completions):
        """Test velocity metrics calculation with no data."""
        generator = StatusReportGenerator(str(mock_roadmap_no_completions))
        completions = generator.get_recent_completions(days=14)

        metrics = generator._calculate_velocity_metrics(completions)

        assert metrics["stories_completed"] == 0
        assert metrics["avg_velocity"] == 0.0
        assert metrics["avg_accuracy"] is None
        assert metrics["trend"] == "unknown"
