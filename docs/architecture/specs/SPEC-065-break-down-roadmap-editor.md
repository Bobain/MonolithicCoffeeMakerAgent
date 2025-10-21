# SPEC-065: Break Down roadmap_editor.py

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**: REFACTORING_BACKLOG.md (P1 Item #3), ADR-005 (Modular CLI Architecture)

---

## Problem Statement

`coffee_maker/cli/roadmap_editor.py` has grown to **945 lines of code**, which is **nearly 2x the recommended 500 LOC limit**. This monolithic file contains a single `RoadmapEditor` class with 18 methods handling multiple distinct responsibilities:

- **Priority management** (add, update, get summary, get content)
- **User story management** (add, update, assign, get summary, get content)
- **ROADMAP parsing** (extract priorities, extract user stories, find sections)
- **File I/O** (atomic writes, backups, validation)
- **Formatting** (build priority sections, build user story sections)
- **Section management** (find insertion points, create sections)

This violates the Single Responsibility Principle and makes the code:
- Hard to test (tight coupling between parsing, editing, and I/O)
- Difficult to extend (adding new roadmap entities requires modifying large class)
- Risky to maintain (changes to one area can break others)
- Challenging to understand (cognitive overload with 18 methods)

---

## Proposed Solution

Break down `roadmap_editor.py` into a **modular roadmap management architecture** with clear separation between parsing, editing, formatting, and file operations.

### High-Level Architecture

```
coffee_maker/cli/roadmap/
├── __init__.py                     # Public API exports
├── editor.py                       # Core RoadmapEditor coordinator (150 LOC)
├── models.py                       # Data models (Priority, UserStory) (100 LOC)
├── parser.py                       # ROADMAP parsing (250 LOC)
├── formatter.py                    # Section formatting (200 LOC)
├── writer.py                       # File I/O and backups (150 LOC)
├── validators.py                   # Validation logic (100 LOC)
├── priority/
│   ├── __init__.py
│   ├── manager.py                  # Priority operations (200 LOC)
│   └── summary.py                  # Priority summaries (100 LOC)
└── user_story/
    ├── __init__.py
    ├── manager.py                  # User story operations (200 LOC)
    └── summary.py                  # User story summaries (100 LOC)
```

**Total LOC after breakdown**: ~1,450 LOC (across 13 files)
**Average file size**: ~112 LOC (all under 250 LOC target)

---

## Architecture

### Component Design

#### 1. `editor.py` - Core Coordinator (150 LOC)

**Responsibility**: Orchestrate roadmap operations, delegate to specialized components.

```python
from coffee_maker.cli.roadmap.parser import RoadmapParser
from coffee_maker.cli.roadmap.formatter import RoadmapFormatter
from coffee_maker.cli.roadmap.writer import RoadmapWriter
from coffee_maker.cli.roadmap.priority.manager import PriorityManager
from coffee_maker.cli.roadmap.user_story.manager import UserStoryManager

class RoadmapEditor:
    """Core roadmap editor coordinator.

    Delegates to specialized components:
    - Parser (ROADMAP parsing)
    - Formatter (section formatting)
    - Writer (file I/O and backups)
    - PriorityManager (priority operations)
    - UserStoryManager (user story operations)
    """

    def __init__(self, roadmap_path: Path):
        self.roadmap_path = Path(roadmap_path)
        self.backup_dir = self.roadmap_path.parent / "roadmap_backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Initialize components
        self.parser = RoadmapParser()
        self.formatter = RoadmapFormatter()
        self.writer = RoadmapWriter(self.roadmap_path, self.backup_dir)
        self.priority_manager = PriorityManager(self.parser, self.formatter, self.writer)
        self.user_story_manager = UserStoryManager(self.parser, self.formatter, self.writer)

    # Priority operations (delegate to PriorityManager)
    def add_priority(self, priority_number: str, title: str, duration: str,
                     impact: str, status: str = "📝 Planned", description: str = "",
                     deliverables: Optional[List[str]] = None) -> bool:
        """Add new priority to roadmap."""
        return self.priority_manager.add(
            priority_number, title, duration, impact, status, description, deliverables
        )

    def update_priority(self, priority_number: str, field: str, value: str) -> bool:
        """Update existing priority field."""
        return self.priority_manager.update(priority_number, field, value)

    def get_priority_summary(self) -> Dict:
        """Get summary of all priorities."""
        return self.priority_manager.get_summary(self.roadmap_path)

    def get_priority_content(self, priority_number: str) -> Optional[str]:
        """Get full content of a specific priority."""
        return self.priority_manager.get_content(self.roadmap_path, priority_number)

    # User story operations (delegate to UserStoryManager)
    def add_user_story(self, story_id: str, title: str, role: str, want: str,
                      so_that: str, business_value: int = 3,
                      estimated_effort: str = "TBD",
                      acceptance_criteria: Optional[List[str]] = None,
                      technical_notes: str = "", status: str = "📝 Backlog",
                      assigned_to: str = "") -> bool:
        """Add new User Story to backlog section."""
        return self.user_story_manager.add(
            story_id, title, role, want, so_that, business_value,
            estimated_effort, acceptance_criteria, technical_notes, status, assigned_to
        )

    def update_user_story(self, story_id: str, field: str, value: str) -> bool:
        """Update existing User Story field."""
        return self.user_story_manager.update(story_id, field, value)

    def assign_user_story_to_priority(self, story_id: str, priority_number: str) -> bool:
        """Assign User Story to a priority."""
        return self.user_story_manager.assign_to_priority(story_id, priority_number)

    def get_user_story_summary(self) -> Dict:
        """Get summary of all User Stories."""
        return self.user_story_manager.get_summary(self.roadmap_path)

    def get_user_story_content(self, story_id: str) -> Optional[str]:
        """Get full content of a specific User Story."""
        return self.user_story_manager.get_content(self.roadmap_path, story_id)
```

**Public API** (unchanged for backward compatibility):
- `add_priority(...) -> bool`
- `update_priority(...) -> bool`
- `get_priority_summary() -> Dict`
- `get_priority_content(...) -> Optional[str]`
- `add_user_story(...) -> bool`
- `update_user_story(...) -> bool`
- `assign_user_story_to_priority(...) -> bool`
- `get_user_story_summary() -> Dict`
- `get_user_story_content(...) -> Optional[str]`

---

#### 2. `models.py` - Data Models (100 LOC)

**Responsibility**: Define data structures for Priority and UserStory.

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Priority:
    """Priority data model."""
    number: str  # e.g., "PRIORITY 10" or "PRIORITY 2.5"
    title: str
    duration: str
    impact: str
    status: str
    description: str = ""
    deliverables: List[str] = None

    def __post_init__(self):
        if self.deliverables is None:
            self.deliverables = []

    @property
    def number_value(self) -> float:
        """Extract numeric value from priority number."""
        match = re.match(r"PRIORITY (\d+\.?\d*)", self.number, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 0.0


@dataclass
class UserStory:
    """User Story data model."""
    story_id: str  # e.g., "US-001"
    title: str
    role: str
    want: str
    so_that: str
    business_value: int = 3  # 1-5 stars
    estimated_effort: str = "TBD"
    acceptance_criteria: List[str] = None
    technical_notes: str = ""
    status: str = "📝 Backlog"
    assigned_to: str = ""

    def __post_init__(self):
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []

    @property
    def business_value_stars(self) -> str:
        """Get star representation of business value."""
        return "⭐" * self.business_value
```

**Benefits**:
- Type safety with dataclasses
- Clear data contracts
- Easy to test
- Reusable across components

---

#### 3. `parser.py` - ROADMAP Parsing (250 LOC)

**Responsibility**: Parse ROADMAP.md and extract structured data.

```python
import re
from pathlib import Path
from typing import List, Optional, Dict

from coffee_maker.cli.roadmap.models import Priority, UserStory

class RoadmapParser:
    """Parses ROADMAP.md and extracts structured data."""

    def parse_priorities(self, content: str) -> List[Priority]:
        """Parse all priorities from ROADMAP content."""
        priorities = []

        # Pattern matches: ### 🔴 **PRIORITY X: Title** ... Status: ...
        pattern = r"### [🔴🟢] \*\*PRIORITY (\d+\.?\d*):(.+?)\*\*.*?\n.*?\*\*Status\*\*: (.+?)\n"
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            priority_number = f"PRIORITY {match[0]}"
            title = match[1].strip()
            status = match[2].strip()

            priorities.append(Priority(
                number=priority_number,
                title=title,
                duration="",  # Extract if needed
                impact="",    # Extract if needed
                status=status
            ))

        return priorities

    def get_priority_content(self, content: str, priority_number: str) -> Optional[str]:
        """Get full content of a specific priority."""
        lines = content.split("\n")

        # Normalize priority number
        if not priority_number.startswith("PRIORITY"):
            priority_number = f"PRIORITY {priority_number}"

        # Find priority section
        in_priority = False
        priority_lines = []

        for line in lines:
            # Check if this is the start of our priority
            if priority_number.upper() in line.upper() and line.startswith("###"):
                in_priority = True
                priority_lines.append(line)
            elif in_priority:
                # Check if we've hit the next priority
                if line.startswith("###") and "PRIORITY" in line.upper():
                    break
                priority_lines.append(line)

        if priority_lines:
            return "\n".join(priority_lines)
        return None

    def parse_user_stories(self, content: str) -> List[UserStory]:
        """Parse all User Stories from ROADMAP content."""
        stories = []

        # Pattern matches: ### 🎯 [US-XXX] Title
        pattern = r"### 🎯 \[(US-\d+)\] (.+?)\n.*?\*\*Status\*\*: (.+?)\n"
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            story_id, title, status = match
            stories.append(UserStory(
                story_id=story_id,
                title=title.strip(),
                role="",  # Extract if needed
                want="",  # Extract if needed
                so_that="",  # Extract if needed
                status=status.strip()
            ))

        return stories

    def get_user_story_content(self, content: str, story_id: str) -> Optional[str]:
        """Get full content of a specific User Story."""
        lines = content.split("\n")

        # Find User Story section
        in_story = False
        story_lines = []

        for line in lines:
            # Check if this is the start of our story
            if f"[{story_id}]" in line and line.startswith("###"):
                in_story = True
                story_lines.append(line)
            elif in_story:
                # Check if we've hit the next story or section
                if line.startswith("###") or line.startswith("##"):
                    break
                story_lines.append(line)

        if story_lines:
            return "\n".join(story_lines)
        return None

    def find_priority_section(self, lines: List[str], priority_number: str) -> Optional[int]:
        """Find line index of priority section."""
        for i, line in enumerate(lines):
            if priority_number.upper() in line.upper() and line.startswith("###"):
                return i
        return None

    def find_user_story_section(self, lines: List[str], story_id: str) -> Optional[int]:
        """Find line index of user story section."""
        for i, line in enumerate(lines):
            if f"[{story_id}]" in line and line.startswith("###"):
                return i
        return None

    def find_priorities_section(self, lines: List[str]) -> Optional[int]:
        """Find line index of PRIORITIES section."""
        for i, line in enumerate(lines):
            if "## 🎯 PRIORITIES" in line or ("## " in line and "PRIORITY" in line.upper()):
                return i
        return None

    def find_user_story_backlog_section(self, lines: List[str]) -> Optional[int]:
        """Find line index of USER STORY BACKLOG section."""
        for i, line in enumerate(lines):
            if "## 📋 USER STORY BACKLOG" in line:
                return i
        return None
```

**Benefits**:
- Centralized parsing logic
- Reusable across components
- Easy to test parsing independently
- Can evolve parsing without affecting other components

---

#### 4. `formatter.py` - Section Formatting (200 LOC)

**Responsibility**: Build formatted ROADMAP sections.

```python
from typing import List

from coffee_maker.cli.roadmap.models import Priority, UserStory

class RoadmapFormatter:
    """Formats ROADMAP sections."""

    def format_priority(self, priority: Priority) -> str:
        """Build formatted priority section."""
        section = f"""
### 🔴 **{priority.number}: {priority.title}**

**Estimated Duration**: {priority.duration}
**Impact**: {priority.impact}
**Status**: {priority.status}

#### Project: {priority.title}

{priority.description if priority.description else f"Implementation of {priority.title}."}

**Deliverables**:
"""
        if priority.deliverables:
            for item in priority.deliverables:
                section += f"- {item}\n"
        else:
            section += "- TBD\n"

        section += "\n---\n"

        return section

    def format_user_story(self, story: UserStory) -> str:
        """Build formatted User Story section."""
        section = f"""
### 🎯 [{story.story_id}] {story.title}

**As a**: {story.role}
**I want**: {story.want}
**So that**: {story.so_that}

**Business Value**: {story.business_value_stars}
**Estimated Effort**: {story.estimated_effort}
**Status**: {story.status}
"""
        if story.assigned_to:
            section += f"**Assigned To**: {story.assigned_to}\n"

        section += "\n**Acceptance Criteria**:\n"
        if story.acceptance_criteria:
            for criterion in story.acceptance_criteria:
                section += f"- [ ] {criterion}\n"
        else:
            section += "- [ ] TBD\n"

        if story.technical_notes:
            section += f"\n**Technical Notes**:\n{story.technical_notes}\n"

        section += "\n---\n"

        return section

    def create_user_story_backlog_section(self) -> List[str]:
        """Create User Story Backlog section header."""
        return [
            "",
            "---",
            "",
            "## 📋 USER STORY BACKLOG",
            "",
            "> **What is this section?**",
            "> This is where user needs are captured before being translated into technical priorities.",
            "> User Stories help us understand WHAT users need and WHY, before deciding HOW to implement.",
            "",
            "---",
            "",
        ]
```

**Benefits**:
- Centralized formatting logic
- Consistent section format
- Easy to change formatting without touching other code
- Testable with simple assertions

---

#### 5. `writer.py` - File I/O and Backups (150 LOC)

**Responsibility**: Handle file writes, backups, and atomic operations.

```python
import shutil
from datetime import datetime
from pathlib import Path

class RoadmapWriter:
    """Handles ROADMAP file I/O and backups."""

    def __init__(self, roadmap_path: Path, backup_dir: Path):
        self.roadmap_path = roadmap_path
        self.backup_dir = backup_dir

    def read_roadmap(self) -> str:
        """Read ROADMAP content."""
        return self.roadmap_path.read_text()

    def write_roadmap(self, content: str):
        """Write ROADMAP with automatic backup."""
        # Create backup first
        self.create_backup()

        # Atomic write
        self._atomic_write(content)

    def create_backup(self):
        """Create timestamped backup of roadmap."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"ROADMAP_{timestamp}.md"
            shutil.copy(self.roadmap_path, backup_path)

            logger.info(f"Created backup: {backup_path}")

            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("ROADMAP_*.md"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")

        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    def _atomic_write(self, content: str):
        """Atomically write content to roadmap file."""
        temp_path = self.roadmap_path.with_suffix(".tmp")
        try:
            # Write to temp file
            temp_path.write_text(content)

            # Atomic rename
            temp_path.replace(self.roadmap_path)

            logger.debug("Atomically wrote roadmap")

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to write roadmap: {e}")
```

**Benefits**:
- Encapsulates all file operations
- Backup logic isolated from editing logic
- Easy to test with temporary files
- Atomic writes prevent corruption

---

#### 6. `validators.py` - Validation Logic (100 LOC)

**Responsibility**: Validate priority numbers, story IDs, fields.

```python
import re

class RoadmapValidator:
    """Validates ROADMAP entities."""

    @staticmethod
    def validate_priority_number(priority_number: str, content: str) -> bool:
        """Validate priority number is unique and well-formed."""
        # Check if already exists (case insensitive)
        if priority_number.upper() in content.upper():
            logger.warning(f"Priority {priority_number} already exists")
            return False

        # Extract and validate number format
        match = re.match(r"PRIORITY (\d+\.?\d*)", priority_number, re.IGNORECASE)
        if not match:
            logger.warning(f"Invalid priority number format: {priority_number}")
            return False

        return True

    @staticmethod
    def validate_story_id(story_id: str, content: str) -> bool:
        """Validate story ID is unique."""
        if story_id.upper() in content.upper():
            logger.warning(f"User Story {story_id} already exists")
            return False
        return True

    @staticmethod
    def validate_priority_field(field: str) -> bool:
        """Validate priority field name."""
        valid_fields = ["status", "duration", "estimated duration", "impact"]
        return field.lower() in valid_fields

    @staticmethod
    def validate_story_field(field: str) -> bool:
        """Validate user story field name."""
        valid_fields = ["status", "business_value", "estimated_effort", "assigned_to"]
        return field.lower() in valid_fields
```

---

#### 7. `priority/manager.py` - Priority Operations (200 LOC)

**Responsibility**: Manage priority CRUD operations.

```python
from typing import List, Optional

from coffee_maker.cli.roadmap.models import Priority
from coffee_maker.cli.roadmap.parser import RoadmapParser
from coffee_maker.cli.roadmap.formatter import RoadmapFormatter
from coffee_maker.cli.roadmap.writer import RoadmapWriter
from coffee_maker.cli.roadmap.validators import RoadmapValidator

class PriorityManager:
    """Manages priority operations."""

    def __init__(self, parser: RoadmapParser, formatter: RoadmapFormatter, writer: RoadmapWriter):
        self.parser = parser
        self.formatter = formatter
        self.writer = writer
        self.validator = RoadmapValidator()

    def add(self, priority_number: str, title: str, duration: str, impact: str,
            status: str, description: str, deliverables: Optional[List[str]]) -> bool:
        """Add new priority to roadmap."""
        try:
            # Read current roadmap
            content = self.writer.read_roadmap()

            # Validate priority number
            if not self.validator.validate_priority_number(priority_number, content):
                raise ValueError(f"Priority {priority_number} already exists or is invalid")

            # Build priority model
            priority = Priority(
                number=priority_number,
                title=title,
                duration=duration,
                impact=impact,
                status=status,
                description=description,
                deliverables=deliverables or []
            )

            # Format priority section
            priority_section = self.formatter.format_priority(priority)

            # Find insertion point
            lines = content.split("\n")
            insert_index = self._find_insertion_point(lines, priority)

            # Insert new priority
            lines.insert(insert_index, priority_section)

            # Write back
            new_content = "\n".join(lines)
            self.writer.write_roadmap(new_content)

            logger.info(f"Added {priority_number}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to add priority: {e}")
            raise

    def update(self, priority_number: str, field: str, value: str) -> bool:
        """Update existing priority field."""
        try:
            # Read roadmap
            content = self.writer.read_roadmap()

            # Normalize priority number
            if not priority_number.startswith("PRIORITY"):
                priority_number = f"PRIORITY {priority_number}"

            # Validate field
            if not self.validator.validate_priority_field(field):
                raise ValueError(f"Unsupported field: {field}")

            # Find priority section
            pattern = rf"### 🔴 \*\*{re.escape(priority_number)}:.*?\*\*"
            match = re.search(pattern, content, re.IGNORECASE)

            if not match:
                raise ValueError(f"{priority_number} not found in roadmap")

            # Update field based on type
            content = self._update_field(content, priority_number, field, value)

            # Write back
            self.writer.write_roadmap(content)

            logger.info(f"Updated {priority_number} {field} to {value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update priority: {e}")
            raise

    def get_summary(self, roadmap_path: Path) -> Dict:
        """Get summary of all priorities."""
        try:
            content = roadmap_path.read_text()
            priorities = self.parser.parse_priorities(content)

            # Count by status
            completed = len([p for p in priorities if "✅" in p.status])
            in_progress = len([p for p in priorities if "🔄" in p.status])
            planned = len([p for p in priorities if "📝" in p.status])

            return {
                "total": len(priorities),
                "priorities": [
                    {"number": p.number, "title": p.title, "status": p.status}
                    for p in priorities
                ],
                "completed": completed,
                "in_progress": in_progress,
                "planned": planned,
            }

        except Exception as e:
            logger.error(f"Failed to get priority summary: {e}")
            return {
                "total": 0,
                "priorities": [],
                "completed": 0,
                "in_progress": 0,
                "planned": 0,
            }

    def get_content(self, roadmap_path: Path, priority_number: str) -> Optional[str]:
        """Get full content of a specific priority."""
        try:
            content = roadmap_path.read_text()
            return self.parser.get_priority_content(content, priority_number)
        except Exception as e:
            logger.error(f"Failed to get priority content: {e}")
            return None

    def _find_insertion_point(self, lines: List[str], priority: Priority) -> int:
        """Find where to insert new priority (numerical order)."""
        new_priority_num = priority.number_value

        # Find all existing priorities and their line numbers
        priority_positions = []
        for i, line in enumerate(lines):
            if line.startswith("### ") and "PRIORITY" in line.upper():
                # Extract priority number
                priority_match = re.search(r"PRIORITY (\d+\.?\d*)", line, re.IGNORECASE)
                if priority_match:
                    priority_positions.append((float(priority_match.group(1)), i))

        # Find insertion point based on numerical order
        insert_line = len(lines)  # Default to end
        for priority_num, line_idx in priority_positions:
            if new_priority_num < priority_num:
                # Insert before this priority
                insert_line = line_idx
                break

        return insert_line

    def _update_field(self, content: str, priority_number: str, field: str, value: str) -> str:
        """Update specific field in priority section."""
        field_lower = field.lower()

        if field_lower == "status":
            content = re.sub(
                rf"(\*\*{re.escape(priority_number)}:.*?\*\*.*?\n.*?\*\*Status\*\*:) [^\n]+",
                rf"\1 {value}",
                content,
                flags=re.IGNORECASE,
            )
        elif field_lower in ["duration", "estimated duration"]:
            content = re.sub(
                rf"(\*\*{re.escape(priority_number)}:.*?\n.*?\*\*Estimated Duration\*\*:) [^\n]+",
                rf"\1 {value}",
                content,
                flags=re.IGNORECASE,
            )
        elif field_lower == "impact":
            content = re.sub(
                rf"(\*\*{re.escape(priority_number)}:.*?\n.*?\*\*Impact\*\*:) [^\n]+",
                rf"\1 {value}",
                content,
                flags=re.IGNORECASE,
            )

        return content
```

---

#### 8. `user_story/manager.py` - User Story Operations (200 LOC)

**Responsibility**: Manage user story CRUD operations.

Similar structure to `PriorityManager` but for user stories:

```python
class UserStoryManager:
    """Manages user story operations."""

    def __init__(self, parser: RoadmapParser, formatter: RoadmapFormatter, writer: RoadmapWriter):
        self.parser = parser
        self.formatter = formatter
        self.writer = writer
        self.validator = RoadmapValidator()

    def add(self, story_id: str, title: str, role: str, want: str, so_that: str,
            business_value: int, estimated_effort: str, acceptance_criteria: Optional[List[str]],
            technical_notes: str, status: str, assigned_to: str) -> bool:
        """Add new User Story to backlog section."""
        # Similar to PriorityManager.add()
        pass

    def update(self, story_id: str, field: str, value: str) -> bool:
        """Update existing User Story field."""
        # Similar to PriorityManager.update()
        pass

    def assign_to_priority(self, story_id: str, priority_number: str) -> bool:
        """Assign User Story to a priority."""
        pass

    def get_summary(self, roadmap_path: Path) -> Dict:
        """Get summary of all User Stories."""
        pass

    def get_content(self, roadmap_path: Path, story_id: str) -> Optional[str]:
        """Get full content of a specific User Story."""
        pass
```

---

## Migration Strategy

**Phase 1: Create New Module Structure (Day 1 Morning)**
1. Create `coffee_maker/cli/roadmap/` directory structure
2. Implement `models.py` (Priority, UserStory data classes)
3. Implement `parser.py` (ROADMAP parsing logic)
4. Implement `formatter.py` (section formatting)
5. Add tests for parser and formatter

**Phase 2: Extract Support Components (Day 1 Afternoon)**
6. Implement `writer.py` (file I/O and backups)
7. Implement `validators.py` (validation logic)
8. Add tests for writer and validators

**Phase 3: Extract Managers (Day 2 Morning)**
9. Implement `priority/manager.py` (priority operations)
10. Implement `user_story/manager.py` (user story operations)
11. Add tests for managers

**Phase 4: Refactor Core Editor (Day 2 Afternoon)**
12. Refactor `RoadmapEditor` to use extracted components
13. Update imports to use new module paths
14. Ensure backward compatibility with existing API
15. Run full test suite

**Phase 5: Update Consumers (Day 2 Afternoon)**
16. Update imports in consuming modules:
    - `coffee_maker/cli/roadmap_cli.py`
    - `coffee_maker/cli/ai_service.py`
    - `coffee_maker/autonomous/daemon.py`
    - Tests
17. Deprecate old imports with warnings

**Phase 6: Documentation & Cleanup (Day 2 Evening)**
18. Update documentation
19. Remove old `roadmap_editor.py` file
20. Final testing and verification

**Total Effort**: 2 days

---

## Testing Strategy

### Unit Tests

**Per Component**:
```python
# tests/unit/cli/roadmap/test_parser.py
def test_parse_priorities():
    """Test priority parsing."""
    parser = RoadmapParser()
    content = """
### 🔴 **PRIORITY 1: Authentication**
**Status**: ✅ Complete
"""
    priorities = parser.parse_priorities(content)
    assert len(priorities) == 1
    assert priorities[0].number == "PRIORITY 1"
    assert priorities[0].title == "Authentication"

# tests/unit/cli/roadmap/test_formatter.py
def test_format_priority():
    """Test priority formatting."""
    formatter = RoadmapFormatter()
    priority = Priority(
        number="PRIORITY 10",
        title="New Feature",
        duration="1 week",
        impact="⭐⭐⭐",
        status="📝 Planned"
    )
    formatted = formatter.format_priority(priority)
    assert "### 🔴 **PRIORITY 10: New Feature**" in formatted
    assert "**Status**: 📝 Planned" in formatted

# tests/unit/cli/roadmap/test_priority_manager.py
def test_priority_manager_add():
    """Test adding priority."""
    manager = PriorityManager(parser, formatter, writer)
    success = manager.add(
        "PRIORITY 10",
        "New Feature",
        "1 week",
        "⭐⭐⭐",
        "📝 Planned",
        "",
        []
    )
    assert success
```

### Integration Tests

**Full Workflow**:
```python
# tests/integration/test_roadmap_editor.py
def test_roadmap_editor_add_priority():
    """Test full add priority workflow."""
    editor = RoadmapEditor(temp_roadmap_path)
    success = editor.add_priority(
        "PRIORITY 10",
        "New Feature",
        "1 week",
        "⭐⭐⭐",
        "📝 Planned"
    )
    assert success

    # Verify priority was added
    content = temp_roadmap_path.read_text()
    assert "PRIORITY 10: New Feature" in content
```

### Characterization Tests

**Capture Current Behavior**:
```python
def test_current_behavior_get_priority_summary():
    """Characterization test: capture current behavior before refactoring."""
    editor = RoadmapEditor(ROADMAP_PATH)
    summary = editor.get_priority_summary()

    # Assert current output structure
    assert "total" in summary
    assert "priorities" in summary
    assert "completed" in summary
```

**Run these tests BEFORE refactoring, ensure they pass AFTER refactoring.**

---

## Rollout Plan

### Timeline

- **Day 1**: Create module structure, extract components, add tests
- **Day 2**: Refactor core editor, update consumers, documentation

**Total Effort**: 2 days

### Rollback Plan

If issues arise:
1. Keep old `roadmap_editor.py` file until fully verified
2. Use feature flags to toggle between old/new implementations
3. Monitor error rates in production
4. Roll back to old implementation if >5% error rate increase

---

## Risks & Mitigations

### Risk 1: Breaking Existing Consumers

**Likelihood**: Medium
**Impact**: High

**Mitigation**:
- Maintain backward compatibility with old imports
- Add deprecation warnings for old imports
- Run full test suite before merging
- Use feature flags for gradual rollout

### Risk 2: Parser Changes

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Add comprehensive parser tests
- Verify with production ROADMAP.md
- Test with edge cases (empty sections, malformed entries)

### Risk 3: File Corruption

**Likelihood**: Low
**Impact**: High

**Mitigation**:
- Maintain backup strategy
- Use atomic writes
- Add file integrity checks
- Test with concurrent writes

---

## Success Metrics

**Before Refactoring**:
- 1 file: `roadmap_editor.py` (945 LOC)
- 1 class: `RoadmapEditor` (18 methods)
- Cognitive complexity: HIGH
- Test coverage: ~70%

**After Refactoring**:
- 13 files (average ~112 LOC each)
- 8 classes (average ~3-4 methods each)
- Cognitive complexity: LOW (each file focused on single responsibility)
- Test coverage: >85% (easier to test isolated components)

**Key Improvements**:
- ✅ All files <250 LOC (target achieved)
- ✅ Clear separation of concerns
- ✅ Easier to test (isolated components)
- ✅ Easier to extend (add new roadmap entities)
- ✅ Better code reuse
- ✅ Reduced coupling

---

## Related Work

- **SPEC-064**: Break down ai_service.py (similar refactoring approach)
- **ADR-005**: Modular CLI Architecture (consistent with this refactoring)
- **REFACTORING_BACKLOG**: P1 Item #3

---

## Approval

**Pending approval from code_developer** for implementation.

Once approved, code_developer will:
1. Create feature branch: `refactor/break-down-roadmap-editor`
2. Implement according to this spec
3. Add comprehensive tests
4. Update documentation
5. Create PR for review

---

## Version History

- **v1.0** (2025-10-17): Initial draft by architect agent
