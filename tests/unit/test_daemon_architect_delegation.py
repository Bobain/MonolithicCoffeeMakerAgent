"""Unit tests for daemon-architect delegation (US-045).

Tests the delegation of technical specification creation from the daemon
to the architect agent, ensuring proper ownership boundaries are respected.
"""

import logging
from pathlib import Path
from unittest.mock import Mock

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


class TestDaemonWithArchitectDelegation(SpecManagerMixin):
    """Test class that includes SpecManagerMixin for testing."""

    def __init__(self, roadmap_path: Path):
        self.roadmap_path = roadmap_path
        self.git = MockGitManager()
        self.claude = MockClaude()


class TestArchitectDelegation:
    """Test daemon-architect delegation for technical spec creation."""

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
    def daemon_with_mixin(self, temp_roadmap_dir):
        """Create daemon instance with SpecManagerMixin."""
        roadmap_path = temp_roadmap_dir / "ROADMAP.md"
        return TestDaemonWithArchitectDelegation(roadmap_path)

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

    def test_delegation_prompt_contains_architect_invocation(self, daemon_with_mixin):
        """Test that delegation prompt explicitly requests architect invocation."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports with sentiment analysis",
        }

        prompt = daemon_with_mixin._build_architect_delegation_prompt(priority, "SPEC-009")

        # Verify prompt structure
        assert "DELEGATION TO ARCHITECT AGENT" in prompt
        assert "architect" in prompt.lower()
        assert "PRIORITY 9" in prompt
        assert "Enhanced Communication" in prompt
        assert "docs/architecture/specs" in prompt
        assert "SPEC-009" in prompt

    def test_delegation_creates_spec_via_architect(self, daemon_with_mixin, tmp_path):
        """Test that delegation results in spec creation in architect's directory."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"

        # Mock Claude to simulate architect creating the spec
        original_execute = daemon_with_mixin.claude.execute_prompt

        def mock_execute_with_spec_creation(prompt, timeout=None):
            # Simulate architect creating the spec file
            spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
            spec_file.write_text("# SPEC-009: Enhanced Communication\n\nArchitect-created spec")
            result = Mock()
            result.success = True
            result.content = "Spec created by architect"
            return result

        daemon_with_mixin.claude.execute_prompt = mock_execute_with_spec_creation

        # Test delegation
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify spec was created
        assert result is True
        spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
        assert spec_file.exists()
        assert "Architect-created spec" in spec_file.read_text()

        # Restore original method
        daemon_with_mixin.claude.execute_prompt = original_execute

    def test_delegation_fails_if_architect_doesnt_create_spec(self, daemon_with_mixin):
        """Test that delegation fails if architect doesn't create the spec file."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Mock Claude to simulate successful execution but no file creation
        daemon_with_mixin.claude.execute_prompt = Mock(return_value=Mock(success=True, content="Completed but no file"))

        # Test delegation failure
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify failure is detected
        assert result is False

    def test_delegation_handles_claude_error(self, daemon_with_mixin):
        """Test that delegation handles Claude execution errors gracefully."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Implement daily standup reports",
        }

        # Mock Claude to simulate error
        daemon_with_mixin.claude.execute_prompt = Mock(return_value=Mock(success=False, error="API timeout"))

        # Test error handling
        result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify error is handled
        assert result is False

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

    def test_handles_missing_priority_content(self, daemon_with_mixin, caplog):
        """Test that missing priority content is handled with warning."""
        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
        }

        # Use parent.parent to go from docs/roadmap/ROADMAP.md to docs/
        specs_dir = daemon_with_mixin.roadmap_path.parent.parent / "architecture" / "specs"

        # Mock Claude to simulate spec creation
        def mock_execute_with_spec_creation(prompt, timeout=None):
            spec_file = specs_dir / "SPEC-009-enhanced-communication.md"
            spec_file.write_text("# SPEC-009\n\nMinimal spec")
            result = Mock()
            result.success = True
            return result

        daemon_with_mixin.claude.execute_prompt = mock_execute_with_spec_creation

        # Test with missing content
        with caplog.at_level(logging.WARNING):
            result = daemon_with_mixin._ensure_technical_spec(priority)

        # Verify warning is logged
        assert result is True
        assert any("no content" in record.message.lower() for record in caplog.records)

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


class TestDeprecatedSpecCreationPrompt:
    """Test deprecated _build_spec_creation_prompt method."""

    @pytest.fixture
    def daemon_with_mixin(self, tmp_path):
        """Create daemon instance with SpecManagerMixin."""
        roadmap_dir = tmp_path / "docs" / "roadmap"
        roadmap_dir.mkdir(parents=True)

        specs_dir = tmp_path / "docs" / "architecture" / "specs"
        specs_dir.mkdir(parents=True)

        roadmap_file = roadmap_dir / "ROADMAP.md"
        roadmap_file.write_text("# ROADMAP\n\nTest roadmap")

        return TestDaemonWithArchitectDelegation(roadmap_file)

    def test_deprecated_method_still_works(self, daemon_with_mixin):
        """Test that deprecated _build_spec_creation_prompt still works for backwards compatibility."""
        priority = {
            "name": "US-033",
            "title": "Streamlit App",
            "content": "Create a Streamlit dashboard application",
        }

        # Test deprecated method
        prompt = daemon_with_mixin._build_spec_creation_prompt(priority, "US-033_TECHNICAL_SPEC.md")

        # Verify prompt is generated (method should still work)
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
