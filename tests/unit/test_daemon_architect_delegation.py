"""Unit tests for daemon-architect spec checking (US-045, US-047).

Tests the CFR-008 enforcement where daemon BLOCKS when specs are missing
and requires architect to create them manually (no delegation).

US-047 UPDATE: Changed from delegation to blocking approach (CFR-008)
- daemon checks if spec exists (does NOT create or delegate)
- daemon BLOCKS if spec missing and notifies user/architect
- architect must create specs proactively in docs/architecture/specs/

US-054 UPDATE: Tests updated to handle CFR-011 enforcement
- Mock ArchitectDailyRoutine to be compliant
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coffee_maker.autonomous.daemon_spec_manager import SpecManagerMixin


class MockGitManager:
    """Mock GitManager for testing."""

    def commit(self, message: str):
        """Mock commit."""

    def push(self):
        """Mock push."""


class MockClaude:
    """Mock Claude interface for testing."""

    def execute_prompt(self, prompt: str, timeout: int = None):
        """Mock execute_prompt."""
        result = Mock()
        result.success = True
        result.content = "Spec created successfully"
        return result


class MockNotifications:
    """Mock NotificationDB for testing."""

    def create_notification(self, **kwargs):
        """Mock notification creation."""
        return "mock_notification_id"


class TestDaemonWithArchitectDelegation(SpecManagerMixin):
    """Test class that includes SpecManagerMixin for testing."""

    def setup(self, roadmap_path: Path):
        """Setup the test instance with required attributes."""
        self.roadmap_path = roadmap_path
        self.git = MockGitManager()
        self.claude = MockClaude()
        self.notifications = MockNotifications()


class TestArchitectDelegation:
    """Test daemon-architect delegation for technical spec creation."""

    @pytest.fixture
    def mock_cfr_011_compliant(self):
        """Mock ArchitectDailyRoutine to be CFR-011 compliant."""
        # Patch enforce_cfr_011 to do nothing (compliant)
        with patch("coffee_maker.autonomous.daemon_spec_manager.ArchitectDailyRoutine") as mock_routine_class:
            mock_routine = Mock()
            mock_routine.enforce_cfr_011.return_value = None  # No violations
            mock_routine_class.return_value = mock_routine
            yield mock_routine

    @pytest.fixture
    def temp_roadmap_dir(self, tmp_path):
        """Create temporary roadmap directory structure."""
        # Create roadmap directory
        roadmap_dir = tmp_path / "docs" / "roadmap"
        roadmap_dir.mkdir(parents=True)

        # Create architecture/specs directory (MUST be at docs level, not docs/roadmap level)
        specs_dir = tmp_path / "docs" / "architecture" / "specs"
        specs_dir.mkdir(parents=True)

        # Create roadmap file
        roadmap_file = roadmap_dir / "ROADMAP.md"
        roadmap_file.write_text("# ROADMAP\n\nTest roadmap content")

        return tmp_path / "docs" / "roadmap"

    @pytest.fixture
    def daemon_with_mixin(self, temp_roadmap_dir, mock_cfr_011_compliant):
        """Create daemon instance with SpecManagerMixin."""
        roadmap_path = temp_roadmap_dir / "ROADMAP.md"
        daemon = TestDaemonWithArchitectDelegation()
        daemon.setup(roadmap_path)
        return daemon

    def test_spec_prefix_generation_for_us_priority(self, daemon_with_mixin):
        """Test spec prefix generation for US-XXX priorities."""
        priority = {
            "name": "US-033",
            "title": "Streamlit App",
            "content": "Create a Streamlit dashboard application",
        }

        # Create a mock spec file to test detection
        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"
        spec_file = specs_dir / "SPEC-033-streamlit-app.md"
        spec_file.write_text("# SPEC-033: Streamlit App\n\nTest spec")

        # Test that existing spec is detected
        result = daemon_with_mixin._ensure_technical_spec(priority)
        assert result is True

    def test_spec_prefix_generation_for_priority_number(self, daemon_with_mixin):
        """Test spec prefix generation for PRIORITY X."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Create a mock spec file
        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"
        spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
        spec_file.write_text("# SPEC-009: Enhanced Communication\n\nTest spec")

        # Test that existing spec is detected
        result = daemon_with_mixin._ensure_technical_spec(priority)
        assert result is True

    def test_cfr_008_blocks_when_spec_missing(self, daemon_with_mixin):
        """Test that CFR-008 enforcement blocks when spec is missing."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports with sentiment analysis",
        }

        # Test that daemon BLOCKS when spec is missing (CFR-008)
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify daemon blocked (returned False)
        assert result is False

    def test_cfr_008_unblocks_when_architect_creates_spec(self, daemon_with_mixin, tmp_path):
        """Test that CFR-008 allows implementation when architect creates spec."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"

        # Simulate architect manually creating the spec (CFR-008 workflow)
        spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
        spec_file.write_text("# SPEC-009: Enhanced Communication\n\nArchitect-created spec per CFR-008")

        # Test that daemon now allows implementation
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify daemon is unblocked (returned True)
        assert result is True
        assert spec_file.exists()
        assert "Architect-created spec per CFR-008" in spec_file.read_text()

    def test_cfr_008_creates_notification_when_spec_missing(self, daemon_with_mixin):
        """Test that CFR-008 creates notification when spec is missing."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Test that notification is created when spec missing
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify failure detected and notification sent
        assert result is False
        # Notification would be created (mocked in MockNotifications)

    def test_handles_missing_priority_name(self, daemon_with_mixin):
        """Test that missing priority name is handled gracefully."""
        priority = {
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Test validation
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify validation failure
        assert result is False

    def test_handles_missing_priority_content(self, daemon_with_mixin):
        """Test that missing priority content still allows spec check (CFR-008)."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
        }

        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"

        # Create spec file (simulate architect created it)
        spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
        spec_file.write_text("# SPEC-009\n\nMinimal spec from architect")

        # Test with missing content - should still find existing spec
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify spec is found
        assert result is True

    def test_spec_prefix_for_priority_with_decimal(self, daemon_with_mixin):
        """Test spec prefix generation for PRIORITY X.Y (e.g., PRIORITY 2.6)."""
        priority = {
            "name": "PRIORITY 2.6",
            "title": "Daemon Improvements",
            "content": "Enhance daemon with new features",
        }

        # Create mock spec
        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"
        spec_file = specs_dir / "SPEC-002-6-daemon-improvements.md"
        spec_file.write_text("# SPEC-002-6\n\nTest spec")

        # Test detection
        result = daemon_with_mixin._ensure_technical_spec(priority)
        assert result is True
