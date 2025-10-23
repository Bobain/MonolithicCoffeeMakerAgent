"""Unit tests for WorkManager (PRIORITY 31).

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

import pytest

from coffee_maker.autonomous.work_manager import (
    WorkManager,
    FileAccessViolationError,
    WorkNotFoundError,
)


@pytest.fixture
def temp_db():
    """Create temporary database with works and commits tables."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create works table (NEW schema)
    cursor.execute(
        """
        CREATE TABLE works (
            work_id TEXT PRIMARY KEY,
            priority_number INTEGER NOT NULL,
            related_works_id TEXT NOT NULL,
            priority_order INTEGER NOT NULL,
            spec_id TEXT NOT NULL,
            scope_description TEXT NOT NULL,
            assigned_files TEXT NOT NULL,
            status TEXT NOT NULL,
            claimed_by TEXT,
            claimed_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL,

            UNIQUE(related_works_id, priority_order)
        )
    """
    )

    # Create commits table (NEW)
    cursor.execute(
        """
        CREATE TABLE commits (
            commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            commit_message TEXT,
            committed_at TEXT NOT NULL,
            reviewed_by TEXT,
            review_status TEXT,
            review_notes TEXT,

            FOREIGN KEY (work_id) REFERENCES works(work_id)
        )
    """
    )

    # Create technical_specs table
    cursor.execute(
        """
        CREATE TABLE technical_specs (
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
def manager(temp_db):
    """Create WorkManager instance."""
    return WorkManager(temp_db)


@pytest.fixture
def sample_work(temp_db):
    """Insert sample work into database."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    work_id = "WORK-31-1"
    priority_number = 31
    related_works_id = "GROUP-31"
    priority_order = 1
    spec_id = "SPEC-131"
    scope_description = "Phase 1: /implementation"
    assigned_files = json.dumps(["coffee_maker/autonomous/work_manager.py", "tests/unit/test_work_manager.py"])

    cursor.execute(
        """
        INSERT INTO works
        (work_id, priority_number, related_works_id, priority_order,
         spec_id, scope_description, assigned_files, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """,
        (
            work_id,
            priority_number,
            related_works_id,
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
        "work_id": work_id,
        "priority_number": priority_number,
        "related_works_id": related_works_id,
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
        INSERT INTO technical_specs
        (id, content, spec_type, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (spec_id, json.dumps(spec_json), spec_type, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return spec_id


class TestWorkManagerInit:
    """Test WorkManager initialization."""

    def test_init(self, temp_db):
        """Test basic initialization."""
        manager = WorkManager(temp_db)

        assert manager.db_path == temp_db
        assert manager.current_work is None
        assert manager.assigned_files == []


class TestQueryNextWorkForPriority:
    """Test querying next work for priority (with sequential ordering)."""

    def test_query_next_work_single_work(self, manager, sample_work):
        """Test querying when one work exists."""
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is not None
        assert next_work["work_id"] == "WORK-31-1"
        assert next_work["priority_order"] == 1

    def test_query_next_work_respects_order(self, manager, temp_db):
        """Test that next work respects priority_order."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 3 works in GROUP-31
        for i in range(1, 4):
            cursor.execute(
                """
                INSERT INTO works
                (work_id, priority_number, related_works_id, priority_order,
                 spec_id, scope_description, assigned_files, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"WORK-31-{i}",
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

        # Should return WORK-31-1 (lowest priority_order)
        next_work = manager.query_next_work_for_priority(31)

        assert next_work["work_id"] == "WORK-31-1"
        assert next_work["priority_order"] == 1

    def test_query_next_work_waits_for_earlier_work(self, manager, temp_db):
        """Test that it waits for earlier work in sequence to complete."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 3 works: WORK-31-1 (in_progress), WORK-31-2 (pending), WORK-31-3 (pending)
        cursor.execute(
            """
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-1",
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
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-2",
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

        # Should return None (waiting for WORK-31-1 to complete)
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is None

    def test_query_next_work_after_completion(self, manager, temp_db):
        """Test that next work is available after earlier work completes."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert 2 works: WORK-31-1 (completed), WORK-31-2 (pending)
        cursor.execute(
            """
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-1",
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
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-2",
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

        # Should return WORK-31-2
        next_work = manager.query_next_work_for_priority(31)

        assert next_work is not None
        assert next_work["work_id"] == "WORK-31-2"

    def test_query_no_works_for_priority(self, manager):
        """Test querying when no works exist for priority."""
        next_work = manager.query_next_work_for_priority(999)

        assert next_work is None


class TestClaimWork:
    """Test atomic work claiming."""

    def test_claim_success(self, manager, sample_work):
        """Test successful work claiming."""
        success = manager.claim_work("WORK-31-1")

        assert success is True
        assert manager.current_work is not None
        assert manager.current_work["work_id"] == "WORK-31-1"
        assert manager.current_work["status"] == "in_progress"
        assert manager.current_work["claimed_by"] == "code_developer"
        assert len(manager.assigned_files) == 2

    def test_claim_nonexistent_work(self, manager):
        """Test claiming work that doesn't exist."""
        with pytest.raises(WorkNotFoundError):
            manager.claim_work("WORK-999-1")

    def test_claim_already_claimed_work(self, manager, sample_work, temp_db):
        """Test claiming work already claimed by another instance."""
        # Manually claim the work
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE works
            SET status = 'in_progress',
                claimed_by = 'another_instance',
                claimed_at = ?
            WHERE work_id = 'WORK-31-1'
        """,
            (datetime.now().isoformat(),),
        )

        conn.commit()
        conn.close()

        # Try to claim
        success = manager.claim_work("WORK-31-1")

        assert success is False
        assert manager.current_work is None

    def test_claim_enforces_sequential_ordering(self, manager, temp_db):
        """Test that claiming enforces sequential ordering."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Insert WORK-31-1 (pending) and WORK-31-2 (pending)
        cursor.execute(
            """
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-1",
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
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "WORK-31-2",
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

        # Try to claim WORK-31-2 (should fail because WORK-31-1 not completed)
        success = manager.claim_work("WORK-31-2")

        assert success is False
        assert manager.current_work is None

    def test_claim_race_condition(self, temp_db, sample_work):
        """Test that only one of two concurrent claims succeeds."""
        # Create two manager instances
        manager1 = WorkManager(temp_db)
        manager2 = WorkManager(temp_db)

        # Both try to claim simultaneously
        success1 = manager1.claim_work("WORK-31-1")
        success2 = manager2.claim_work("WORK-31-1")

        # Only one should succeed
        assert (success1 and not success2) or (not success1 and success2)


class TestValidateFileAccess:
    """Test file access validation."""

    def test_validate_file_in_assigned_files(self, manager, sample_work):
        """Test validating file that is in assigned_files."""
        manager.claim_work("WORK-31-1")

        # Should not raise
        result = manager.validate_file_access("coffee_maker/autonomous/work_manager.py")

        assert result is True

    def test_validate_file_not_in_assigned_files(self, manager, sample_work):
        """Test validating file that is NOT in assigned_files."""
        manager.claim_work("WORK-31-1")

        # Should raise FileAccessViolationError
        with pytest.raises(FileAccessViolationError) as exc_info:
            manager.validate_file_access("coffee_maker/autonomous/daemon.py")

        assert "daemon.py" in str(exc_info.value)
        assert "WORK-31-1" in str(exc_info.value)

    def test_validate_without_active_work(self, manager):
        """Test validating when no work is active (legacy mode)."""
        # Should allow all files when no work active
        result = manager.validate_file_access("any_file.py")

        assert result is True


class TestUpdateWorkStatus:
    """Test work status updates."""

    def test_update_to_in_progress(self, manager, sample_work):
        """Test updating status to in_progress."""
        manager.claim_work("WORK-31-1")

        manager.update_work_status("in_progress")

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, started_at FROM works WHERE work_id = 'WORK-31-1'")
        status, started_at = cursor.fetchone()

        conn.close()

        assert status == "in_progress"
        assert started_at is not None

    def test_update_to_completed(self, manager, sample_work):
        """Test updating status to completed (no commit_sha in works table)."""
        manager.claim_work("WORK-31-1")

        manager.update_work_status("completed")

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, completed_at FROM works WHERE work_id = 'WORK-31-1'")
        status, completed_at = cursor.fetchone()

        conn.close()

        assert status == "completed"
        assert completed_at is not None

    def test_update_to_failed_with_error_message(self, manager, sample_work):
        """Test updating status to failed with error message."""
        manager.claim_work("WORK-31-1")

        error_msg = "File access violation occurred"
        manager.update_work_status("failed", error_message=error_msg)

        # Verify in database
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, completed_at FROM works WHERE work_id = 'WORK-31-1'")
        status, completed_at = cursor.fetchone()

        conn.close()

        assert status == "failed"
        assert completed_at is not None

    def test_update_without_active_work(self, manager):
        """Test updating when no work is active."""
        with pytest.raises(ValueError) as exc_info:
            manager.update_work_status("completed")

        assert "No active work" in str(exc_info.value)


class TestRecordCommit:
    """Test commit recording (NEW feature for code_reviewer sync)."""

    def test_record_commit_success(self, manager, sample_work):
        """Test recording a commit for current work."""
        manager.claim_work("WORK-31-1")

        commit_sha = "abc123def456"
        commit_message = "feat(WORK-31-1): Implement Phase 1"

        manager.record_commit(commit_sha, commit_message)

        # Verify in commits table
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT work_id, commit_sha, commit_message FROM commits WHERE work_id = 'WORK-31-1'")
        result = cursor.fetchone()

        conn.close()

        assert result is not None
        assert result[0] == "WORK-31-1"
        assert result[1] == commit_sha
        assert result[2] == commit_message

    def test_record_multiple_commits(self, manager, sample_work):
        """Test recording multiple commits for same work."""
        manager.claim_work("WORK-31-1")

        # Record 3 commits
        for i in range(1, 4):
            manager.record_commit(f"commit{i}", f"Commit message {i}")

        # Verify in commits table
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM commits WHERE work_id = 'WORK-31-1'")
        count = cursor.fetchone()[0]

        conn.close()

        assert count == 3

    def test_record_commit_without_active_work(self, manager):
        """Test recording commit when no work is active."""
        with pytest.raises(ValueError) as exc_info:
            manager.record_commit("abc123", "commit message")

        assert "No active work" in str(exc_info.value)


class TestReadTechnicalSpecForWork:
    """Test reading technical spec sections."""

    def test_read_specific_section(self, manager, sample_work, sample_spec):
        """Test reading specific section from hierarchical spec."""
        manager.claim_work("WORK-31-1")

        spec_content = manager.read_technical_spec_for_work()

        # Should contain implementation section
        assert "implementation" in spec_content.lower()
        assert "detailed instructions" in spec_content

    def test_read_full_spec_when_no_sections_specified(self, manager, temp_db, sample_spec):
        """Test reading full spec when scope_description has no section paths."""
        # Create work without section paths
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO works
            (work_id, priority_number, related_works_id, priority_order,
             spec_id, scope_description, assigned_files, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                "WORK-31-100",
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

        manager.claim_work("WORK-31-100")

        spec_content = manager.read_technical_spec_for_work()

        # Should contain all sections
        assert "overview" in spec_content.lower()
        assert "implementation" in spec_content.lower()
        assert "test_strategy" in spec_content.lower()


class TestWorkManagerIntegration:
    """Integration tests for complete workflow."""

    def test_complete_workflow_with_commits(self, manager, sample_work, sample_spec):
        """Test complete work workflow from claim to completion with commits."""
        # 1. Claim work
        success = manager.claim_work("WORK-31-1")
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

        # Check work status
        cursor.execute("SELECT status FROM works WHERE work_id = 'WORK-31-1'")
        status = cursor.fetchone()[0]

        # Check commits count
        cursor.execute("SELECT COUNT(*) FROM commits WHERE work_id = 'WORK-31-1'")
        commit_count = cursor.fetchone()[0]

        conn.close()

        assert status == "completed"
        assert commit_count == 2
