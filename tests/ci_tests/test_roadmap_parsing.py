"""ROADMAP parsing tests for code_developer daemon.

These tests verify the RoadmapParser can handle various ROADMAP formats,
edge cases, and malformed input without crashing.
"""

from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestRoadmapParserBasics:
    """Test basic ROADMAP parsing functionality."""

    def test_parser_loads_real_roadmap(self):
        """Verify parser can load the actual project ROADMAP."""
        parser = RoadmapParser("docs/ROADMAP.md")
        assert parser.roadmap_path.exists()
        content = parser.roadmap_path.read_text()
        assert len(content) > 0

    def test_parser_extracts_priorities(self):
        """Verify parser can extract all priorities from ROADMAP."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()
        assert len(priorities) > 0
        assert all(isinstance(p, dict) for p in priorities)

    def test_parser_priority_has_required_fields(self):
        """Verify each priority has name, title, status, content."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()

        for priority in priorities:
            assert "name" in priority
            assert "title" in priority
            assert "status" in priority
            assert "content" in priority

    def test_parser_finds_next_planned_priority(self):
        """Verify parser can find next planned priority."""
        parser = RoadmapParser("docs/ROADMAP.md")
        next_priority = parser.get_next_planned_priority()
        # May be None if all complete, otherwise should be dict
        assert next_priority is None or isinstance(next_priority, dict)


class TestRoadmapStatusDetection:
    """Test status detection in priorities."""

    def test_status_complete(self, tmp_path):
        """Verify detection of ✅ Complete status."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
This is done
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert priorities[0]["status"] == "complete"

    def test_status_planned(self, tmp_path):
        """Verify detection of 📝 Planned status."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Todo 📝 Planned
Not started yet
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert priorities[0]["status"] == "planned"

    def test_status_in_progress(self, tmp_path):
        """Verify detection of 🔄 In Progress status."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Working 🔄 In Progress
Currently working on this
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert priorities[0]["status"] == "in_progress"

    def test_status_blocked(self, tmp_path):
        """Verify detection of ⏸️ Blocked status."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Blocked ⏸️ Blocked
Waiting on external dependency
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert priorities[0]["status"] == "blocked"


class TestRoadmapEdgeCases:
    """Test edge cases and malformed ROADMAP handling."""

    def test_empty_roadmap(self, tmp_path):
        """Verify parser handles completely empty ROADMAP."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 0

    def test_roadmap_with_only_title(self, tmp_path):
        """Verify parser handles ROADMAP with just a title."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# My Roadmap\n\n")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 0

    def test_roadmap_with_no_priorities(self, tmp_path):
        """Verify parser handles ROADMAP with content but no priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

This is my project roadmap. I will add priorities later.

## Notes
- Some random notes
- More notes
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 0

    def test_malformed_priority_header(self, tmp_path):
        """Verify parser handles malformed priority headers."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY NOT A NUMBER: Weird
This priority name is malformed

### PRIORITY 1: Normal 📝 Planned
This one is normal
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        # Should find at least the normal one
        assert any(p["name"] == "PRIORITY 1" for p in priorities)

    def test_priority_with_no_content(self, tmp_path):
        """Verify parser handles priority with no content."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Empty 📝 Planned

### PRIORITY 2: Has Content 📝 Planned
This has actual content
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 2

    def test_priority_with_special_characters(self, tmp_path):
        """Verify parser handles special characters in titles."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Test with "quotes" & symbols <> 📝 Planned
Content with $pecial ch@racters!
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert "quotes" in priorities[0]["title"]


class TestRoadmapComplexStructures:
    """Test complex ROADMAP structures."""

    def test_nested_subsections(self, tmp_path):
        """Verify parser handles priorities with nested subsections."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Complex Task 📝 Planned

#### Phase 1: Analysis
Do analysis

#### Phase 2: Implementation
Implement stuff

#### Phase 3: Testing
Test everything
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert "Phase 1" in priorities[0]["content"]
        assert "Phase 2" in priorities[0]["content"]

    def test_priority_with_code_blocks(self, tmp_path):
        """Verify parser handles code blocks in priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Code Example 📝 Planned

Example code:

```python
def hello():
    return "world"
```

More content after code block.
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert "def hello" in priorities[0]["content"]

    def test_priority_with_lists(self, tmp_path):
        """Verify parser handles bulleted and numbered lists."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Lists 📝 Planned

**Deliverables**:
- Item 1
- Item 2
- Item 3

**Steps**:
1. First step
2. Second step
3. Third step
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 1
        assert "Item 1" in priorities[0]["content"]
        assert "First step" in priorities[0]["content"]

    def test_multiple_priorities_sequential(self, tmp_path):
        """Verify parser correctly extracts multiple priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: First ✅ Complete
Done

### PRIORITY 2: Second 📝 Planned
Next

### PRIORITY 3: Third 📝 Planned
After that

### PRIORITY 4: Fourth ⏸️ Blocked
Blocked
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        assert len(priorities) == 4

        # Verify order preserved
        assert priorities[0]["name"] == "PRIORITY 1"
        assert priorities[1]["name"] == "PRIORITY 2"
        assert priorities[2]["name"] == "PRIORITY 3"
        assert priorities[3]["name"] == "PRIORITY 4"

    def test_decimal_priority_numbers(self, tmp_path):
        """Verify parser handles decimal priority numbers (2.5, 2.6, etc.)."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 2: Original ✅ Complete
Done

### PRIORITY 2.5: Inserted ✅ Complete
Also done

### PRIORITY 2.6: Another Insert 📝 Planned
Current

### PRIORITY 3: Next 📝 Planned
Later
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should find all priorities including decimals
        priority_names = [p["name"] for p in priorities]
        assert "PRIORITY 2" in priority_names
        assert "PRIORITY 2.5" in priority_names
        assert "PRIORITY 2.6" in priority_names
        assert "PRIORITY 3" in priority_names


class TestGetNextPlannedPriority:
    """Test get_next_planned_priority() method."""

    def test_finds_first_planned(self, tmp_path):
        """Verify finds first 📝 Planned priority."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
Complete

### PRIORITY 2: Current 📝 Planned
This should be returned

### PRIORITY 3: Future 📝 Planned
Later
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        assert next_task is not None
        assert next_task["name"] == "PRIORITY 2"

    def test_returns_none_when_all_complete(self, tmp_path):
        """Verify returns None when all priorities complete."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
Done

### PRIORITY 2: Also Done ✅ Complete
Done too
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        assert next_task is None

    def test_skips_blocked_priorities(self, tmp_path):
        """Verify skips ⏸️ Blocked priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
Complete

### PRIORITY 2: Blocked ⏸️ Blocked
Can't do this yet

### PRIORITY 3: Can Do 📝 Planned
This should be returned
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        assert next_task is not None
        assert next_task["name"] == "PRIORITY 3"

    def test_skips_in_progress(self, tmp_path):
        """Verify behavior with 🔄 In Progress priorities."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Working 🔄 In Progress
Currently being worked on

### PRIORITY 2: Next 📝 Planned
Should pick this one
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        # Should skip in_progress and find planned
        assert next_task is not None
        assert next_task["name"] == "PRIORITY 2"
