"""Unit tests for ImplementationTaskManager (PRIORITY 31).

Tests cover:
- Work querying (respecting sequential ordering)
- Atomic claiming (race-safe)
- Sequential ordering enforcement
- File access validation
- Status updates
- Commit recording (for code_reviewer sync)
- Technical spec reading

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 31, CFR-000
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import os
import pytest

from coffee_maker.autonomous.implementation_task_manager import (
    ImplementationTaskManager,
    FileAccessViolationError,
    TaskNotFoundError,
)


@pytest.fixture
def temp_db():
    """Create temporary database with tasks and commits tables."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tasks table (NEW schema)
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

    # Create commits table (NEW)
    cursor.execute(
        """
        CREATE TABLE commits (
            commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            commit_message TEXT,
            committed_at TEXT NOT NULL,
            reviewed_by TEXT,
            review_status TEXT,
            review_notes TEXT,

            FOREIGN KEY (task_id) REFERENCES tasks(task_id)
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

    # Create specs_task_dependency table
    cursor.execute(
        """
        CREATE TABLE specs_task_dependency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_group_id TEXT NOT NULL,
            depends_on_group_id TEXT NOT NULL,
            dependency_type TEXT NOT NULL,
            reason TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL,

            UNIQUE(task_group_id, depends_on_group_id),
            CHECK(task_group_id != depends_on_group_id),
            CHECK(dependency_type IN ('hard', 'soft'))
        )
    """
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def manager(temp_db):
    """Create ImplementationTaskManager instance."""
    return ImplementationTaskManager(temp_db)


@pytest.fixture
def sample_work(temp_db):
    """Insert sample task into database."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    task_id = "TASK-31-1"
    priority_number = 31
    task_group_id = "GROUP-31"
    priority_order = 1
    spec_id = "SPEC-131"
    scope_description = "Phase 1: /implementation"
    assigned_files = json.dumps(["coffee_maker/autonomous/work_manager.py", "tests/unit/test_work_manager.py"])

    cursor.execute(
        """
        INSERT INTO specs_task
        (task_id, priority_number, task_group_id, priority_order,
         spec_id, scope_description, assigned_files, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """,
        (
            task_id,
            priority_number,
            task_group_id,
            priority_order,
            spec_id,
            scope_description,
            assigned_files,
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    return {
        "task_id": task_id,
        "priority_number": priority_number,
        "task_group_id": task_group_id,
        "priority_order": priority_order,
        "spec_id": spec_id,
        "assigned_files": json.loads(assigned_files),
    }


@pytest.fixture
def sample_spec(temp_db):
    """Insert sample technical spec into database."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    spec_id = "SPEC-131"
    spec_type = "hierarchical"

    # Hierarchical spec JSON
    spec_json = {
        "overview": "This is the overview section",
        "implementation": "This is the implementation section with detailed instructions",
        "test_strategy": "This is the test strategy section",
    }

    cursor.execute(
        """
        INSERT INTO specs_specification
        (id, content, spec_type, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (spec_id, json.dumps(spec_json), spec_type, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return spec_id


class TestWorkManagerInit:
    """Test ImplementationTaskManager initialization."""

    def test_init(self, temp_db):
        """Test basic initialization."""
        manager = ImplementationTaskManager(temp_db)

        assert manager.db_path == temp_db
        assert manager.current_work is None
        assert manager.assigned_files == []


class TestQueryNextWorkForPriority:
    """Test querying next task for priority (with sequential ordering)."""

    def test_query_next_work_single_work(self, manager, sample_work):
        """Test querying when one task exists."""
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is not None
        assert next_work["task_id"] == "TASK-31-1"
        assert next_work["priority_order"] == 1

    def test_query_next_work_respects_order(self, manager, temp_db):
        """Test that next task respects priority_order."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 3 tasks in GROUP-31
        for i in range(1, 4):
            cursor.execute(
                """
                INSERT INTO specs_task
                (task_id, priority_number, task_group_id, priority_order,
                 spec_id, scope_description, assigned_files, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"TASK-31-{i}",
                    31,
                    "GROUP-31",
                    i,
                    "SPEC-131",
                    f"Phase {i}",
                    json.dumps([f"file{i}.py"]),
                    "pending" if i == 1 else "pending",  # All pending
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

        # Should return TASK-31-1 (lowest priority_order)
        next_work = manager.query_next_work_for_priority(31)

        assert next_work["task_id"] == "TASK-31-1"
        assert next_work["priority_order"] == 1

    def test_query_next_work_waits_for_earlier_work(self, manager, temp_db):
        """Test that it waits for earlier task in sequence to complete."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 3 tasks: TASK-31-1 (in_progress), TASK-31-2 (pending), TASK-31-3 (pending)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-1",
                31,
                "GROUP-31",
                1,
                "SPEC-131",
                "Phase 1",
                json.dumps(["file1.py"]),
                "in_progress",  # Still in progress
                datetime.now().isoformat(),
            ),
        )

        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-2",
                31,
                "GROUP-31",
                2,
                "SPEC-131",
                "Phase 2",
                json.dumps(["file2.py"]),
                "pending",
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # Should return None (waiting for TASK-31-1 to complete)
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is None

    def test_query_next_work_after_completion(self, manager, temp_db):
        """Test that next task is available after earlier task completes."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 2 tasks: TASK-31-1 (completed), TASK-31-2 (pending)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-1",
                31,
                "GROUP-31",
                1,
                "SPEC-131",
                "Phase 1",
                json.dumps(["file1.py"]),
                "completed",
                datetime.now().isoformat(),
            ),
        )

        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-2",
                31,
                "GROUP-31",
                2,
                "SPEC-131",
                "Phase 2",
                json.dumps(["file2.py"]),
                "pending",
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # Should return TASK-31-2
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is not None
        assert next_work["task_id"] == "TASK-31-2"

    def test_query_no_works_for_priority(self, manager):
        """Test querying when no tasks exist for priority."""
        next_work = manager.query_next_work_for_priority(999)

        assert next_work is None


class TestClaimWork:
    """Test atomic task claiming."""

    def test_claim_success(self, manager, sample_work):
        """Test successful task claiming."""
        success = manager.claim_work("TASK-31-1")

        assert success is True
        assert manager.current_work is not None
        assert manager.current_work["task_id"] == "TASK-31-1"
        assert manager.current_work["status"] == "in_progress"
        assert manager.current_work["process_id"] == os.getpid()
        assert len(manager.assigned_files) == 2

    def test_claim_nonexistent_work(self, manager):
        """Test claiming task that doesn't exist."""
        with pytest.raises(TaskNotFoundError):
            manager.claim_work("TASK-999-1")

    def test_claim_already_claimed_work(self, manager, sample_work, temp_db):
        """Test claiming task already claimed by another instance."""
        # Manually claim the task
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE specs_task
            SET status = 'in_progress',
                process_id = 99999,
                claimed_at = ?
            WHERE task_id = 'TASK-31-1'
        """,
            (datetime.now().isoformat(),),
        )

        conn.commit()
        conn.close()

        # Try to claim
        success = manager.claim_work("TASK-31-1")

        assert success is False
        assert manager.current_work is None

    def test_claim_enforces_sequential_ordering(self, manager, temp_db):
        """Test that claiming enforces sequential ordering."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert TASK-31-1 (pending) and TASK-31-2 (pending)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-1",
                31,
                "GROUP-31",
                1,
                "SPEC-131",
                "Phase 1",
                json.dumps(["file1.py"]),
                "pending",
                datetime.now().isoformat(),
            ),
        )

        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TASK-31-2",
                31,
                "GROUP-31",
                2,
                "SPEC-131",
                "Phase 2",
                json.dumps(["file2.py"]),
                "pending",
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        # Try to claim TASK-31-2 (should fail because TASK-31-1 not completed)
        success = manager.claim_work("TASK-31-2")

        assert success is False
        assert manager.current_work is None

    def test_claim_race_condition(self, temp_db, sample_work):
        """Test that only one of two concurrent claims succeeds."""
        # Create two manager instances
        manager1 = ImplementationTaskManager(temp_db)
        manager2 = ImplementationTaskManager(temp_db)

        # Both try to claim simultaneously
        success1 = manager1.claim_work("TASK-31-1")
        success2 = manager2.claim_work("TASK-31-1")

        # Only one should succeed
        assert (success1 and not success2) or (not success1 and success2)


class TestValidateFileAccess:
    """Test file access validation."""

    def test_validate_file_in_assigned_files(self, manager, sample_work):
        """Test validating file that is in assigned_files."""
        manager.claim_work("TASK-31-1")

        # Should not raise
        result = manager.validate_file_access("coffee_maker/autonomous/work_manager.py")

        assert result is True

    def test_validate_file_not_in_assigned_files(self, manager, sample_work):
        """Test validating file that is NOT in assigned_files."""
        manager.claim_work("TASK-31-1")

        # Should raise FileAccessViolationError
        with pytest.raises(FileAccessViolationError) as exc_info:
            manager.validate_file_access("coffee_maker/autonomous/daemon.py")

        assert "daemon.py" in str(exc_info.value)
        assert "TASK-31-1" in str(exc_info.value)

    def test_validate_without_active_work(self, manager):
        """Test validating when no task is active (legacy mode)."""
        # Should allow all files when no task active
        result = manager.validate_file_access("any_file.py")

        assert result is True


class TestUpdateWorkStatus:
    """Test task status updates."""

    def test_update_to_in_progress(self, manager, sample_work):
        """Test updating status to in_progress."""
        manager.claim_work("TASK-31-1")

        manager.update_work_status("in_progress")

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, started_at FROM specs_task WHERE task_id = 'TASK-31-1'")
        status, started_at = cursor.fetchone()

        conn.close()

        assert status == "in_progress"
        assert started_at is not None

    def test_update_to_completed(self, manager, sample_work):
        """Test updating status to completed (no commit_sha in tasks table)."""
        manager.claim_work("TASK-31-1")

        manager.update_work_status("completed")

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, completed_at FROM specs_task WHERE task_id = 'TASK-31-1'")
        status, completed_at = cursor.fetchone()

        conn.close()

        assert status == "completed"
        assert completed_at is not None

    def test_update_to_failed_with_error_message(self, manager, sample_work):
        """Test updating status to failed with error message."""
        manager.claim_work("TASK-31-1")

        error_msg = "File access violation occurred"
        manager.update_work_status("failed", error_message=error_msg)

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, completed_at FROM specs_task WHERE task_id = 'TASK-31-1'")
        status, completed_at = cursor.fetchone()

        conn.close()

        assert status == "failed"
        assert completed_at is not None

    def test_update_without_active_work(self, manager):
        """Test updating when no task is active."""
        with pytest.raises(ValueError) as exc_info:
            manager.update_work_status("completed")

        assert "No active task" in str(exc_info.value)


class TestRecordCommit:
    """Test commit recording (NEW feature for code_reviewer sync)."""

    def test_record_commit_success(self, manager, sample_work):
        """Test recording a commit for current task."""
        manager.claim_work("TASK-31-1")

        commit_sha = "abc123def456"
        commit_message = "feat(TASK-31-1): Implement Phase 1"

        manager.record_commit(commit_sha, commit_message)

        # Verify in commits table
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT task_id, commit_sha, commit_message FROM commits WHERE task_id = 'TASK-31-1'")
        result = cursor.fetchone()

        conn.close()

        assert result is not None
        assert result[0] == "TASK-31-1"
        assert result[1] == commit_sha
        assert result[2] == commit_message

    def test_record_multiple_commits(self, manager, sample_work):
        """Test recording multiple commits for same task."""
        manager.claim_work("TASK-31-1")

        # Record 3 commits
        for i in range(1, 4):
            manager.record_commit(f"commit{i}", f"Commit message {i}")

        # Verify in commits table
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM commits WHERE task_id = 'TASK-31-1'")
        count = cursor.fetchone()[0]

        conn.close()

        assert count == 3

    def test_record_commit_without_active_work(self, manager):
        """Test recording commit when no task is active."""
        with pytest.raises(ValueError) as exc_info:
            manager.record_commit("abc123", "commit message")

        assert "No active task" in str(exc_info.value)


class TestReadTechnicalSpecForWork:
    """Test reading technical spec sections."""

    def test_read_specific_section(self, manager, sample_work, sample_spec):
        """Test reading specific section from hierarchical spec."""
        manager.claim_work("TASK-31-1")

        spec_content = manager.read_technical_spec_for_work()

        # Should contain implementation section
        assert "implementation" in spec_content.lower()
        assert "detailed instructions" in spec_content

    def test_read_full_spec_when_no_sections_specified(self, manager, temp_db, sample_spec):
        """Test reading full spec when scope_description has no section paths."""
        # Create task without section paths
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                "TASK-31-100",
                31,
                "GROUP-31",
                100,
                "SPEC-131",
                "Complete implementation",
                json.dumps(["file.py"]),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        manager.claim_work("TASK-31-100")

        spec_content = manager.read_technical_spec_for_work()

        # Should contain all sections
        assert "overview" in spec_content.lower()
        assert "implementation" in spec_content.lower()
        assert "test_strategy" in spec_content.lower()


class TestWorkManagerIntegration:
    """Integration tests for complete workflow."""

    def test_complete_workflow_with_commits(self, manager, sample_work, sample_spec):
        """Test complete task workflow from claim to completion with commits."""
        # 1. Claim task
        success = manager.claim_work("TASK-31-1")
        assert success is True

        # 2. Read spec
        spec_content = manager.read_technical_spec_for_work()
        assert len(spec_content) > 0

        # 3. Validate file access (allowed)
        manager.validate_file_access("coffee_maker/autonomous/work_manager.py")

        # 4. Record first commit
        manager.record_commit("commit1", "Initial implementation")

        # 5. Record second commit
        manager.record_commit("commit2", "Add tests")

        # 6. Update status to completed
        manager.update_work_status("completed")

        # 7. Verify final state
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        # Check task status
        cursor.execute("SELECT status FROM specs_task WHERE task_id = 'TASK-31-1'")
        status = cursor.fetchone()[0]

        # Check commits count
        cursor.execute("SELECT COUNT(*) FROM commits WHERE task_id = 'TASK-31-1'")
        commit_count = cursor.fetchone()[0]

        conn.close()

        assert status == "completed"
        assert commit_count == 2


class TestTaskGroupDependencies:
    """Test task group dependency enforcement (PRIORITY 32)."""

    @pytest.fixture
    def db_with_dependencies(self, temp_db):
        """Create database with task groups and dependencies."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create specs_task_dependency table (if not exists - may be created by temp_db fixture)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS specs_task_dependency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_group_id TEXT NOT NULL,
                depends_on_group_id TEXT NOT NULL,
                dependency_type TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,

                UNIQUE(task_group_id, depends_on_group_id),
                CHECK(task_group_id != depends_on_group_id),
                CHECK(dependency_type IN ('hard', 'soft'))
            )
        """
        )

        # Create task groups:
        # GROUP-36: Shared JSON serialization library (no dependencies)
        # GROUP-20: Import CSV (depends on GROUP-36)
        # GROUP-35: Export JSON (depends on GROUP-36)

        # Insert tasks for GROUP-36 (prerequisite)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES ('TASK-36-1', 32, 'GROUP-36', 1, 'SPEC-136',
                    'Implement JSON serialization library',
                    '["coffee_maker/utils/json_serializer.py"]',
                    'pending', ?)
        """,
            (datetime.now().isoformat(),),
        )

        # Insert tasks for GROUP-20 (depends on GROUP-36)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES ('TASK-20-1', 32, 'GROUP-20', 2, 'SPEC-120',
                    'Import CSV using JSON library',
                    '["coffee_maker/importers/csv_importer.py"]',
                    'pending', ?)
        """,
            (datetime.now().isoformat(),),
        )

        # Insert tasks for GROUP-35 (depends on GROUP-36)
        cursor.execute(
            """
            INSERT INTO specs_task
            (task_id, priority_number, task_group_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES ('TASK-35-1', 32, 'GROUP-35', 3, 'SPEC-135',
                    'Export data to JSON using JSON library',
                    '["coffee_maker/exporters/json_exporter.py"]',
                    'pending', ?)
        """,
            (datetime.now().isoformat(),),
        )

        # Add dependencies: GROUP-20 and GROUP-35 depend on GROUP-36
        cursor.execute(
            """
            INSERT INTO specs_task_dependency
            (task_group_id, depends_on_group_id, dependency_type, reason, created_at, created_by)
            VALUES ('GROUP-20', 'GROUP-36', 'hard',
                    'Requires JSON serialization library from SPEC-136', ?, 'architect')
        """,
            (datetime.now().isoformat(),),
        )

        cursor.execute(
            """
            INSERT INTO specs_task_dependency
            (task_group_id, depends_on_group_id, dependency_type, reason, created_at, created_by)
            VALUES ('GROUP-35', 'GROUP-36', 'hard',
                    'Requires JSON serialization library from SPEC-136', ?, 'architect')
        """,
            (datetime.now().isoformat(),),
        )

        conn.commit()
        conn.close()

        return temp_db

    def test_query_blocks_dependent_groups_when_prerequisite_pending(self, db_with_dependencies):
        """Test that query_next_work_for_priority blocks GROUP-20 and GROUP-35 when GROUP-36 is pending."""
        manager = ImplementationTaskManager(db_with_dependencies)

        # Query for priority 32
        next_task = manager.query_next_work_for_priority(32)

        # Should return GROUP-36 task (no dependencies)
        assert next_task is not None
        assert next_task["task_group_id"] == "GROUP-36"
        assert next_task["task_id"] == "TASK-36-1"

    def test_query_unblocks_dependent_groups_after_prerequisite_completed(self, db_with_dependencies):
        """Test that GROUP-20 and GROUP-35 are available after GROUP-36 completes."""
        manager = ImplementationTaskManager(db_with_dependencies)

        # Mark GROUP-36 as completed
        conn = sqlite3.connect(db_with_dependencies)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE specs_task
            SET status = 'completed', completed_at = ?
            WHERE task_id = 'TASK-36-1'
        """,
            (datetime.now().isoformat(),),
        )
        conn.commit()
        conn.close()

        # Now query for next task
        next_task = manager.query_next_work_for_priority(32)

        # Should return either GROUP-20 or GROUP-35 (both unblocked)
        assert next_task is not None
        assert next_task["task_group_id"] in ["GROUP-20", "GROUP-35"]

    def test_query_available_works_respects_dependencies(self, db_with_dependencies):
        """Test that query_available_works filters out blocked groups."""
        manager = ImplementationTaskManager(db_with_dependencies)

        # Query all available works
        available_works = manager.query_available_works()

        # Should only return GROUP-36 (GROUP-20 and GROUP-35 are blocked)
        assert len(available_works) == 1
        assert available_works[0]["task_group_id"] == "GROUP-36"

    def test_query_available_works_for_specific_blocked_group(self, db_with_dependencies):
        """Test querying specific blocked group returns empty."""
        manager = ImplementationTaskManager(db_with_dependencies)

        # Query GROUP-20 specifically (should be blocked)
        available_works = manager.query_available_works(task_group_id="GROUP-20")

        # Should return empty (GROUP-20 depends on incomplete GROUP-36)
        assert len(available_works) == 0

    def test_parallel_execution_after_prerequisite_complete(self, db_with_dependencies):
        """Test that GROUP-20 and GROUP-35 can run in parallel after GROUP-36 completes."""
        # Mark GROUP-36 as completed
        conn = sqlite3.connect(db_with_dependencies)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE specs_task
            SET status = 'completed', completed_at = ?
            WHERE task_id = 'TASK-36-1'
        """,
            (datetime.now().isoformat(),),
        )
        conn.commit()
        conn.close()

        manager = ImplementationTaskManager(db_with_dependencies)

        # Query all available works
        available_works = manager.query_available_works()

        # Should return both GROUP-20 and GROUP-35 (can run in parallel)
        assert len(available_works) == 2
        task_groups = {work["task_group_id"] for work in available_works}
        assert task_groups == {"GROUP-20", "GROUP-35"}
