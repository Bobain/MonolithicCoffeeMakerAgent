"""Test partial technical spec loading for implementation tasks.

This test verifies that code_developer only loads the necessary sections
of a technical spec based on the task's spec_sections field, ensuring
efficient context usage (CFR-007 compliance).

Author: code_developer
Date: 2025-10-24
Related: PRIORITY 32, SPEC-132, CFR-007
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from coffee_maker.autonomous.implementation_task_creator import (
    ImplementationTaskCreator,
)
from coffee_maker.autonomous.implementation_task_manager import (
    ImplementationTaskManager,
)


@pytest.fixture
def temp_db():
    """Create temporary database with specs_task and specs_specification tables."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create specs_task table
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

    # Create commits table
    cursor.execute(
        """
        CREATE TABLE commits (
            commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            commit_message TEXT,
            committed_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES specs_task(task_id)
        )
    """
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def large_hierarchical_spec(temp_db):
    """Insert a large hierarchical spec with multiple sections."""
    spec_id = "SPEC-200"
    spec_type = "hierarchical"

    # Simulate a large spec with multiple sections
    spec_json = {
        "overview": "This is the overview section. " * 100,  # ~500 tokens
        "architecture": "This is the architecture section. " * 100,  # ~500 tokens
        "implementation": "This is the implementation section. " * 200,  # ~1000 tokens
        "api_design": "This is the API design section. " * 150,  # ~750 tokens
        "testing": "This is the testing section. " * 100,  # ~500 tokens
        "deployment": "This is the deployment section. " * 100,  # ~500 tokens
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


class TestPartialSpecLoading:
    """Test that code_developer loads only necessary spec sections."""

    def test_load_only_implementation_section(self, temp_db, large_hierarchical_spec):
        """Test loading only the implementation section."""
        # Create a task with only implementation section
        ImplementationTaskCreator(temp_db)

        tasks = [
            {
                "description": "Phase 1: Core Implementation",
                "sections": ["/implementation"],
                "assigned_files": ["core.py"],
                "phase_content": "Implement core functionality",
            }
        ]

        # Manually insert task with specific spec_sections
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        task_id = "TASK-200-1"
        spec_sections_json = json.dumps(["implementation"])

        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                task_id,
                200,
                "GROUP-200",
                1,
                large_hierarchical_spec,
                "Phase 1: Core Implementation",
                json.dumps(["core.py"]),
                spec_sections_json,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # code_developer claims task and reads spec
        manager = ImplementationTaskManager(temp_db)
        success = manager.claim_work(task_id)
        assert success

        spec_content = manager.read_technical_spec_for_work()

        # Verify: Only implementation section loaded
        assert "## /implementation" in spec_content
        assert "This is the implementation section" in spec_content

        # Verify: Other sections NOT loaded
        assert "## /overview" not in spec_content
        assert "## /architecture" not in spec_content
        assert "## /api_design" not in spec_content
        assert "## /testing" not in spec_content
        assert "## /deployment" not in spec_content

        # Verify: Content is significantly smaller
        # Full spec would be ~3750 tokens, we should have ~1000
        assert len(spec_content) < 40000  # Much smaller than full spec

    def test_load_multiple_sections(self, temp_db, large_hierarchical_spec):
        """Test loading multiple specific sections."""
        # Create task with overview + implementation sections
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        task_id = "TASK-200-2"
        spec_sections_json = json.dumps(["overview", "implementation"])

        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                task_id,
                200,
                "GROUP-200",
                2,
                large_hierarchical_spec,
                "Phase 2: Setup + Implementation",
                json.dumps(["setup.py", "core.py"]),
                spec_sections_json,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # code_developer claims and reads
        manager = ImplementationTaskManager(temp_db)
        success = manager.claim_work(task_id)
        assert success

        spec_content = manager.read_technical_spec_for_work()

        # Verify: Both requested sections loaded
        assert "## /overview" in spec_content
        assert "## /implementation" in spec_content

        # Verify: Other sections NOT loaded
        assert "## /architecture" not in spec_content
        assert "## /api_design" not in spec_content
        assert "## /testing" not in spec_content

    def test_load_full_spec_when_no_sections_specified(self, temp_db, large_hierarchical_spec):
        """Test that full spec is loaded when spec_sections is NULL."""
        # Create task without spec_sections
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        task_id = "TASK-200-3"

        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 'pending', ?)
        """,
            (
                task_id,
                200,
                "GROUP-200",
                3,
                large_hierarchical_spec,
                "Phase 3: Full Implementation",
                json.dumps(["all.py"]),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # code_developer claims and reads
        manager = ImplementationTaskManager(temp_db)
        success = manager.claim_work(task_id)
        assert success

        spec_content = manager.read_technical_spec_for_work()

        # Verify: ALL sections loaded
        assert "## /overview" in spec_content
        assert "## /architecture" in spec_content
        assert "## /implementation" in spec_content
        assert "## /api_design" in spec_content
        assert "## /testing" in spec_content
        assert "## /deployment" in spec_content

    def test_different_tasks_load_different_sections(self, temp_db, large_hierarchical_spec):
        """Test that different tasks for same spec load different sections."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Task 1: Only overview
        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                "TASK-200-4",
                200,
                "GROUP-200",
                4,
                large_hierarchical_spec,
                "Phase 4: Planning",
                json.dumps(["plan.py"]),
                json.dumps(["overview"]),
                datetime.now().isoformat(),
            ),
        )

        # Task 2: Only testing
        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                "TASK-200-5",
                200,
                "GROUP-200",
                5,
                large_hierarchical_spec,
                "Phase 5: Testing",
                json.dumps(["test.py"]),
                json.dumps(["testing"]),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # Test Task 1: Should only have overview
        manager1 = ImplementationTaskManager(temp_db)
        manager1.claim_work("TASK-200-4")
        spec_content_1 = manager1.read_technical_spec_for_work()

        assert "## /overview" in spec_content_1
        assert "## /testing" not in spec_content_1
        assert "## /implementation" not in spec_content_1

        # Complete Task 1 before claiming Task 2 (sequential ordering)
        manager1.update_work_status("completed")

        # Test Task 2: Should only have testing
        manager2 = ImplementationTaskManager(temp_db)
        manager2.claim_work("TASK-200-5")
        spec_content_2 = manager2.read_technical_spec_for_work()

        assert "## /testing" in spec_content_2
        assert "## /overview" not in spec_content_2
        assert "## /implementation" not in spec_content_2

        # Verify they loaded different content
        assert spec_content_1 != spec_content_2


class TestScopeDescriptionUsage:
    """Test that scope_description provides human context."""

    def test_scope_description_provides_context(self, temp_db, large_hierarchical_spec):
        """Test that scope_description gives human-readable context."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        task_id = "TASK-200-6"
        scope_description = "Phase 1: Database Schema - Create User and Post tables"
        spec_sections_json = json.dumps(["implementation"])

        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                task_id,
                200,
                "GROUP-200",
                6,
                large_hierarchical_spec,
                scope_description,
                json.dumps(["models.py"]),
                spec_sections_json,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # code_developer claims task
        manager = ImplementationTaskManager(temp_db)
        success = manager.claim_work(task_id)
        assert success

        # Verify: code_developer can see what this task is about
        assert manager.current_work["scope_description"] == scope_description

        # Verify: This is separate from the spec sections loaded
        spec_content = manager.read_technical_spec_for_work()
        assert scope_description not in spec_content  # Not in spec itself
        assert "## /implementation" in spec_content  # But spec sections are loaded
