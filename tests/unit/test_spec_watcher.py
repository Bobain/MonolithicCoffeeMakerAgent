"""Unit tests for SpecWatcher (US-047 Phase 3).

This module tests the SpecWatcher class which monitors ROADMAP.md for new
priorities that need technical specifications.

Tests:
- New priority detection
- Spec existence checking
- Known priorities tracking
- Spec prefix generation
"""

import pytest
from coffee_maker.autonomous.spec_watcher import SpecWatcher


class TestSpecWatcher:
    """Test SpecWatcher functionality."""

    @pytest.fixture
    def temp_roadmap(self, tmp_path):
        """Create temporary ROADMAP for testing."""
        roadmap_path = tmp_path / "docs" / "roadmap" / "ROADMAP.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)

        # Create specs directory
        specs_dir = tmp_path / "docs" / "architecture" / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)

        # Write initial ROADMAP content
        roadmap_content = """# Coffee Maker ROADMAP

### PRIORITY 1: First Feature ✅ Complete

### PRIORITY 2: Second Feature 📝 Planned
"""
        roadmap_path.write_text(roadmap_content)

        return roadmap_path, specs_dir

    @pytest.fixture
    def spec_watcher(self, temp_roadmap):
        """Create SpecWatcher instance for testing."""
        roadmap_path, specs_dir = temp_roadmap
        watcher = SpecWatcher(roadmap_path=roadmap_path, spec_dir=specs_dir)
        return watcher

    def test_parse_roadmap_extracts_priorities(self, spec_watcher):
        """Test that _parse_roadmap extracts priority names and titles."""
        priorities = spec_watcher._parse_roadmap()

        assert len(priorities) == 2
        assert priorities[0]["name"] == "PRIORITY 1"
        assert priorities[0]["title"] == "First Feature"
        assert priorities[1]["name"] == "PRIORITY 2"
        assert priorities[1]["title"] == "Second Feature"

    def test_parse_roadmap_handles_us_prefix(self, spec_watcher, temp_roadmap):
        """Test parsing priorities with US- prefix."""
        roadmap_path, _ = temp_roadmap

        content = """# ROADMAP

### US-047: Architect-Only Specs 📝 Planned
### US-048: Silent Background Agents 📝 Planned
"""
        roadmap_path.write_text(content)

        priorities = spec_watcher._parse_roadmap()

        assert len(priorities) == 2
        assert priorities[0]["name"] == "US-047"
        assert priorities[0]["title"] == "Architect-Only Specs"
        assert priorities[1]["name"] == "US-048"
        assert priorities[1]["title"] == "Silent Background Agents"

    def test_parse_roadmap_handles_decimal_priorities(self, spec_watcher, temp_roadmap):
        """Test parsing priorities with decimal notation."""
        roadmap_path, _ = temp_roadmap

        content = """# ROADMAP

### PRIORITY 2.5: Mid Priority ✅ Complete
### PRIORITY 2.6: Another Mid Priority 📝 Planned
"""
        roadmap_path.write_text(content)

        priorities = spec_watcher._parse_roadmap()

        assert len(priorities) == 2
        assert priorities[0]["name"] == "PRIORITY 2.5"
        assert priorities[1]["name"] == "PRIORITY 2.6"

    def test_spec_exists_returns_true_when_spec_present(self, spec_watcher, temp_roadmap):
        """Test that _spec_exists returns True when spec file exists."""
        _, specs_dir = temp_roadmap

        # Create spec file
        spec_file = specs_dir / "SPEC-001-first-feature.md"
        spec_file.write_text("# Spec Content")

        priority = {"name": "PRIORITY 1", "title": "First Feature"}

        assert spec_watcher._spec_exists(priority) is True

    def test_spec_exists_returns_false_when_spec_missing(self, spec_watcher):
        """Test that _spec_exists returns False when no spec exists."""
        priority = {"name": "PRIORITY 2", "title": "Second Feature"}

        assert spec_watcher._spec_exists(priority) is False

    def test_get_spec_prefix_for_us_priority(self, spec_watcher):
        """Test spec prefix generation for US- priorities."""
        prefix = spec_watcher._get_spec_prefix("US-047")
        assert prefix == "SPEC-047"

        prefix = spec_watcher._get_spec_prefix("US-123")
        assert prefix == "SPEC-123"

    def test_get_spec_prefix_for_priority_number(self, spec_watcher):
        """Test spec prefix generation for PRIORITY X."""
        prefix = spec_watcher._get_spec_prefix("PRIORITY 1")
        assert prefix == "SPEC-001"

        prefix = spec_watcher._get_spec_prefix("PRIORITY 12")
        assert prefix == "SPEC-012"

    def test_get_spec_prefix_for_decimal_priority(self, spec_watcher):
        """Test spec prefix generation for PRIORITY X.Y."""
        prefix = spec_watcher._get_spec_prefix("PRIORITY 2.5")
        assert prefix == "SPEC-002-5"

        prefix = spec_watcher._get_spec_prefix("PRIORITY 10.3")
        assert prefix == "SPEC-010-3"

    def test_check_for_new_priorities_detects_missing_specs(self, spec_watcher, temp_roadmap):
        """Test that check_for_new_priorities detects new priorities without specs."""
        roadmap_path, specs_dir = temp_roadmap

        # Add new priority to ROADMAP
        content = roadmap_path.read_text()
        content += "\n### PRIORITY 3: Third Feature 📝 Planned\n"
        roadmap_path.write_text(content)

        # Run check
        missing = spec_watcher.check_for_new_priorities()

        # Should detect all 3 priorities as new (none have specs)
        assert len(missing) >= 1
        priority_names = [p["name"] for p in missing]
        assert "PRIORITY 3" in priority_names

    def test_check_for_new_priorities_ignores_priorities_with_specs(self, spec_watcher, temp_roadmap):
        """Test that priorities with existing specs are not flagged."""
        roadmap_path, specs_dir = temp_roadmap

        # Create spec for PRIORITY 1
        spec_file = specs_dir / "SPEC-001-first-feature.md"
        spec_file.write_text("# Spec")

        # Add new priority without spec
        content = roadmap_path.read_text()
        content += "\n### PRIORITY 3: Third Feature 📝 Planned\n"
        roadmap_path.write_text(content)

        # Run check
        missing = spec_watcher.check_for_new_priorities()

        # PRIORITY 1 has spec, should not be in missing list
        # PRIORITY 2 and 3 don't have specs, should be in list
        priority_names = [p["name"] for p in missing]
        assert "PRIORITY 1" not in priority_names
        assert "PRIORITY 2" in priority_names or "PRIORITY 3" in priority_names

    def test_check_for_new_priorities_tracks_known_priorities(self, spec_watcher, temp_roadmap):
        """Test that known priorities are not re-reported."""
        roadmap_path, _ = temp_roadmap

        # First check - all priorities are new
        missing1 = spec_watcher.check_for_new_priorities()
        len(missing1)

        # Second check - no new priorities added
        missing2 = spec_watcher.check_for_new_priorities()

        # Should not re-report same priorities
        assert len(missing2) == 0

        # Add truly new priority
        content = roadmap_path.read_text()
        content += "\n### PRIORITY 4: Fourth Feature 📝 Planned\n"
        roadmap_path.write_text(content)

        # Third check - should only report PRIORITY 4
        missing3 = spec_watcher.check_for_new_priorities()
        assert len(missing3) == 1
        assert missing3[0]["name"] == "PRIORITY 4"

    def test_reset_known_priorities(self, spec_watcher):
        """Test that reset_known_priorities clears tracking."""
        # First check - populate known priorities
        spec_watcher.check_for_new_priorities()
        initial_count = spec_watcher.get_known_priorities_count()
        assert initial_count > 0

        # Reset
        spec_watcher.reset_known_priorities()

        # Count should be zero
        assert spec_watcher.get_known_priorities_count() == 0

    def test_get_known_priorities_count(self, spec_watcher):
        """Test get_known_priorities_count returns correct count."""
        assert spec_watcher.get_known_priorities_count() == 0

        spec_watcher.check_for_new_priorities()
        count = spec_watcher.get_known_priorities_count()

        # Should have tracked the priorities
        assert count >= 2  # At least PRIORITY 1 and 2 from fixture

    def test_handles_empty_roadmap(self, spec_watcher, temp_roadmap):
        """Test behavior with empty ROADMAP."""
        roadmap_path, _ = temp_roadmap
        roadmap_path.write_text("# Empty ROADMAP\n")

        missing = spec_watcher.check_for_new_priorities()
        assert missing == []

    def test_handles_missing_roadmap_file(self, tmp_path):
        """Test behavior when ROADMAP file doesn't exist."""
        roadmap_path = tmp_path / "nonexistent" / "ROADMAP.md"
        watcher = SpecWatcher(roadmap_path=roadmap_path)

        missing = watcher.check_for_new_priorities()
        assert missing == []

    def test_handles_missing_specs_directory(self, temp_roadmap):
        """Test behavior when specs directory doesn't exist."""
        roadmap_path, specs_dir = temp_roadmap

        # Remove specs directory
        import shutil

        shutil.rmtree(specs_dir)

        watcher = SpecWatcher(roadmap_path=roadmap_path, spec_dir=specs_dir)
        missing = watcher.check_for_new_priorities()

        # All priorities should be missing specs
        assert len(missing) >= 2

    def test_spec_prefix_in_result(self, spec_watcher):
        """Test that check_for_new_priorities includes spec_prefix in results."""
        missing = spec_watcher.check_for_new_priorities()

        if len(missing) > 0:
            priority = missing[0]
            assert "spec_prefix" in priority
            assert priority["spec_prefix"].startswith("SPEC-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
