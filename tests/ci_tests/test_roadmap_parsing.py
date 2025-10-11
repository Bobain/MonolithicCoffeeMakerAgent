"""Tests for ROADMAP.md parsing functionality.

These tests verify the RoadmapParser correctly extracts priorities,
status, deliverables, and other information from the ROADMAP.
"""

from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestRoadmapParsing:
    """Test ROADMAP parsing functionality."""

    def test_parser_loads_real_roadmap(self):
        """Verify parser can load the actual ROADMAP.md."""
        parser = RoadmapParser("docs/ROADMAP.md")
        assert parser is not None
        assert parser.content is not None
        assert len(parser.content) > 0

    def test_parser_finds_priorities(self):
        """Verify parser extracts priorities from ROADMAP."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()

        assert len(priorities) > 0
        # Each priority should have required fields
        for p in priorities:
            assert "name" in p
            assert "number" in p
            assert "title" in p
            assert "status" in p
            assert "content" in p

    def test_parser_priority_names_format(self, tmp_path):
        """Verify priority names follow expected format."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: First Task** 📝 Planned

**Status**: 📝 Planned

Task content

### 🔴 **PRIORITY 2.5: Sub Priority** 🔄 In Progress

**Status**: 🔄 In Progress

More content
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert len(priorities) == 2
        assert priorities[0]["name"] == "PRIORITY 1"
        assert priorities[1]["name"] == "PRIORITY 2.5"

    def test_parser_extracts_status(self, tmp_path):
        """Verify parser correctly extracts status from priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Planned Task** 📝 Planned

**Status**: 📝 Planned

Content

### 🔴 **PRIORITY 2: In Progress Task** 🔄 In Progress

**Status**: 🔄 In Progress

Content

### 🔴 **PRIORITY 3: Complete Task** ✅ Complete

**Status**: ✅ Complete

Content
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert len(priorities) == 3
        assert "Planned" in priorities[0]["status"]
        assert "In Progress" in priorities[1]["status"]
        assert "Complete" in priorities[2]["status"]

    def test_parser_get_next_planned_priority(self, tmp_path):
        """Verify parser finds next planned priority correctly."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Done** ✅ Complete

**Status**: ✅ Complete

Already done

### 🔴 **PRIORITY 2: Next** 📝 Planned

**Status**: 📝 Planned

Should be selected

### 🔴 **PRIORITY 3: Future** 📝 Planned

**Status**: 📝 Planned

Later
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        assert next_priority is not None
        assert next_priority["name"] == "PRIORITY 2"

    def test_parser_get_in_progress_priorities(self, tmp_path):
        """Verify parser finds all in-progress priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: WIP 1** 🔄 In Progress

**Status**: 🔄 In Progress

Working

### 🔴 **PRIORITY 2: Planned** 📝 Planned

**Status**: 📝 Planned

Not started

### 🔴 **PRIORITY 3: WIP 2** 🔄 In Progress

**Status**: 🔄 In Progress

Also working
        """
        )

        parser = RoadmapParser(str(roadmap))
        in_progress = parser.get_in_progress_priorities()

        assert len(in_progress) == 2
        assert in_progress[0]["name"] == "PRIORITY 1"
        assert in_progress[1]["name"] == "PRIORITY 3"

    def test_parser_extract_deliverables(self, tmp_path):
        """Verify parser extracts deliverables from priority."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test** 📝 Planned

**Status**: 📝 Planned

Task description

**Deliverables**:
- Create file1.txt
- Create file2.py
- Update README.md
        """
        )

        parser = RoadmapParser(str(roadmap))
        deliverables = parser.extract_deliverables("PRIORITY 1")

        assert len(deliverables) == 3
        assert "Create file1.txt" in deliverables
        assert "Create file2.py" in deliverables
        assert "Update README.md" in deliverables

    def test_parser_is_priority_complete(self, tmp_path):
        """Verify parser correctly identifies complete priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Done** ✅ Complete

**Status**: ✅ Complete

Complete

### 🔴 **PRIORITY 2: Not Done** 📝 Planned

**Status**: 📝 Planned

Not complete
        """
        )

        parser = RoadmapParser(str(roadmap))

        assert parser.is_priority_complete("PRIORITY 1") is True
        assert parser.is_priority_complete("PRIORITY 2") is False

    def test_parser_handles_no_priorities(self, tmp_path):
        """Verify parser handles ROADMAP with no priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

This is a roadmap but it has no priorities yet.
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert isinstance(priorities, list)
        assert len(priorities) == 0

    def test_parser_handles_malformed_priority(self, tmp_path):
        """Verify parser handles malformed priority headers."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1 Missing Format

Not properly formatted

### 🔴 **PRIORITY 2: Valid** 📝 Planned

**Status**: 📝 Planned

This is valid
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should find only the valid priority
        assert len(priorities) >= 1
        valid_found = any(p["name"] == "PRIORITY 2" for p in priorities)
        assert valid_found
