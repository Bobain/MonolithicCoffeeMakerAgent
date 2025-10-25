"""Unit tests for ImplementationTaskCreator (PRIORITY 32).

Tests cover:
- Spec analysis and task unit identification
- File dependency analysis
- Implementation task creation with sequential ordering
- File conflict detection
- Parallelization analysis

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 32, SPEC-132, CFR-000
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from coffee_maker.autonomous.implementation_task_creator import (
    ImplementationTaskCreator,
    FileConflictError,
    SpecNotFoundError,
)


@pytest.fixture
def temp_db():
    """Create temporary database with tasks and specs_specification tables."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute(
        """
        CREATE TABLE specs_task (
            task_id TEXT PRIMARY KEY,
            priority_number INTEGER NOT NULL,
            task_group_id TEXT NOT NULL,
            priority_order INTEGER NOT NULL,
            spec_id TEXT NOT NULL,
            scope_description TEXT NOT NULL,
            assigned_files TEXT NOT NULL,
            spec_sections TEXT,
            status TEXT NOT NULL,
            process_id INTEGER,
                worktree_path TEXT,
                branch_name TEXT,
            claimed_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL,

            UNIQUE(priority_number, priority_order),
                UNIQUE(spec_id, priority_order),
                UNIQUE(task_group_id, priority_order),
                UNIQUE(spec_id, scope_description, spec_sections)
        )
    """
    )

    # Create specs_specification table
    cursor.execute(
        """
        CREATE TABLE specs_specification (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            spec_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def creator(temp_db):
    """Create ImplementationTaskCreator instance."""
    return ImplementationTaskCreator(temp_db)


@pytest.fixture
def hierarchical_spec(temp_db):
    """Insert hierarchical spec into database."""
    spec_id = "SPEC-100"
    spec_type = "hierarchical"

    spec_json = {
        "overview": "Test spec for task creation",
        "implementation": """
Phase 1: Database Schema
Create `coffee_maker/autonomous/unified_database.py` with schema definitions.
Create `tests/unit/test_unified_database.py` for tests.

Phase 2: API Implementation
Modify `coffee_maker/api/endpoints.py` to add new endpoints.
Create `tests/unit/test_endpoints.py` for API tests.

Phase 3: Testing
Create `tests/integration/test_full_workflow.py` for integration tests.
        """,
        "testing": "Run all tests and ensure coverage > 90%",
    }

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO specs_specification (id, content, spec_type, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (spec_id, json.dumps(spec_json), spec_type, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return spec_id


@pytest.fixture
def markdown_spec(temp_db):
    """Insert markdown spec into database."""
    spec_id = "SPEC-101"
    spec_type = "markdown"

    spec_content = """
# Feature Implementation

## Phase 1: Setup
Create database.py for database access.

## Phase 2: Logic
Implement business logic in core.py.

## Phase 3: Tests
Add tests in test_core.py.
    """

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO specs_specification (id, content, spec_type, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (spec_id, spec_content, spec_type, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return spec_id


class TestWorkCreatorInit:
    """Test ImplementationTaskCreator initialization."""

    def test_init(self, temp_db):
        """Test basic initialization."""
        creator = ImplementationTaskCreator(temp_db)

        assert creator.db_path == temp_db


class TestReadSpec:
    """Test reading technical specs."""

    def test_read_hierarchical_spec(self, creator, hierarchical_spec):
        """Test reading hierarchical spec."""
        content, spec_type = creator._read_spec(hierarchical_spec)

        assert spec_type == "hierarchical"
        assert isinstance(content, dict)
        assert "overview" in content
        assert "implementation" in content

    def test_read_markdown_spec(self, creator, markdown_spec):
        """Test reading markdown spec."""
        content, spec_type = creator._read_spec(markdown_spec)

        assert spec_type == "markdown"
        assert isinstance(content, str)
        assert "Phase 1" in content

    def test_read_nonexistent_spec(self, creator):
        """Test reading spec that doesn't exist."""
        with pytest.raises(SpecNotFoundError):
            creator._read_spec("SPEC-999")


class TestIdentifyWorkUnits:
    """Test task unit identification."""

    def test_identify_hierarchical_units_phase_granularity(self, creator, hierarchical_spec):
        """Test identifying work units from hierarchical spec (phase level)."""
        content, spec_type = creator._read_spec(hierarchical_spec)

        units = creator._identify_work_units(content, spec_type, "phase")

        # Should identify 3 phases
        assert len(units) == 3
        assert units[0]["description"] == "Phase 1: Database Schema"
        assert units[1]["description"] == "Phase 2: API Implementation"
        assert units[2]["description"] == "Phase 3: Testing"

    def test_identify_hierarchical_units_section_granularity(self, creator, hierarchical_spec):
        """Test identifying work units from hierarchical spec (section level)."""
        content, spec_type = creator._read_spec(hierarchical_spec)

        units = creator._identify_work_units(content, spec_type, "section")

        # Should identify sections: implementation, testing
        assert len(units) == 2
        assert any("/implementation" in u["sections"] for u in units)
        assert any("/testing" in u["sections"] for u in units)

    def test_identify_markdown_units(self, creator, markdown_spec):
        """Test identifying work units from markdown spec."""
        content, spec_type = creator._read_spec(markdown_spec)

        units = creator._identify_work_units(content, spec_type, "phase")

        # Should identify 3 phases from markdown
        assert len(units) == 3
        assert units[0]["description"] == "Phase 1: Setup"
        assert units[1]["description"] == "Phase 2: Logic"


class TestExtractPhases:
    """Test phase extraction from markdown."""

    def test_extract_phases_from_text(self, creator):
        """Test extracting phases from markdown text."""
        content = """
Phase 1: Database Setup
Create the database schema.

Phase 2: API Development
Implement REST endpoints.

Phase 3: Testing
Write integration tests.
        """

        phases = creator._extract_phases(content)

        assert len(phases) == 3
        assert phases[0]["number"] == 1
        assert phases[0]["title"] == "Database Setup"
        assert "database schema" in phases[0]["content"].lower()

    def test_extract_phases_with_headers(self, creator):
        """Test extracting phases with markdown headers."""
        content = """
## Phase 1: Setup
Initial setup code.

## Phase 2: Implementation
Main implementation.
        """

        phases = creator._extract_phases(content)

        assert len(phases) == 2
        assert phases[0]["title"] == "Setup"
        assert phases[1]["title"] == "Implementation"


class TestAnalyzeFileDependencies:
    """Test file dependency analysis."""

    def test_analyze_file_dependencies_with_backticks(self, creator):
        """Test analyzing files mentioned with backticks."""
        work_unit = {
            "description": "Phase 1",
            "phase_content": "Create `coffee_maker/api.py` and `tests/test_api.py` files.",
        }

        files = creator._analyze_file_dependencies(work_unit, None)

        assert "coffee_maker/api.py" in files
        assert "tests/test_api.py" in files

    def test_analyze_file_dependencies_with_paths(self, creator):
        """Test analyzing files mentioned as paths."""
        work_unit = {
            "description": "Phase 2",
            "phase_content": "Modify coffee_maker/autonomous/daemon.py to add new features.",
        }

        files = creator._analyze_file_dependencies(work_unit, None)

        assert "coffee_maker/autonomous/daemon.py" in files

    def test_analyze_file_dependencies_with_create_modify(self, creator):
        """Test analyzing files with Create/Modify keywords."""
        work_unit = {
            "description": "Phase 3",
            "phase_content": "Create database.py and Modify api.py to integrate database.",
        }

        files = creator._analyze_file_dependencies(work_unit, None)

        assert "database.py" in files
        assert "api.py" in files

    def test_analyze_file_dependencies_fallback(self, creator):
        """Test fallback when no files found."""
        work_unit = {
            "description": "Phase for testing",
            "phase_content": "Implement some features without specifying files.",
        }

        files = creator._analyze_file_dependencies(work_unit, None)

        # Should generate placeholder
        assert len(files) == 1
        assert "test" in files[0].lower()


class TestValidateFileIndependence:
    """Test file conflict validation."""

    def test_validate_no_conflicts(self, creator):
        """Test validation with no conflicts."""
        work_units = [
            {"assigned_files": ["a.py", "b.py"], "description": "Work 1"},
            {"assigned_files": ["c.py", "d.py"], "description": "Work 2"},
            {"assigned_files": ["e.py"], "description": "Work 3"},
        ]

        # Should not raise
        creator._validate_file_independence(work_units)

    def test_validate_with_conflicts(self, creator):
        """Test validation with file conflicts."""
        work_units = [
            {"assigned_files": ["a.py", "b.py"], "description": "Work 1"},
            {"assigned_files": ["b.py", "c.py"], "description": "Work 2"},
        ]

        with pytest.raises(FileConflictError) as exc_info:
            creator._validate_file_independence(work_units)

        assert "b.py" in str(exc_info.value)
        assert "Work 1" in str(exc_info.value)
        assert "Work 2" in str(exc_info.value)


class TestInsertWork:
    """Test task insertion into database."""

    def test_insert_work_success(self, creator):
        """Test successful task insertion."""
        work_data = creator._insert_work(
            task_id="TASK-31-1",
            priority_number=31,
            task_group_id="GROUP-31",
            priority_order=1,
            spec_id="SPEC-131",
            scope_description="Phase 1: Implementation",
            assigned_files=["file1.py", "file2.py"],
        )

        assert work_data["task_id"] == "TASK-31-1"
        assert work_data["priority_number"] == 31
        assert work_data["task_group_id"] == "GROUP-31"
        assert work_data["priority_order"] == 1
        assert work_data["status"] == "pending"

        # Verify in database
        conn = sqlite3.connect(creator.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM specs_task WHERE task_id = ?", ("TASK-31-1",))
        result = cursor.fetchone()

        conn.close()

        assert result is not None


class TestCreateWorksForSpec:
    """Test complete task creation workflow."""

    def test_create_works_for_hierarchical_spec(self, creator, hierarchical_spec):
        """Test creating tasks from hierarchical spec."""
        tasks = creator.create_works_for_spec(hierarchical_spec, priority_number=100)

        # Should create 3 tasks (3 phases)
        assert len(tasks) == 3

        # Check task IDs
        assert tasks[0]["task_id"] == "TASK-100-1"
        assert tasks[1]["task_id"] == "TASK-100-2"
        assert tasks[2]["task_id"] == "TASK-100-3"

        # Check task_group_id (all same group)
        assert all(w["task_group_id"] == "GROUP-100" for w in tasks)

        # Check priority_order (sequential)
        assert tasks[0]["priority_order"] == 1
        assert tasks[1]["priority_order"] == 2
        assert tasks[2]["priority_order"] == 3

        # Check assigned_files
        assert len(tasks[0]["assigned_files"]) > 0
        assert len(tasks[1]["assigned_files"]) > 0

        # Verify in database
        conn = sqlite3.connect(creator.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM specs_task WHERE task_group_id = ?", ("GROUP-100",))
        count = cursor.fetchone()[0]

        conn.close()

        assert count == 3

    def test_create_works_validates_conflicts(self, creator, temp_db):
        """Test that task creation detects file conflicts."""
        # Create spec with conflicting files
        spec_id = "SPEC-102"
        spec_json = {
            "implementation": """
Phase 1: Part A
Create `conflict.py` file.

Phase 2: Part B
Modify `conflict.py` file.
        """
        }

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO specs_specification (id, content, spec_type, created_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                spec_id,
                json.dumps(spec_json),
                "hierarchical",
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # Should raise FileConflictError
        with pytest.raises(FileConflictError):
            creator.create_works_for_spec(spec_id, priority_number=102)


class TestAnalyzeParallelizationPotential:
    """Test parallelization analysis between specs."""

    def test_analyze_parallelization_no_conflicts(self, creator, temp_db):
        """Test analyzing two specs with no file conflicts."""
        # Create two specs with different files
        spec_1_json = {
            "implementation": """
Phase 1: Database
Create `coffee_maker/db.py` file.
        """
        }

        spec_2_json = {
            "implementation": """
Phase 1: API
Create `coffee_maker/api.py` file.
        """
        }

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        for spec_id, spec_json in [
            ("SPEC-201", spec_1_json),
            ("SPEC-202", spec_2_json),
        ]:
            cursor.execute(
                """
                INSERT INTO specs_specification (id, content, spec_type, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    spec_id,
                    json.dumps(spec_json),
                    "hierarchical",
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

        result = creator.analyze_parallelization_potential("SPEC-201", "SPEC-202")

        assert result["can_parallelize"] is True
        assert len(result["file_conflicts"]) == 0

    def test_analyze_parallelization_with_conflicts(self, creator, temp_db):
        """Test analyzing two specs with file conflicts."""
        # Create two specs with overlapping files
        spec_1_json = {
            "implementation": """
Phase 1: Part A
Create `coffee_maker/shared.py` file.
        """
        }

        spec_2_json = {
            "implementation": """
Phase 1: Part B
Modify `coffee_maker/shared.py` file.
        """
        }

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        for spec_id, spec_json in [
            ("SPEC-203", spec_1_json),
            ("SPEC-204", spec_2_json),
        ]:
            cursor.execute(
                """
                INSERT INTO specs_specification (id, content, spec_type, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    spec_id,
                    json.dumps(spec_json),
                    "hierarchical",
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

        result = creator.analyze_parallelization_potential("SPEC-203", "SPEC-204")

        assert result["can_parallelize"] is False
        assert "coffee_maker/shared.py" in result["file_conflicts"]
