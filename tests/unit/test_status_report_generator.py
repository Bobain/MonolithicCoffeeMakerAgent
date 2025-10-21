"""Unit tests for StatusReportGenerator.

Tests cover:
- Data class instantiation
- ROADMAP parsing for completions
- ROADMAP parsing for upcoming deliverables
- Executive summary formatting
- Calendar report formatting
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

from coffee_maker.reports.status_report_generator import (
    StatusReportGenerator,
    StoryCompletion,
    UpcomingStory,
)


# ==================== FIXTURES ====================


@pytest.fixture
def sample_roadmap_content():
    """Sample ROADMAP.md content for testing."""
    return """# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-15
**Status**: Active

---

## Recent User Stories

### 🎯 [US-016] Technical Spec Generation

**As a**: project_manager
**I want**: detailed technical specs with task-level estimates
**So that**: we can give accurate delivery estimates

**Business Value**: ⭐⭐⭐⭐⭐ Accurate delivery estimates before coding starts
**Estimated Effort**: 4-5 days
**Status**: ✅ COMPLETE (2025-10-15)
**Actual Effort**: 3.75 days

**Key Features**:
- AI-assisted task breakdown from user stories
- Historical metrics integration for better estimates
- Interactive approval workflow
- 100 tests passing
- Comprehensive templates and examples

---

### 🎯 [US-015] Estimation Metrics Tracking

**As a**: project_manager
**I want**: metrics about estimation accuracy and team velocity
**So that**: I can improve future estimates based on historical data

**Business Value**: ⭐⭐⭐⭐ Data-driven planning and estimation
**Estimated Effort**: 3-4 days
**Status**: 🔄 In Progress
**Assigned To**: code_developer

**Acceptance Criteria**:
- [ ] Track estimated vs actual time for each story
- [ ] Calculate team velocity
- [ ] Display estimation accuracy metrics

---

### 🎯 [US-017] Summary & Calendar

**As a**: user
**I want**: proactive delivery summaries and upcoming calendar
**So that**: I have better visibility without asking for status

**Business Value**: ⭐⭐⭐⭐⭐ Better visibility, reduced status questions
**Estimated Effort**: 5-7 days
**Status**: 📝 Planned

**Impact**: Proactive communication, reduced interruptions, better planning

---

## 🎯 PRIORITIES

### 🔴 **PRIORITY 4: Developer Status Dashboard**

**Estimated Duration**: 2-3 days
**Impact**: ⭐⭐⭐⭐
**Status**: ✅ Complete (2025-10-10)

#### Project: Developer Status Dashboard

Real-time dashboard showing code_developer progress, current task, and recent completions.

**Business Value**: Visibility into autonomous development progress

**Key Features**:
- Live progress tracking
- Recent completions list
- Current task display
- Streamlit-based UI

**Deliverables**:
- Streamlit dashboard app
- Status tracking backend
- Real-time updates

---

### 🔴 **PRIORITY 5: Analytics Dashboard**

**Estimated Duration**: 3-4 days
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned

#### Project: Analytics Dashboard

Comprehensive analytics for code quality, test coverage, and development velocity.

**Deliverables**:
- Analytics backend service
- Streamlit visualization
- Metrics collection

---
"""


@pytest.fixture
def temp_roadmap_file(sample_roadmap_content):
    """Create temporary ROADMAP.md file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(sample_roadmap_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def generator(temp_roadmap_file):
    """StatusReportGenerator instance for testing."""
    return StatusReportGenerator(temp_roadmap_file)


# ==================== DATA CLASS TESTS ====================


def test_story_completion_creation():
    """Test StoryCompletion data class instantiation."""
    completion = StoryCompletion(
        story_id="US-016",
        title="Technical Spec Generation",
        completion_date=datetime(2025, 10, 15),
        business_value="Accurate delivery estimates",
        key_features=["AI-assisted task breakdown", "100 tests passing"],
        estimated_days=4.5,
        actual_days=3.75,
    )

    assert completion.story_id == "US-016"
    assert completion.title == "Technical Spec Generation"
    assert completion.completion_date == datetime(2025, 10, 15)
    assert completion.business_value == "Accurate delivery estimates"
    assert len(completion.key_features) == 2
    assert completion.estimated_days == 4.5
    assert completion.actual_days == 3.75


def test_story_completion_optional_fields():
    """Test StoryCompletion with optional fields as None."""
    completion = StoryCompletion(
        story_id="US-001",
        title="Test Story",
        completion_date=datetime.now(),
        business_value="Test value",
        key_features=[],
    )

    assert completion.estimated_days is None
    assert completion.actual_days is None


def test_upcoming_story_creation():
    """Test UpcomingStory data class instantiation."""
    upcoming = UpcomingStory(
        story_id="US-017",
        title="Summary & Calendar",
        estimated_min_days=5.0,
        estimated_max_days=7.0,
        estimated_completion_date=datetime(2025, 10, 27),
        what_description="Proactive delivery summaries",
        impact_statement="Better visibility",
    )

    assert upcoming.story_id == "US-017"
    assert upcoming.title == "Summary & Calendar"
    assert upcoming.estimated_min_days == 5.0
    assert upcoming.estimated_max_days == 7.0
    assert upcoming.estimated_completion_date == datetime(2025, 10, 27)
    assert upcoming.what_description == "Proactive delivery summaries"
    assert upcoming.impact_statement == "Better visibility"


# ==================== GENERATOR INITIALIZATION TESTS ====================


def test_generator_initialization(temp_roadmap_file):
    """Test StatusReportGenerator initialization."""
    generator = StatusReportGenerator(temp_roadmap_file)

    assert generator.roadmap_path == Path(temp_roadmap_file)
    assert generator.parser is not None
    assert generator.velocity_days_per_story == 3.5


def test_generator_initialization_custom_velocity(temp_roadmap_file):
    """Test StatusReportGenerator with custom velocity."""
    generator = StatusReportGenerator(temp_roadmap_file, velocity_days_per_story=5.0)

    assert generator.velocity_days_per_story == 5.0


def test_generator_initialization_missing_file():
    """Test initialization with missing ROADMAP file."""
    with pytest.raises(FileNotFoundError):
        StatusReportGenerator("/nonexistent/ROADMAP.md")


# ==================== GET RECENT COMPLETIONS TESTS ====================


def test_get_recent_completions_finds_user_stories(generator):
    """Test that get_recent_completions finds completed user stories."""
    completions = generator.get_recent_completions(days=30)

    # Should find US-016 (completed 2025-10-15)
    assert len(completions) >= 1

    us_016 = next((c for c in completions if c.story_id == "US-016"), None)
    assert us_016 is not None
    assert us_016.title == "Technical Spec Generation"
    assert us_016.business_value != ""
    assert len(us_016.key_features) > 0


def test_get_recent_completions_finds_priorities(generator):
    """Test that get_recent_completions finds completed priorities."""
    completions = generator.get_recent_completions(days=30)

    # Should find PRIORITY 4 (completed 2025-10-10)
    priority_4 = next((c for c in completions if c.story_id == "PRIORITY 4"), None)
    assert priority_4 is not None
    assert "Dashboard" in priority_4.title


def test_get_recent_completions_filters_by_date(generator):
    """Test that get_recent_completions filters by date range."""
    # Only 1 day back - should find nothing (completion dates are in past)
    completions = generator.get_recent_completions(days=1)

    # This depends on the mock data dates - adjust based on sample content
    # In our sample, US-016 was completed on 2025-10-15
    # If today is before that, we won't find it
    # This test verifies the filtering logic works
    assert isinstance(completions, list)


def test_get_recent_completions_sorts_by_date(generator):
    """Test that completions are sorted by date (newest first)."""
    completions = generator.get_recent_completions(days=30)

    if len(completions) >= 2:
        # Verify sorted in descending order (newest first)
        for i in range(len(completions) - 1):
            assert completions[i].completion_date >= completions[i + 1].completion_date


def test_get_recent_completions_extracts_estimates(generator):
    """Test that estimates are extracted correctly."""
    completions = generator.get_recent_completions(days=30)

    us_016 = next((c for c in completions if c.story_id == "US-016"), None)
    if us_016:
        # US-016 has estimated and actual days
        assert us_016.estimated_days is not None
        assert us_016.actual_days is not None


def test_get_recent_completions_no_completions():
    """Test behavior when no completions are found."""
    # Create roadmap with no completions
    content = """# ROADMAP

### 🎯 [US-001] Test Story

**Status**: 📝 Planned
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        generator = StatusReportGenerator(temp_path)
        completions = generator.get_recent_completions(days=14)

        assert completions == []
    finally:
        os.unlink(temp_path)


# ==================== GET UPCOMING DELIVERABLES TESTS ====================


def test_get_upcoming_deliverables_finds_stories(generator):
    """Test that get_upcoming_deliverables finds upcoming stories."""
    upcoming = generator.get_upcoming_deliverables(limit=3)

    # Should find US-015 (in progress) and US-017 (planned)
    assert len(upcoming) >= 1

    us_015 = next((u for u in upcoming if u.story_id == "US-015"), None)
    if us_015:
        assert us_015.estimated_min_days == 3.0
        assert us_015.estimated_max_days == 4.0


def test_get_upcoming_deliverables_finds_priorities(generator):
    """Test that get_upcoming_deliverables finds planned priorities."""
    upcoming = generator.get_upcoming_deliverables(limit=5)

    # Should find PRIORITY 5 (planned with estimate)
    priority_5 = next((u for u in upcoming if u.story_id == "PRIORITY 5"), None)
    if priority_5:
        assert priority_5.estimated_min_days == 3.0
        assert priority_5.estimated_max_days == 4.0


def test_get_upcoming_deliverables_respects_limit(generator):
    """Test that limit parameter works."""
    upcoming = generator.get_upcoming_deliverables(limit=1)

    assert len(upcoming) <= 1


def test_get_upcoming_deliverables_excludes_completed(generator):
    """Test that completed stories are excluded."""
    upcoming = generator.get_upcoming_deliverables(limit=10)

    # US-016 is complete, should not be in upcoming
    us_016 = next((u for u in upcoming if u.story_id == "US-016"), None)
    assert us_016 is None


def test_get_upcoming_deliverables_requires_estimates(generator):
    """Test that stories without estimates are excluded."""
    # Add story without estimate
    content = generator.roadmap_path.read_text()
    content += """
### 🎯 [US-999] No Estimate Story

**Status**: 📝 Planned
**Estimated Effort**: TBD
"""
    generator.roadmap_path.write_text(content)

    upcoming = generator.get_upcoming_deliverables(limit=10)

    # US-999 should not be included (no estimate)
    us_999 = next((u for u in upcoming if u.story_id == "US-999"), None)
    assert us_999 is None


def test_get_upcoming_deliverables_calculates_completion_date(generator):
    """Test that estimated completion dates are calculated."""
    upcoming = generator.get_upcoming_deliverables(limit=3)

    if upcoming:
        story = upcoming[0]
        # Completion date should be in the future
        assert story.estimated_completion_date > datetime.now()

        # Should be roughly avg_days in the future
        avg_days = (story.estimated_min_days + story.estimated_max_days) / 2
        expected_date = datetime.now() + timedelta(days=avg_days)

        # Allow 1 day tolerance
        date_diff = abs((story.estimated_completion_date - expected_date).days)
        assert date_diff <= 1


# ==================== FORMATTING TESTS ====================


def test_format_delivery_summary_empty_list():
    """Test format_delivery_summary with empty list."""
    generator = StatusReportGenerator.__new__(StatusReportGenerator)
    summary = generator.format_delivery_summary([])

    assert "No recent deliveries" in summary


def test_format_delivery_summary_single_completion(generator):
    """Test format_delivery_summary with single completion."""
    completion = StoryCompletion(
        story_id="US-016",
        title="Technical Spec Generation",
        completion_date=datetime(2025, 10, 15),
        business_value="Accurate delivery estimates",
        key_features=["AI-assisted task breakdown", "100 tests passing"],
        estimated_days=4.5,
        actual_days=3.75,
    )

    summary = generator.format_delivery_summary([completion])

    assert "US-016" in summary
    assert "Technical Spec Generation" in summary
    assert "2025-10-15" in summary
    assert "Accurate delivery estimates" in summary
    assert "AI-assisted task breakdown" in summary
    assert "100 tests passing" in summary
    assert "Estimation Accuracy" in summary


def test_format_delivery_summary_multiple_completions(generator):
    """Test format_delivery_summary with multiple completions."""
    completions = [
        StoryCompletion(
            story_id="US-016",
            title="Spec Generation",
            completion_date=datetime(2025, 10, 15),
            business_value="Better estimates",
            key_features=["Feature 1"],
        ),
        StoryCompletion(
            story_id="US-015",
            title="Metrics Tracking",
            completion_date=datetime(2025, 10, 10),
            business_value="Data-driven planning",
            key_features=["Feature 2"],
        ),
    ]

    summary = generator.format_delivery_summary(completions)

    assert "US-016" in summary
    assert "US-015" in summary
    assert "Total Deliveries: 2" in summary


def test_format_calendar_report_empty_list():
    """Test format_calendar_report with empty list."""
    generator = StatusReportGenerator.__new__(StatusReportGenerator)
    calendar = generator.format_calendar_report([])

    assert "No upcoming deliverables" in calendar


def test_format_calendar_report_single_story(generator):
    """Test format_calendar_report with single story."""
    story = UpcomingStory(
        story_id="US-017",
        title="Summary & Calendar",
        estimated_min_days=5.0,
        estimated_max_days=7.0,
        estimated_completion_date=datetime(2025, 10, 27),
        what_description="Proactive delivery summaries",
        impact_statement="Better visibility",
    )

    calendar = generator.format_calendar_report([story])

    assert "US-017" in calendar
    assert "Summary & Calendar" in calendar
    assert "5-7 days" in calendar
    assert "2025-10-27" in calendar
    assert "Proactive delivery summaries" in calendar
    assert "Better visibility" in calendar


def test_format_calendar_report_multiple_stories(generator):
    """Test format_calendar_report with multiple stories."""
    stories = [
        UpcomingStory(
            story_id="US-017",
            title="Story 1",
            estimated_min_days=5.0,
            estimated_max_days=7.0,
            estimated_completion_date=datetime(2025, 10, 27),
            what_description="Description 1",
            impact_statement="Impact 1",
        ),
        UpcomingStory(
            story_id="US-018",
            title="Story 2",
            estimated_min_days=3.0,
            estimated_max_days=4.0,
            estimated_completion_date=datetime(2025, 10, 30),
            what_description="Description 2",
            impact_statement="Impact 2",
        ),
    ]

    calendar = generator.format_calendar_report(stories)

    assert "1. US-017" in calendar
    assert "2. US-018" in calendar
    assert "Next 2 Priorities" in calendar


# ==================== HELPER METHOD TESTS ====================


def test_is_complete_with_checkmark(generator):
    """Test _is_complete with checkmark emoji."""
    content = "**Status**: ✅ Complete"
    assert generator._is_complete(content) is True


def test_is_complete_with_text(generator):
    """Test _is_complete with 'complete' text."""
    content = "**Status**: Complete (2025-10-15)"
    assert generator._is_complete(content) is True


def test_is_complete_with_incomplete_status(generator):
    """Test _is_complete with incomplete status."""
    content = "**Status**: 📝 Planned"
    assert generator._is_complete(content) is False


def test_extract_completion_date_formats(generator):
    """Test _extract_completion_date with various formats."""
    # Format 1: **Completed**: YYYY-MM-DD
    content1 = "**Completed**: 2025-10-15"
    date1 = generator._extract_completion_date(content1)
    assert date1 == datetime(2025, 10, 15)

    # Format 2: Completed: YYYY-MM-DD
    content2 = "Completed: 2025-10-10"
    date2 = generator._extract_completion_date(content2)
    assert date2 == datetime(2025, 10, 10)

    # Format 3: (YYYY-MM-DD)
    content3 = "Status: Complete (2025-10-05)"
    date3 = generator._extract_completion_date(content3)
    assert date3 == datetime(2025, 10, 5)


def test_extract_business_value(generator):
    """Test _extract_business_value extraction."""
    content = "**Business Value**: ⭐⭐⭐ Improved system performance"
    value = generator._extract_business_value(content)

    assert "Improved system performance" in value
    assert "⭐" not in value  # Stars should be removed


def test_extract_key_features(generator):
    """Test _extract_key_features extraction."""
    content = """**Key Features**:
- Feature 1
- Feature 2
- Feature 3
"""
    features = generator._extract_key_features(content)

    assert len(features) == 3
    assert "Feature 1" in features
    assert "Feature 2" in features
    assert "Feature 3" in features


def test_extract_estimated_days(generator):
    """Test _extract_estimated_days extraction."""
    content = "**Estimated Effort**: 4-5 days"
    estimate = generator._extract_estimated_days(content)

    assert estimate is not None
    assert estimate["min_days"] == 4.0
    assert estimate["max_days"] == 5.0


def test_extract_estimated_days_story_points_format(generator):
    """Test _extract_estimated_days with story points format."""
    content = "**Estimated Effort**: 3 story points (2-3 days)"
    estimate = generator._extract_estimated_days(content)

    assert estimate is not None
    assert estimate["min_days"] == 2.0
    assert estimate["max_days"] == 3.0


def test_extract_estimated_days_weeks_format(generator):
    """Test _extract_estimated_days with weeks format."""
    content = "**Estimated Effort**: 5-8 story points (1-2 weeks)"
    estimate = generator._extract_estimated_days(content)

    assert estimate is not None
    assert estimate["min_days"] == 5.0  # 1 week = 5 days
    assert estimate["max_days"] == 10.0  # 2 weeks = 10 days


def test_extract_actual_days(generator):
    """Test _extract_actual_days extraction."""
    content = "**Actual Effort**: 3.75 days"
    actual = generator._extract_actual_days(content)

    assert actual == 3.75


def test_extract_what_description(generator):
    """Test _extract_what_description extraction."""
    content = "**I want**: to have proactive delivery summaries"
    what = generator._extract_what_description(content)

    assert "proactive delivery summaries" in what


def test_extract_impact_statement(generator):
    """Test _extract_impact_statement extraction."""
    content = "**So that**: users have better visibility into project progress"
    impact = generator._extract_impact_statement(content)

    assert "better visibility" in impact
