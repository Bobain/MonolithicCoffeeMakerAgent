"""Unit tests for agent lifecycle database tracing (CFR-014).

Tests the agent_lifecycle table, analytics views, and query functionality
required by US-110 and CFR-014.

Author: code_developer
Date: 2025-10-21
Related: US-110, CFR-014, SPEC-110
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.orchestrator.migrate_add_agent_lifecycle import AgentLifecycleMigration


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_orchestrator.db"

        # Initialize database with message queue schema first
        conn = sqlite3.connect(str(db_path))
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                type TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 5,
                status TEXT NOT NULL DEFAULT 'queued',
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                duration_ms INTEGER,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS orchestrator_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """
        )
        conn.commit()
        conn.close()

        yield db_path


@pytest.fixture
def migrated_db(temp_db):
    """Create migrated database with agent_lifecycle table."""
    migration = AgentLifecycleMigration(db_path=str(temp_db), json_path="nonexistent.json")
    migration.run(migrate_json=False)
    return temp_db


class TestAgentLifecycleSchema:
    """Test database schema creation and structure."""

    def test_migration_creates_agent_lifecycle_table(self, temp_db):
        """Test that migration creates agent_lifecycle table."""
        migration = AgentLifecycleMigration(db_path=str(temp_db), json_path="nonexistent.json")
        migration.run(migrate_json=False)

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_lifecycle'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "agent_lifecycle table should exist"

    def test_agent_lifecycle_has_required_columns(self, migrated_db):
        """Test that agent_lifecycle table has all required columns."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(agent_lifecycle)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        required_columns = {
            "agent_id",
            "pid",
            "agent_type",
            "task_id",
            "task_type",
            "priority_number",
            "spawned_at",
            "started_at",
            "completed_at",
            "status",
            "exit_code",
            "duration_ms",
            "idle_time_ms",
            "command",
            "worktree_path",
            "worktree_branch",
            "merged_at",
            "cleaned_at",
            "merge_duration_ms",
            "cleanup_duration_ms",
            "error_message",
            "metadata",
        }

        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_agent_lifecycle_has_indexes(self, migrated_db):
        """Test that required indexes are created."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='agent_lifecycle'")
        indexes = {row[0] for row in cursor.fetchall()}
        conn.close()

        required_indexes = {
            "idx_agent_type_status",
            "idx_priority_number",
            "idx_spawned_at",
            "idx_duration",
            "idx_task_id",
            "idx_pid",
            "idx_worktree_branch",
            "idx_merged_at",
        }

        assert required_indexes.issubset(indexes), f"Missing indexes: {required_indexes - indexes}"


class TestAnalyticsViews:
    """Test analytics views creation and functionality."""

    def test_active_agents_view_exists(self, migrated_db):
        """Test that active_agents view is created."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='active_agents'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "active_agents view should exist"

    def test_agent_velocity_view_exists(self, migrated_db):
        """Test that agent_velocity view is created."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='agent_velocity'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "agent_velocity view should exist"

    def test_agent_bottlenecks_view_exists(self, migrated_db):
        """Test that agent_bottlenecks view is created."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='agent_bottlenecks'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "agent_bottlenecks view should exist"

    def test_priority_timeline_view_exists(self, migrated_db):
        """Test that priority_timeline view is created."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='priority_timeline'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "priority_timeline view should exist"


class TestAgentLifecycleData:
    """Test agent lifecycle data insertion and querying."""

    def test_insert_agent_lifecycle_record(self, migrated_db):
        """Test inserting agent lifecycle record."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, spawned_at, status, command
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (12345, "architect", "spec-110", datetime.now().isoformat(), "spawned", "poetry run architect"),
        )
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM agent_lifecycle")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, "Should have 1 agent lifecycle record"

    def test_active_agents_view_filters_running_agents(self, migrated_db):
        """Test that active_agents view only shows spawned/running agents."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Insert running agent
        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, spawned_at, status, command
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (12345, "architect", "spec-110", datetime.now().isoformat(), "running", "poetry run architect"),
        )

        # Insert completed agent (should not appear)
        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, spawned_at, completed_at, status, command
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                12346,
                "code_developer",
                "impl-110",
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "completed",
                "poetry run code-developer",
            ),
        )

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM active_agents")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, "active_agents should only show running agents"

    def test_agent_velocity_calculates_avg_duration(self, migrated_db):
        """Test that agent_velocity view calculates average duration correctly."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Insert multiple completed agents with durations
        for i in range(3):
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, spawned_at, completed_at,
                    status, duration_ms, command
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    12340 + i,
                    "architect",
                    f"spec-{i}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    "completed",
                    (i + 1) * 60000,  # 1 min, 2 min, 3 min
                    "poetry run architect",
                ),
            )

        conn.commit()

        cursor.execute("SELECT avg_duration_ms FROM agent_velocity WHERE agent_type = 'architect'")
        avg_duration = cursor.fetchone()[0]
        conn.close()

        # Average of 1, 2, 3 minutes = 2 minutes = 120000 ms
        assert avg_duration == 120000, f"Expected avg_duration_ms=120000, got {avg_duration}"

    def test_agent_bottlenecks_identifies_long_duration(self, migrated_db):
        """Test that agent_bottlenecks view identifies long-running agents."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Insert long-running agent (>30 minutes)
        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, priority_number, spawned_at, completed_at,
                status, duration_ms, command
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                12345,
                "architect",
                "spec-110",
                110,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "completed",
                2000000,  # 33+ minutes
                "poetry run architect",
            ),
        )

        conn.commit()

        cursor.execute("SELECT bottleneck_type FROM agent_bottlenecks WHERE task_id = 'spec-110'")
        bottleneck_type = cursor.fetchone()[0]
        conn.close()

        assert bottleneck_type == "Long Duration", f"Expected 'Long Duration', got {bottleneck_type}"

    def test_agent_bottlenecks_identifies_high_idle_time(self, migrated_db):
        """Test that agent_bottlenecks view identifies high idle time."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Insert agent with high idle time (>50% of duration)
        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, priority_number, spawned_at, completed_at,
                status, duration_ms, idle_time_ms, command
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                12345,
                "architect",
                "spec-111",
                111,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "completed",
                100000,  # 100 seconds total
                60000,  # 60 seconds idle (60%)
                "poetry run architect",
            ),
        )

        conn.commit()

        cursor.execute("SELECT bottleneck_type FROM agent_bottlenecks WHERE task_id = 'spec-111'")
        bottleneck_type = cursor.fetchone()[0]
        conn.close()

        assert bottleneck_type == "High Idle Time", f"Expected 'High Idle Time', got {bottleneck_type}"

    def test_priority_timeline_aggregates_by_priority(self, migrated_db):
        """Test that priority_timeline view aggregates agents by priority."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Insert multiple agents for same priority
        for i in range(3):
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, priority_number, spawned_at, completed_at,
                    status, duration_ms, command
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    12340 + i,
                    "architect" if i == 0 else "code_developer",
                    f"task-{i}",
                    110,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    "completed",
                    60000,
                    "poetry run agent",
                ),
            )

        conn.commit()

        cursor.execute("SELECT agent_count, total_time_ms FROM priority_timeline WHERE priority_number = 110")
        rows = cursor.fetchall()
        conn.close()

        # Should have 2 rows (1 for architect, 2 for code_developer)
        total_agents = sum(row[0] for row in rows)
        assert total_agents == 3, f"Expected 3 total agents for priority 110, got {total_agents}"


class TestMigrationIdempotency:
    """Test that migration can be run multiple times safely."""

    def test_migration_is_idempotent(self, temp_db):
        """Test that running migration multiple times is safe."""
        migration = AgentLifecycleMigration(db_path=str(temp_db), json_path="nonexistent.json")

        # Run migration twice
        result1 = migration.run(migrate_json=False)
        result2 = migration.run(migrate_json=False)

        assert result1 is True, "First migration should succeed"
        assert result2 is True, "Second migration should also succeed (idempotent)"

        # Verify table still exists
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_lifecycle'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "Table should still exist after re-running migration"


class TestCFR014Compliance:
    """Test CFR-014 compliance requirements."""

    def test_all_agent_spawns_recorded_in_database(self, migrated_db):
        """Test that all agent spawns can be recorded in database (CFR-014)."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Simulate orchestrator spawning agents
        agents = [
            (12345, "architect", "spec-110"),
            (12346, "code_developer", "impl-110"),
            (12347, "project_manager", "plan-110"),
        ]

        for pid, agent_type, task_id in agents:
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, spawned_at, status, command
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (pid, agent_type, task_id, datetime.now().isoformat(), "spawned", f"poetry run {agent_type}"),
            )

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM agent_lifecycle")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 3, "All 3 agent spawns should be recorded in database"

    def test_duration_calculated_on_completion(self, migrated_db):
        """Test that duration is calculated when agent completes (CFR-014)."""
        conn = sqlite3.connect(str(migrated_db))
        cursor = conn.cursor()

        # Spawn agent
        spawned_at = datetime.now()
        cursor.execute(
            """
            INSERT INTO agent_lifecycle (
                pid, agent_type, task_id, spawned_at, status, command
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (12345, "architect", "spec-110", spawned_at.isoformat(), "running", "poetry run architect"),
        )

        conn.commit()

        # Complete agent (simulating orchestrator update)
        completed_at = spawned_at + timedelta(minutes=5)
        expected_duration_ms = int((completed_at - spawned_at).total_seconds() * 1000)

        cursor.execute(
            """
            UPDATE agent_lifecycle
            SET completed_at = ?,
                status = 'completed',
                duration_ms = CAST((julianday(?) - julianday(spawned_at)) * 86400000 AS INTEGER)
            WHERE pid = 12345
            """,
            (completed_at.isoformat(), completed_at.isoformat()),
        )

        conn.commit()

        cursor.execute("SELECT duration_ms FROM agent_lifecycle WHERE pid = 12345")
        duration_ms = cursor.fetchone()[0]
        conn.close()

        # Allow 1ms tolerance for rounding
        assert abs(duration_ms - expected_duration_ms) <= 1, f"Duration should be ~{expected_duration_ms}ms"
